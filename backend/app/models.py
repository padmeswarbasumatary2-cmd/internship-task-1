from __future__ import annotations

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, JSON, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    job_description: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    resumes: Mapped[list[Resume]] = relationship(back_populates="job", cascade="all, delete-orphan")
    analyses: Mapped[list[Analysis]] = relationship(back_populates="job", cascade="all, delete-orphan")


class Resume(Base):
    __tablename__ = "resumes"
    __table_args__ = (Index("ix_resumes_job_id", "job_id"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False, default="pasted-text.txt")
    file: Mapped[str] = mapped_column(Text, nullable=False)
    profile: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    job: Mapped[Job] = relationship(back_populates="resumes")
    analyses: Mapped[list[Analysis]] = relationship(back_populates="resume", cascade="all, delete-orphan")


class Analysis(Base):
    __tablename__ = "analyses"
    __table_args__ = (
        CheckConstraint("overall_score >= 0 AND overall_score <= 100", name="ck_analyses_score_range"),
        CheckConstraint("skill_score BETWEEN 0 AND 100", name="ck_analyses_skill_score_range"),
        CheckConstraint("experience_score BETWEEN 0 AND 100", name="ck_analyses_experience_score_range"),
        CheckConstraint("education_score BETWEEN 0 AND 100", name="ck_analyses_education_score_range"),
        CheckConstraint("semantic_score BETWEEN 0 AND 100", name="ck_analyses_semantic_score_range"),
        Index("ix_analyses_created_at", "created_at"),
        Index("ix_analyses_job_id", "job_id"),
    )

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    resume_id: Mapped[str] = mapped_column(ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, unique=True)
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    overall_score: Mapped[int] = mapped_column(nullable=False)
    matched_skills: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    missing_skills: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    skill_score: Mapped[int] = mapped_column(nullable=False, default=0)
    experience_score: Mapped[int] = mapped_column(nullable=False, default=0)
    education_score: Mapped[int] = mapped_column(nullable=False, default=0)
    semantic_score: Mapped[int] = mapped_column(nullable=False, default=0)
    recommendations: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    resume: Mapped[Resume] = relationship(back_populates="analyses")
    job: Mapped[Job] = relationship(back_populates="analyses")
