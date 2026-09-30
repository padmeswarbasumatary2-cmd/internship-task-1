from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel, Field
from sqlalchemy import desc, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Analysis, Job, Resume
from app.services.analysis import analyze_resume_against_job, extract_skills
from app.services.documents import extract_document_text, extract_profile

router = APIRouter()


class UploadRequest(BaseModel):
    file: str = ""
    jobDescription: str = Field(..., min_length=1)


class AnalyzeRequest(BaseModel):
    resumeId: str = Field(..., min_length=1)
    jobId: str = Field(..., min_length=1)


def _as_analysis(analysis: Analysis) -> dict[str, object]:
    return {
        "id": analysis.id,
        "resumeId": analysis.resume_id,
        "jobId": analysis.job_id,
        "overall_score": analysis.overall_score,
        "matched_skills": analysis.matched_skills,
        "missing_skills": analysis.missing_skills,
        "summary": analysis.summary,
        "skill_score": analysis.skill_score,
        "experience_score": analysis.experience_score,
        "education_score": analysis.education_score,
        "semantic_score": analysis.semantic_score,
        "recommendations": analysis.recommendations,
    }


@router.get("/health")
def get_health(db: Session = Depends(get_db)) -> dict[str, object]:
    try:
        db.execute(select(1))
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        ) from error
    return {"status": "ok", "services": {"database": "available", "storage": "inline"}}


@router.post("/upload", status_code=status.HTTP_201_CREATED)
def upload_resume(payload: UploadRequest, db: Session = Depends(get_db)) -> dict[str, str]:
    resume_text = payload.file.strip()
    if len(resume_text) < 20:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Resume text must contain at least 20 characters.")
    return _save_resume(resume_text, "pasted-text.txt", payload.jobDescription, db)


@router.post("/upload-file", status_code=status.HTTP_201_CREATED)
async def upload_resume_file(
    job_description: str = Form(..., min_length=1),
    resume: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    try:
        resume_text = extract_document_text(resume.filename or "resume", await resume.read(10 * 1024 * 1024 + 1))
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
    return _save_resume(resume_text, resume.filename or "resume", job_description, db)


def _save_resume(resume_text: str, filename: str, job_description: str, db: Session) -> dict[str, str]:
    job_description = job_description.strip()
    if len(job_description) < 10:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Job description must contain at least 10 characters.")
    job_id = str(uuid4())
    resume_id = str(uuid4())
    analysis_id = f"analysis-{resume_id}"
    job = Job(id=job_id, job_description=job_description)
    profile = extract_profile(resume_text)
    profile["skills"] = sorted(extract_skills(resume_text))
    resume = Resume(id=resume_id, filename=filename[:255], file=resume_text, profile=profile, job_id=job_id)
    db.add_all([job, resume])
    db.commit()
    return {"resumeId": resume_id, "jobId": job_id, "analysisId": analysis_id}


@router.get("/resumes/{resume_id}")
def get_resume(resume_id: str, db: Session = Depends(get_db)) -> dict[str, object]:
    resume = db.get(Resume, resume_id)
    if resume is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    return {
        "resume": {
            "id": resume.id,
            "filename": resume.filename,
            "jobDescription": resume.job.job_description,
            "jobId": resume.job_id,
            "profile": {
                "name": None,
                "contact": {"email": None, "phone": None, "linkedin": None, "github": None},
                "education": [],
                "experienceHighlights": [],
                "graduationYears": [],
                "skills": resume.profile.get("skills", []),
                "educationEntries": len(resume.profile.get("education", [])),
                "experienceEntries": len(resume.profile.get("experienceHighlights", [])),
            },
        }
    }


@router.post("/analyze")
def run_analysis(payload: AnalyzeRequest, db: Session = Depends(get_db)) -> dict[str, object]:
    resume = db.get(Resume, payload.resumeId)
    if resume is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Resume not found")
    if resume.job_id != payload.jobId:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Job does not match resume")

    computed = analyze_resume_against_job(resume.file, resume.job.job_description)
    analysis_id = f"analysis-{resume.id}"
    analysis = db.get(Analysis, analysis_id)
    if analysis is None:
        analysis = Analysis(
            id=analysis_id,
            resume_id=resume.id,
            job_id=resume.job_id,
            overall_score=computed["overall_score"],
            matched_skills=computed["matched_skills"],
            missing_skills=computed["missing_skills"],
            summary=computed["summary"],
            skill_score=computed["skill_score"],
            experience_score=computed["experience_score"],
            education_score=computed["education_score"],
            semantic_score=computed["semantic_score"],
            recommendations=computed["recommendations"],
        )
        db.add(analysis)
    else:
        analysis.overall_score = computed["overall_score"]
        analysis.matched_skills = computed["matched_skills"]
        analysis.missing_skills = computed["missing_skills"]
        analysis.summary = computed["summary"]
        analysis.skill_score = computed["skill_score"]
        analysis.experience_score = computed["experience_score"]
        analysis.education_score = computed["education_score"]
        analysis.semantic_score = computed["semantic_score"]
        analysis.recommendations = computed["recommendations"]
    db.commit()
    db.refresh(analysis)
    return _as_analysis(analysis)


@router.get("/analyses")
def list_analyses(db: Session = Depends(get_db)) -> dict[str, list[dict[str, object]]]:
    analyses = db.scalars(select(Analysis).order_by(desc(Analysis.created_at))).all()
    rows = []
    for analysis in analyses:
        job = db.get(Job, analysis.job_id)
        job_title = (job.job_description.splitlines()[0][:80] if job else "") or "Untitled role"
        candidate = f"Candidate {analysis.resume_id[:8]}"
        rows.append(
            {
                **_as_analysis(analysis),
                "candidate": candidate,
                "jobTitle": job_title,
                "score": analysis.overall_score,
            }
        )
    return {"rows": rows}


@router.get("/analyses/{analysis_id}")
def get_analysis(analysis_id: str, db: Session = Depends(get_db)) -> dict[str, object]:
    analysis = db.get(Analysis, analysis_id)
    if analysis is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found")
    return {"analysis": _as_analysis(analysis)}
