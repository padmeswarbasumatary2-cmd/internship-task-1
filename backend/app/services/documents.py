from __future__ import annotations

import io
import re
import unicodedata
from typing import Any

MAX_DOCUMENT_BYTES = 10 * 1024 * 1024
SUPPORTED_EXTENSIONS = {".txt", ".pdf", ".docx", ".png", ".jpg", ".jpeg"}


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\u00a0", " ").replace("\u2019", "'").replace("\u2013", "-").replace("\u2014", "-")
    text = re.sub(r"[\t\r\f\v]+", " ", text)
    text = re.sub(r"[ ]{2,}", " ", text)
    text = re.sub(r"\n[ \t]+", "\n", text)
    return text.strip()


def extract_document_text(filename: str, content: bytes) -> str:
    if not content:
        raise ValueError("The uploaded document is empty.")
    if len(content) > MAX_DOCUMENT_BYTES:
        raise ValueError("Resume files must be 10 MB or smaller.")

    extension = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError("Supported resume formats are PDF, DOCX, TXT, PNG, and JPG.")

    try:
        if extension == ".txt":
            text = content.decode("utf-8-sig")
        elif extension == ".pdf":
            from pypdf import PdfReader

            pages = PdfReader(io.BytesIO(content)).pages
            if len(pages) > 100:
                raise ValueError("PDF uploads are limited to 100 pages.")
            text = "\n".join(page.extract_text() or "" for page in pages)
            if not text.strip():
                import fitz
                from PIL import Image
                import pytesseract

                pdf = fitz.open(stream=content, filetype="pdf")
                if len(pdf) > 30:
                    raise ValueError("OCR is limited to the first 30 pages of a PDF.")
                text = "\n".join(
                    pytesseract.image_to_string(
                        Image.open(io.BytesIO(page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5)).tobytes("png")))
                    )
                    for page in pdf
                )
                if not text.strip():
                    raise ValueError("OCR could not recognize text in this scanned PDF.")
        elif extension == ".docx":
            from docx import Document

            document = Document(io.BytesIO(content))
            chunks = [paragraph.text for paragraph in document.paragraphs]
            chunks.extend("\t".join(cell.text for cell in row.cells) for table in document.tables for row in table.rows)
            text = "\n".join(chunks)
        else:
            from PIL import Image
            import pytesseract

            image = Image.open(io.BytesIO(content))
            if image.width * image.height > 25_000_000:
                raise ValueError("Image dimensions exceed the 25-megapixel processing limit.")
            text = pytesseract.image_to_string(image)
            if not text.strip():
                raise ValueError("OCR could not recognize text in this image.")
    except ValueError:
        raise
    except Exception as error:
        if extension in {".png", ".jpg", ".jpeg"} and "tesseract" in str(error).lower():
            raise ValueError("OCR requires the Tesseract executable. Install it and add it to PATH.") from error
        raise ValueError(f"Could not read this {extension[1:].upper()} document.") from error

    cleaned = normalize_text(text)
    if len(cleaned) < 20:
        raise ValueError("Not enough readable text was extracted from this document.")
    return cleaned


def extract_profile(text: str) -> dict[str, Any]:
    email = _first_match(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", text, re.IGNORECASE)
    phone = _first_match(r"(?<!\w)(?:\+?\d[\d ().-]{7,}\d)(?!\w)", text)
    linkedin = _first_match(r"(?:https?://)?(?:www\.)?linkedin\.com/in/[\w-]+", text, re.IGNORECASE)
    github = _first_match(r"(?:https?://)?(?:www\.)?github\.com/[\w-]+", text, re.IGNORECASE)

    lines = [line.strip(" \t-|•") for line in text.splitlines() if line.strip()]
    name = None
    for line in lines[:8]:
        if len(line) <= 70 and not re.search(r"@|https?://|\d{3,}|resume|curriculum vitae", line, re.IGNORECASE):
            words = re.findall(r"[A-Za-z][A-Za-z'-]*", line)
            if 2 <= len(words) <= 4 and all(word[:1].isupper() for word in words):
                name = line
                break

    section_headers = {
        "education": re.compile(r"^(education|academic background|academic history)$", re.IGNORECASE),
        "experience": re.compile(r"^(professional experience|work experience|employment history|experience|employment|work history|career history)$", re.IGNORECASE),
    }
    sections: dict[str, list[str]] = {"education": [], "experience": []}
    active_section: str | None = None
    for line in lines:
        matched_section = next((key for key, pattern in section_headers.items() if pattern.fullmatch(line.rstrip(":"))), None)
        if matched_section:
            active_section = matched_section
            continue
        if re.fullmatch(r"(?:skills|projects|certifications|summary|objective|contact|references)\s*:?[ ]*", line, re.IGNORECASE):
            active_section = None
        elif active_section and len(sections[active_section]) < 12:
            sections[active_section].append(line[:240])
    education = sections["education"]
    experience = sections["experience"]
    years = [int(value) for value in re.findall(r"\b(?:19|20)\d{2}\b", text)]
    degree = _first_match(
        r"\b(?:Ph\.?D\.?|doctorate|master(?:'s)?|M\.?S\.?|M\.?A\.?|bachelor(?:'s)?|B\.?S\.?|B\.?A\.?|associate(?:'s)?)\b",
        text,
        re.IGNORECASE,
    )
    gpa = _first_match(r"\bGPA\s*[:=]?\s*\d(?:\.\d{1,2})?(?:\s*/\s*\d(?:\.\d{1,2})?)?", text, re.IGNORECASE)
    achievement_metrics = list(dict.fromkeys(re.findall(r"(?:\$\s?\d[\d,.]*\s?[kKmMbB]?|\b\d+(?:\.\d+)?%|\b\d+\+?\s*(?:users|customers|clients|projects|people|employees)\b)", text, re.IGNORECASE)))[:12]
    skills: list[str] = []
    return {
        "name": name,
        "contact": {"email": email, "phone": phone, "linkedin": linkedin, "github": github},
        "education": education,
        "experienceHighlights": experience,
        "graduationYears": years[-4:],
        "degree": degree,
        "gpa": gpa,
        "achievementMetrics": achievement_metrics,
        "skills": skills,
    }


def _first_match(pattern: str, text: str, flags: int = 0) -> str | None:
    match = re.search(pattern, text, flags)
    return match.group(0) if match else None
