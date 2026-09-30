"""
Lightweight API demonstration (no database/cache required)
Shows the tagging engine working with mock results
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import json
from datetime import datetime

# Initialize FastAPI
app = FastAPI(
    title="Automated Content Tagging Engine",
    version="1.0.0",
    description="Demo mode - shows API endpoints (no DB/cache required)"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============= SCHEMAS =============

class SuggestedTag(BaseModel):
    name: str
    score: float
    tag_type: str

class TaggingRequest(BaseModel):
    title: str
    content: str
    include_categories: bool = True
    include_tags: bool = True
    include_entities: bool = True

class TaggingResponse(BaseModel):
    suggested_categories: List[SuggestedTag]
    suggested_tags: List[SuggestedTag]
    suggested_entities: List[SuggestedTag]
    overall_confidence: float
    json_ld: dict
    processing_time_ms: float

class HealthResponse(BaseModel):
    status: str
    version: str
    models_loaded: bool
    database_connected: bool
    redis_connected: bool

# ============= ENDPOINTS =============

@app.get("/")
def root():
    """Root endpoint with API info"""
    return {
        "app": "Automated Content Tagging Engine",
        "version": "1.0.0",
        "mode": "demo (no database/cache required)",
        "docs": "http://localhost:8000/docs",
        "health": "http://localhost:8000/api/v1/health"
    }

@app.get("/api/v1/health", response_model=HealthResponse)
def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        models_loaded=False,  # Demo mode doesn't load heavy models
        database_connected=False,  # No database in demo mode
        redis_connected=False  # No Redis in demo mode
    )

@app.post("/api/v1/tag-content", response_model=TaggingResponse)
def tag_content(request: TaggingRequest):
    """Main tagging endpoint - returns mock results"""
    
    # Mock taxonomy-based categories
    if request.include_categories:
        categories = [
            SuggestedTag(name="Machine Learning", score=0.92, tag_type="category"),
            SuggestedTag(name="Data Science", score=0.87, tag_type="category"),
        ]
    else:
        categories = []
    
    # Mock semantic tags
    if request.include_tags:
        tags = [
            SuggestedTag(name="neural networks", score=0.89, tag_type="micro-tag"),
            SuggestedTag(name="deep learning", score=0.85, tag_type="micro-tag"),
            SuggestedTag(name="pytorch", score=0.81, tag_type="micro-tag"),
        ]
    else:
        tags = []
    
    # Mock entities (NER)
    if request.include_entities:
        entities = [
            SuggestedTag(name="PyTorch", score=0.95, tag_type="entity:PRODUCT"),
            SuggestedTag(name="Google", score=0.91, tag_type="entity:ORG"),
        ]
    else:
        entities = []
    
    # Mock JSON-LD schema
    json_ld = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": request.title,
        "keywords": [tag.name for tag in tags],
        "about": [cat.name for cat in categories]
    }
    
    response = TaggingResponse(
        suggested_categories=categories,
        suggested_tags=tags,
        suggested_entities=entities,
        overall_confidence=0.88,
        json_ld=json_ld,
        processing_time_ms=42.5  # Mock processing time
    )
    
    return response

@app.get("/api/v1/categories")
def get_categories():
    """List all taxonomy categories"""
    return {
        "categories": [
            {"id": "ml", "name": "Machine Learning", "parent_id": None},
            {"id": "dl", "name": "Deep Learning", "parent_id": "ml"},
            {"id": "nlp", "name": "Natural Language Processing", "parent_id": "ml"},
            {"id": "cv", "name": "Computer Vision", "parent_id": "ml"},
            {"id": "ds", "name": "Data Science", "parent_id": None},
            {"id": "devops", "name": "DevOps", "parent_id": None},
        ]
    }

@app.get("/api/v1/taxonomy")
def get_taxonomy():
    """Export full taxonomy as JSON"""
    return {
        "version": "1.0",
        "last_updated": datetime.now().isoformat(),
        "nodes": 50,
        "structure": "Hierarchical DAG with fuzzy matching and aliases",
        "features": [
            "Entity resolution",
            "Synonym normalization", 
            "Batch processing",
            "Confidence scoring"
        ]
    }

@app.get("/api/v1/model-info")
def model_info():
    """Return loaded model names and parameters"""
    return {
        "status": "demo_mode",
        "message": "Full models require: pytorch, transformers, spacy, keybert installation",
        "available_models": {
            "multi_label_classifier": "Ready (requires transformers + torch)",
            "sentence_transformer": "Ready (requires sentence-transformers)",
            "ner_model": "Ready (requires spacy)",
            "keybert": "Ready (requires keybert)"
        },
        "to_install_all": "pip install -r requirements.txt && python -m spacy download en_core_web_sm"
    }

@app.post("/api/v1/validate-tags")
def validate_tags(feedback: dict):
    """Accept editorial feedback for active learning"""
    return {
        "status": "feedback_received",
        "message": "In demo mode - feedback stored in memory only",
        "feedback_count": 1
    }

@app.post("/api/v1/resolve-entity")
def resolve_entity(entity: str):
    """Resolve entity to canonical form"""
    # Mock entity resolution
    resolutions = {
        "pytorch": {"canonical": "PyTorch", "confidence": 1.0, "type": "PRODUCT"},
        "torch": {"canonical": "PyTorch", "confidence": 0.95, "type": "PRODUCT"},
        "tensorflow": {"canonical": "TensorFlow", "confidence": 1.0, "type": "PRODUCT"},
        "keras": {"canonical": "Keras", "confidence": 0.98, "type": "LIBRARY"},
        "react": {"canonical": "React", "confidence": 1.0, "type": "LIBRARY"},
    }
    
    entity_lower = entity.lower()
    if entity_lower in resolutions:
        return {"entity": entity, **resolutions[entity_lower]}
    else:
        return {
            "entity": entity,
            "canonical": entity,
            "confidence": 0.0,
            "message": "Not in demo taxonomy"
        }

@app.post("/api/v1/batch-tag")
def batch_tag(requests: List[TaggingRequest]):
    """Process multiple documents"""
    results = []
    for req in requests:
        result = tag_content(req)
        results.append(result)
    return {"count": len(results), "results": results}

# ============= STARTUP/SHUTDOWN =============

@app.on_event("startup")
async def startup_event():
    print("✓ Lightweight demo server started")
    print("✓ Visit http://localhost:8000/docs for interactive API explorer")

@app.on_event("shutdown")
async def shutdown_event():
    print("✓ Server shutting down")

if __name__ == "__main__":
    import uvicorn
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║  🚀 AUTOMATED CONTENT TAGGING ENGINE - DEMO MODE           ║
    ╠════════════════════════════════════════════════════════════╣
    ║  Starting lightweight API demonstration...                 ║
    ║  No database or cache required for this demo               ║
    ║                                                            ║
    ║  📍 API Available at: http://localhost:8000                ║
    ║  📚 Interactive Docs: http://localhost:8000/docs           ║
    ║  ❤️  Health Check: http://localhost:8000/api/v1/health     ║
    ║                                                            ║
    ║  Try tagging some content at the /docs endpoint!          ║
    ║  Press Ctrl+C to stop the server                          ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    uvicorn.run(app, host="0.0.0.0", port=8000)
