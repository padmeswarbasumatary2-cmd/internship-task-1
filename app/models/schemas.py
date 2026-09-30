"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class TagBase(BaseModel):
    """Base schema for tags"""
    name: str
    slug: str
    description: Optional[str] = None


class TagCreate(TagBase):
    """Schema for creating a tag"""
    pass


class Tag(TagBase):
    """Schema for tag response"""
    id: int
    usage_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class CategoryBase(BaseModel):
    """Base schema for categories"""
    name: str
    slug: str
    description: Optional[str] = None
    parent_id: Optional[int] = None


class CategoryCreate(CategoryBase):
    """Schema for creating a category"""
    pass


class Category(CategoryBase):
    """Schema for category response"""
    id: int
    display_order: int
    created_at: datetime

    class Config:
        from_attributes = True


class ContentBase(BaseModel):
    """Base schema for content"""
    title: str
    slug: str
    content: str
    author: Optional[str] = None


class ContentCreate(ContentBase):
    """Schema for creating content"""
    html_content: Optional[str] = None
    published_at: Optional[datetime] = None


class ContentUpdate(BaseModel):
    """Schema for updating content"""
    title: Optional[str] = None
    content: Optional[str] = None
    html_content: Optional[str] = None


class Content(ContentBase):
    """Schema for content response"""
    id: int
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    meta_description: Optional[str] = None
    tags: List[Tag] = []
    categories: List[Category] = []

    class Config:
        from_attributes = True


class TaggingRequest(BaseModel):
    """Schema for tagging API request"""
    content_id: Optional[int] = None
    title: str
    content: str
    html_content: Optional[str] = None
    include_categories: bool = True
    include_micro_tags: bool = True
    include_entities: bool = True


class SuggestedTag(BaseModel):
    """Schema for a suggested tag with confidence"""
    name: str
    score: float = Field(..., ge=0.0, le=1.0)
    tag_type: str  # "category", "micro-tag", "entity"


class TaggingResponse(BaseModel):
    """Schema for tagging API response"""
    content_id: Optional[int] = None
    suggested_categories: List[SuggestedTag] = []
    suggested_tags: List[SuggestedTag] = []
    suggested_entities: List[SuggestedTag] = []
    overall_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    json_ld: Optional[Dict[str, Any]] = None
    processing_time_ms: float


class ValidationFeedback(BaseModel):
    """Schema for editorial validation feedback"""
    tagging_result_id: int
    accepted_tags: List[str] = []
    rejected_tags: List[str] = []
    manual_tags: List[str] = []


class TaxonomyNode(BaseModel):
    """Schema for taxonomy node in the knowledge graph"""
    id: str
    name: str
    canonical_name: str
    aliases: List[str] = []
    description: Optional[str] = None
    parent_id: Optional[str] = None
    confidence: float = 1.0


class HealthCheckResponse(BaseModel):
    """Schema for health check response"""
    status: str
    version: str
    models_loaded: bool
    database_connected: bool
    redis_connected: bool
