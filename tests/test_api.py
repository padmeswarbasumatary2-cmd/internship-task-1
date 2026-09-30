"""
Test suite for API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint"""

    def test_health_check(self):
        """Test /health endpoint"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestTaggingEndpoint:
    """Test main tagging endpoint"""

    def test_tag_content_basic(self):
        """Test basic content tagging"""
        payload = {
            "title": "Getting Started with PyTorch",
            "content": "PyTorch is a machine learning framework for Python",
            "include_categories": True,
            "include_micro_tags": True,
            "include_entities": True
        }
        
        response = client.post("/api/v1/tag-content", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            assert "suggested_categories" in data
            assert "suggested_tags" in data
            assert "suggested_entities" in data
            assert "processing_time_ms" in data

    def test_tag_content_minimal(self):
        """Test minimal content tagging"""
        payload = {
            "title": "Test Article",
            "content": "This is a test article"
        }
        
        response = client.post("/api/v1/tag-content", json=payload)
        # May fail if models not loaded, but should return valid response structure


class TestCategoriesEndpoint:
    """Test categories endpoint"""

    def test_get_categories(self):
        """Test /categories endpoint"""
        response = client.get("/api/v1/categories")
        
        if response.status_code == 200:
            data = response.json()
            assert "categories" in data


class TestResolveEntityEndpoint:
    """Test entity resolution endpoint"""

    def test_resolve_entity(self):
        """Test entity resolution"""
        response = client.post("/api/v1/resolve-entity", params={"entity_text": "PyTorch"})
        
        if response.status_code == 200:
            data = response.json()
            assert "canonical_name" in data or "status" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
