import pytest

from app.services.documents import extract_document_text, extract_profile, normalize_text


def test_text_extraction_normalizes_unicode_and_whitespace():
    text = extract_document_text("resume.txt", b"Jane Doe\r\nPython\u00a0Developer\u2014Data Team")
    assert text == "Jane Doe\nPython Developer-Data Team"


def test_unsupported_document_type_returns_validation_error():
    with pytest.raises(ValueError, match="Supported resume formats"):
        extract_document_text("resume.rtf", b"some resume text that is long enough")


def test_profile_extracts_skill_and_sections_without_requiring_model_downloads():
    profile = extract_profile(
        "Jane Doe\ncontact jane@example.com\n"
        "Experience\nSoftware Engineer, Acme\nBuilt APIs with Python\n"
        "Education\nB.S. Computer Science, Example University 2022\n"
        "Skills\nSQL"
    )
    assert profile["name"] == "Jane Doe"
    assert profile["contact"]["email"] == "jane@example.com"
    assert "Software Engineer, Acme" in profile["experienceHighlights"]
    assert any("Computer Science" in line for line in profile["education"])


def test_normalize_text_replaces_typographic_dash():
    assert normalize_text("A\u2014B") == "A-B"
