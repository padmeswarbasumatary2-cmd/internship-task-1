from __future__ import annotations

import re
from collections.abc import Iterable

SKILL_ALIASES: dict[str, tuple[str, ...]] = {
    "python": ("python", "py"),
    "javascript": ("javascript", "js", "ecmascript"),
    "typescript": ("typescript", "ts"),
    "react": ("react", "react.js", "reactjs"),
    "node.js": ("node.js", "nodejs", "node"),
    "sql": ("sql", "postgresql", "postgres", "mysql", "sqlite"),
    "excel": ("excel", "microsoft excel", "spreadsheets"),
    "power bi": ("power bi", "powerbi"),
    "tableau": ("tableau",),
    "data analysis": ("data analysis", "data analytics", "analytics"),
    "data cleaning": ("data cleaning", "data cleansing", "data wrangling"),
    "machine learning": ("machine learning", "ml", "scikit-learn", "sklearn"),
    "deep learning": ("deep learning", "pytorch", "tensorflow", "keras"),
    "natural language processing": ("natural language processing", "nlp", "spacy", "transformers"),
    "apis": ("api", "apis", "rest api", "restful"),
    "fastapi": ("fastapi",),
    "flask": ("flask",),
    "django": ("django",),
    "aws": ("aws", "amazon web services"),
    "azure": ("azure", "microsoft azure"),
    "gcp": ("gcp", "google cloud platform"),
    "docker": ("docker", "containerization"),
    "kubernetes": ("kubernetes", "k8s"),
    "git": ("git", "github", "gitlab"),
    "communication": ("communication", "communicated", "presented"),
    "leadership": ("leadership", "led", "mentored", "managed"),
    "project management": ("project management", "project manager", "agile", "scrum"),
    "statistics": ("statistics", "statistical analysis", "statistical modeling"),
    "dashboards": ("dashboard", "dashboards", "visualization", "data visualization"),
    "etl": ("etl", "data pipeline", "data pipelines", "extract transform load"),
}


def _contains_term(text: str, term: str) -> bool:
    normalized = term.casefold().strip()
    if not normalized:
        return False
    return re.search(r"(?<![a-z0-9+#])" + re.escape(normalized) + r"(?![a-z0-9+#])", text) is not None


def extract_skills(text: str, vocabulary: Iterable[str] | None = None) -> set[str]:
    normalized_text = re.sub(r"\s+", " ", text.casefold())
    found: set[str] = set()
    for canonical, aliases in SKILL_ALIASES.items():
        if any(_contains_term(normalized_text, alias) for alias in aliases):
            found.add(canonical)

    if any(_contains_term(normalized_text, term) for term in ("pandas", "numpy", "scikit-learn", "sklearn")):
        found.add("python")

    if vocabulary:
        for item in vocabulary:
            canonical = item.casefold().strip()
            if canonical and any(_contains_term(normalized_text, alias) for alias in (canonical, *SKILL_ALIASES.get(canonical, ()))):
                found.add(canonical)
    return found


def _experience_score(resume_text: str, job_description: str) -> int:
    requested = re.search(r"(\d+)\s*\+?\s*(?:years?|yrs?)\s+(?:of\s+)?experience", job_description, re.IGNORECASE)
    if not requested:
        return 100
    target_years = max(1, int(requested.group(1)))
    durations = [float(value) for value in re.findall(r"\b(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)", resume_text, re.IGNORECASE)]
    dates = [int(year) for year in re.findall(r"\b(?:19|20)\d{2}\b", resume_text)]
    inferred_years = max(durations, default=0.0)
    if len(dates) >= 2:
        inferred_years = max(inferred_years, min(50, max(dates) - min(dates)))
    return round(min(100, inferred_years / target_years * 100))


def _education_score(resume_text: str, job_description: str) -> int:
    requirements = {
        "phd": (r"\b(?:ph\.?d|doctorate)\b", r"\b(?:ph\.?d|doctorate)\b"),
        "master": (r"\b(?:master'?s|m\.?s\.?|m\.?a\.?)\b", r"\b(?:master'?s|m\.?s\.?|m\.?a\.?)\b"),
        "bachelor": (r"\b(?:bachelor'?s|b\.?s\.?|b\.?a\.?)\b", r"\b(?:bachelor'?s|b\.?s\.?|b\.?a\.?)\b"),
    }
    for _, (requirement_pattern, candidate_pattern) in requirements.items():
        if re.search(requirement_pattern, job_description, re.IGNORECASE):
            return 100 if re.search(candidate_pattern, resume_text, re.IGNORECASE) else 0
    return 100


def analyze_resume_against_job(resume_text: str, job_description: str) -> dict[str, object]:
    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_description)
    matched = sorted(job_skills & resume_skills)
    missing = sorted(job_skills - resume_skills)

    skill_score = round(len(matched) / len(job_skills) * 100) if job_skills else 0
    experience_score = _experience_score(resume_text, job_description)
    education_score = _education_score(resume_text, job_description)
    # Lightweight lexical overlap is a transparent fallback, not an embedding model.
    resume_terms = {term for term in re.findall(r"[a-zA-Z]{3,}", resume_text.casefold()) if term not in {"the", "and", "for", "with", "from", "that", "this", "you", "your"}}
    job_terms = {term for term in re.findall(r"[a-zA-Z]{3,}", job_description.casefold()) if term not in {"the", "and", "for", "with", "from", "that", "this", "you", "your"}}
    semantic_score = round(len(resume_terms & job_terms) / len(job_terms) * 100) if job_terms else 0
    score = round(0.4 * skill_score + 0.3 * experience_score + 0.2 * education_score + 0.1 * semantic_score)

    recommendations = []
    if missing:
        recommendations.append("Review evidence for these requested skills: " + ", ".join(missing[:8]) + ".")
    if experience_score < 100:
        recommendations.append("Verify the candidate's relevant experience duration; the resume may not demonstrate the requested years.")
    if education_score == 0:
        recommendations.append("Review whether the candidate's education meets the stated degree requirement.")
    if not recommendations:
        recommendations.append("Review the cited resume evidence with a recruiter; this score is decision support, not an automated hiring decision.")

    summary = (
        f"Rule-based fit score {score}/100: skill coverage {skill_score}%, experience indicator "
        f"{experience_score}%, education indicator {education_score}%, and text overlap {semantic_score}%. "
        "Scores are not a validated prediction of job performance."
    )
    return {
        "overall_score": max(0, min(100, score)),
        "skill_score": skill_score,
        "experience_score": experience_score,
        "education_score": education_score,
        "semantic_score": semantic_score,
        "matched_skills": matched,
        "missing_skills": missing,
        "summary": summary,
        "recommendations": recommendations,
    }
