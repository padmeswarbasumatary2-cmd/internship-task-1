from collections.abc import Generator
from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.database import get_db
from app.main import app
from app.models import Base


def test_every_analysis_route_responds_with_persisted_data():
    with TemporaryDirectory() as temp_dir:
        database_path = Path(temp_dir) / "api-smoke.db"
        engine = create_engine(f"sqlite:///{database_path.as_posix()}", connect_args={"check_same_thread": False})
        Base.metadata.create_all(engine)
        test_sessions = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

        def open_test_session() -> Generator[Session, None, None]:
            session = test_sessions()
            try:
                yield session
            finally:
                session.close()

        app.dependency_overrides[get_db] = open_test_session
        try:
            with TestClient(app) as client:
                health = client.get("/api/health")
                assert health.status_code == 200
                assert health.json()["services"]["database"] == "available"

                upload = client.post(
                    "/api/upload",
                    json={
                        "file": "Jane Doe\nPython, SQL, React, APIs, dashboards",
                        "jobDescription": "Data Analyst\nPython, SQL, Excel, Power BI, dashboards",
                    },
                )
                assert upload.status_code == 201
                ids = upload.json()

                resume = client.get(f"/api/resumes/{ids['resumeId']}")
                assert resume.status_code == 200
                assert resume.json()["resume"]["jobId"] == ids["jobId"]
                assert resume.json()["resume"]["profile"]["contact"]["email"] is None
                assert resume.json()["resume"]["profile"]["skills"]
                assert "file" not in resume.json()["resume"]

                computed = client.post(
                    "/api/analyze",
                    json={"resumeId": ids["resumeId"], "jobId": ids["jobId"]},
                )
                assert computed.status_code == 200
                analysis_id = computed.json()["id"]
                assert 0 <= computed.json()["overall_score"] <= 100
                assert 0 <= computed.json()["skill_score"] <= 100
                assert computed.json()["recommendations"]

                analysis_list = client.get("/api/analyses")
                assert analysis_list.status_code == 200
                assert len(analysis_list.json()["rows"]) == 1

                analysis = client.get(f"/api/analyses/{analysis_id}")
                assert analysis.status_code == 200
                assert analysis.json()["analysis"]["id"] == analysis_id

                document_upload = client.post(
                    "/api/upload-file",
                    data={"job_description": "Python developer with SQL background"},
                    files={"resume": ("resume.txt", b"Jane Doe\nPython Engineer with SQL and APIs.", "text/plain")},
                )
                assert document_upload.status_code == 201

                missing_resume = client.get("/api/resumes/does-not-exist")
                assert missing_resume.status_code == 404
        finally:
            app.dependency_overrides.pop(get_db, None)
            engine.dispose()
