from app.services.analysis import analyze_resume_against_job, extract_skills


def test_analysis_returns_score_and_missing_skills():
    resume_text = """
    Jane Doe
    Python, FastAPI, SQL, React, APIs
    Built dashboards for internal customer reporting and optimized data pipelines.
    """
    job_description = """
    We are hiring a Data Analyst with Python, SQL, Power BI, and Excel experience.
    Must be comfortable with dashboards and data cleaning.
    """

    result = analyze_resume_against_job(resume_text, job_description)

    assert 0 <= result["overall_score"] <= 100
    assert result["matched_skills"]
    assert result["missing_skills"]
    assert result["summary"]


def test_skill_aliases_map_to_canonical_skills_and_infer_python():
    assert extract_skills("Built UI with React.js and NodeJS; used Pandas and NumPy") == {
        "react",
        "node.js",
        "python",
    }


def test_skill_detection_does_not_match_inside_unrelated_words():
    assert "sql" not in extract_skills("The candidate was a strong and reliable teammate.")
