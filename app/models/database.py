"""
Database models for content and tags
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Table, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import List

Base = declarative_base()

# Association table for many-to-many relationship between Content and Tags
content_tags_association = Table(
    'content_tags',
    Base.metadata,
    Column('content_id', Integer, ForeignKey('content.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)

# Association table for category mappings
content_categories_association = Table(
    'content_categories',
    Base.metadata,
    Column('content_id', Integer, ForeignKey('content.id')),
    Column('category_id', Integer, ForeignKey('categories.id'))
)


class Content(Base):
    """Model representing a blog post or article"""
    __tablename__ = "content"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True, nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    content = Column(Text, nullable=False)
    html_content = Column(Text, nullable=True)
    author = Column(String(100), nullable=True)
    
    # Relationships
    tags = relationship("Tag", secondary=content_tags_association, back_populates="contents")
    categories = relationship("Category", secondary=content_categories_association, back_populates="contents")
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True, index=True)
    
    # SEO and CMS
    meta_description = Column(String(160), nullable=True)
    json_ld = Column(Text, nullable=True)  # Stores JSON-LD schema markup


class Tag(Base):
    """Model representing a micro-tag (keyword/entity)"""
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Relationship
    contents = relationship("Content", secondary=content_tags_association, back_populates="tags")
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    usage_count = Column(Integer, default=0)


class Category(Base):
    """Model representing a macro-category (hierarchical taxonomy)"""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Hierarchy
    parent_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    parent = relationship("Category", remote_side=[id], backref="children")
    
    # Relationship
    contents = relationship("Content", secondary=content_categories_association, back_populates="categories")
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    display_order = Column(Integer, default=0)


class TaggingResult(Base):
    """Model storing tagging results for audit and active learning"""
    __tablename__ = "tagging_results"

    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey('content.id'), nullable=False)
    
    # AI-suggested tags
    suggested_categories = Column(Text, nullable=True)  # JSON string
    suggested_tags = Column(Text, nullable=True)  # JSON string
    suggested_entities = Column(Text, nullable=True)  # JSON string
    
    # Editorial validation
    accepted_categories = Column(Text, nullable=True)  # JSON string
    accepted_tags = Column(Text, nullable=True)  # JSON string
    rejected_tags = Column(Text, nullable=True)  # JSON string
    manual_tags = Column(Text, nullable=True)  # JSON string
    
    # Confidence scores
    overall_confidence = Column(Float, default=0.0)
    
    # Flags
    is_validated = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    validated_at = Column(DateTime, nullable=True)
    validated_by = Column(String(100), nullable=True)
