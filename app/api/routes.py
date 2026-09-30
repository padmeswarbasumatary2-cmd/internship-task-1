"""
Main API routes for content tagging endpoints
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional
import time
from datetime import datetime
import json

from ..models.schemas import (
    TaggingRequest, TaggingResponse, ContentCreate, Content,
    ValidationFeedback, HealthCheckResponse
)
from ..services.tagging_service import TaggingService
from ..services.cache_service import CacheService
from ..config import settings

router = APIRouter(prefix=settings.API_PREFIX)

# Initialize services lazily so app startup does not block on downloading ML models
# and large NLP dependencies.
tagging_service = None
cache_service = CacheService()


def get_tagging_service() -> TaggingService:
    """Create the tagging service on first use instead of at import time."""
    global tagging_service
    if tagging_service is None:
        tagging_service = TaggingService()
    return tagging_service


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    service = get_tagging_service()
    return HealthCheckResponse(
        status="healthy",
        version=settings.APP_VERSION,
        models_loaded=service.models_loaded,
        database_connected=True,
        redis_connected=cache_service.is_connected()
    )


@router.post("/tag-content", response_model=TaggingResponse)
async def tag_content(request: TaggingRequest, background_tasks: BackgroundTasks):
    """
    Main tagging endpoint: analyzes content and returns suggested tags
    
    Args:
        request: TaggingRequest with content to analyze
        background_tasks: For async operations
    
    Returns:
        TaggingResponse with suggested tags, categories, and entities
    """
    start_time = time.time()
    
    try:
        # Check cache first
        cache_key = f"tagging:{request.slug or request.title}"
        cached_result = cache_service.get(cache_key)
        if cached_result:
            return TaggingResponse(**json.loads(cached_result))
        
        service = get_tagging_service()

        # Perform tagging
        result = await service.tag_document(
            title=request.title,
            content=request.content,
            html_content=request.html_content,
            include_categories=request.include_categories,
            include_micro_tags=request.include_micro_tags,
            include_entities=request.include_entities
        )
        
        # Cache result
        result_dict = result.dict()
        result_dict["processing_time_ms"] = time.time() - start_time
        cache_service.set(cache_key, json.dumps(result_dict), settings.CACHE_TTL)
        
        # Store in database asynchronously if content_id provided
        if request.content_id:
            background_tasks.add_task(
                service.store_tagging_result,
                request.content_id,
                result
            )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tagging failed: {str(e)}")


@router.post("/validate-tags")
async def validate_tags(feedback: ValidationFeedback):
    """
    Editorial validation feedback for active learning
    
    Args:
        feedback: User feedback on suggested tags
    
    Returns:
        Success message and feedback ID
    """
    try:
        service = get_tagging_service()
        feedback_id = await service.store_validation_feedback(feedback)
        return {
            "status": "success",
            "feedback_id": feedback_id,
            "message": "Feedback recorded for model retraining"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@router.get("/categories")
async def get_categories():
    """Get all available categories in the taxonomy"""
    try:
        service = get_tagging_service()
        categories = await service.get_all_categories()
        return {"categories": categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/taxonomy")
async def get_taxonomy():
    """Get the full taxonomy graph as JSON"""
    try:
        service = get_tagging_service()
        taxonomy_json = service.get_taxonomy_json()
        return {"taxonomy": json.loads(taxonomy_json)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/resolve-entity")
async def resolve_entity(entity_text: str):
    """
    Resolve a raw entity text to canonical taxonomy node
    
    Args:
        entity_text: Raw entity text to resolve
    
    Returns:
        Canonical node and confidence score
    """
    try:
        service = get_tagging_service()
        node_id, score = service.resolve_entity(entity_text)
        
        if node_id:
            node = service.get_taxonomy_node(node_id)
            return {
                "canonical_name": node.name if node else entity_text,
                "node_id": node_id,
                "confidence": score
            }
        else:
            return {
                "status": "not_found",
                "entity": entity_text,
                "confidence": score
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch-tag")
async def batch_tag(requests: List[TaggingRequest]):
    """
    Process multiple documents in batch
    
    Args:
        requests: List of tagging requests
    
    Returns:
        List of tagging responses
    """
    try:
        results = []
        for req in requests:
            result = await tag_content(req, BackgroundTasks())
            results.append(result)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/model-info")
async def get_model_info():
    """Get information about loaded models"""
    return {
        "multi_label_classifier": settings.MULTI_LABEL_MODEL,
        "sentence_transformer": settings.SENTENCE_TRANSFORMER_MODEL,
        "ner_model": settings.NER_MODEL,
        "max_tags": settings.MAX_TAGS_PER_DOCUMENT
    }


@router.get("/api-docs")
async def api_docs():
    """Return API documentation"""
    return {
        "title": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "endpoints": {
            "/health": "Check API health status",
            "/tag-content": "Analyze content and generate tags",
            "/validate-tags": "Provide editorial feedback",
            "/categories": "List all taxonomy categories",
            "/taxonomy": "Export full taxonomy graph",
            "/resolve-entity": "Normalize entity to canonical form",
            "/batch-tag": "Process multiple documents",
            "/model-info": "Get loaded model information"
        }
    }
