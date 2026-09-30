"""
Core tagging service orchestrating the ML pipeline
"""
import asyncio
import json
from typing import List, Optional, Tuple
import time
from datetime import datetime

from ..models.schemas import TaggingResponse, SuggestedTag, ValidationFeedback
from ..ml_pipeline.preprocessing import DocumentPreprocessor
from ..ml_pipeline.multi_label_classifier import MultiLabelClassifier
from ..ml_pipeline.keybert_extractor import SemanticKeyphraseExtractor
from ..ml_pipeline.ner_extractor import NamedEntityRecognizer
from ..ml_pipeline.taxonomy_graph import TaxonomyGraph, TaxonomyNode
from ..config import settings


class TaggingService:
    """
    Orchestrates the complete tagging pipeline combining multiple NLP/ML models.
    Coordinates preprocessing, classification, keyphrase extraction, NER, and taxonomy resolution.
    """

    def __init__(self):
        """Initialize all ML components"""
        self.models_loaded = False
        
        try:
            # Initialize components
            self.preprocessor = DocumentPreprocessor()
            self.classifier = MultiLabelClassifier(settings.MULTI_LABEL_MODEL)
            self.keyphrase_extractor = SemanticKeyphraseExtractor(settings.SENTENCE_TRANSFORMER_MODEL)
            self.ner = NamedEntityRecognizer(settings.NER_MODEL)
            self.taxonomy = TaxonomyGraph()
            
            self.models_loaded = True
            print("✓ All ML models loaded successfully")
        except Exception as e:
            print(f"✗ Error loading models: {e}")
            self.models_loaded = False

    async def tag_document(
        self,
        title: str,
        content: str,
        html_content: Optional[str] = None,
        include_categories: bool = True,
        include_micro_tags: bool = True,
        include_entities: bool = True
    ) -> TaggingResponse:
        """
        Complete tagging pipeline for a single document
        
        Args:
            title: Document title
            content: Document content (Markdown or plain text)
            html_content: HTML version of content (optional)
            include_categories: Whether to extract macro-categories
            include_micro_tags: Whether to extract micro-tags
            include_entities: Whether to extract named entities
        
        Returns:
            TaggingResponse with all extracted tags
        """
        start_time = time.time()
        
        try:
            # Preprocess document
            processed_text, structure = self.preprocessor.preprocess_document(
                html_content or content,
                is_html=bool(html_content)
            )
            
            # Combine title for importance
            full_text = f"{title}. {processed_text}"
            
            # Parallel execution of ML tasks
            results = await asyncio.gather(
                self._extract_categories(full_text) if include_categories else asyncio.sleep(0),
                self._extract_micro_tags(processed_text) if include_micro_tags else asyncio.sleep(0),
                self._extract_entities(processed_text) if include_entities else asyncio.sleep(0)
            )
            
            categories, micro_tags, entities = results if include_categories else ([], [], [])
            
            # Generate JSON-LD schema markup
            json_ld = self._generate_jsonld(title, categories, micro_tags)
            
            # Calculate overall confidence
            all_scores = (
                [c.score for c in categories] +
                [m.score for m in micro_tags] +
                [e.score for e in entities]
            )
            overall_confidence = sum(all_scores) / len(all_scores) if all_scores else 0.0
            
            # Create response
            response = TaggingResponse(
                suggested_categories=categories,
                suggested_tags=micro_tags,
                suggested_entities=entities,
                overall_confidence=overall_confidence,
                json_ld=json_ld,
                processing_time_ms=time.time() - start_time
            )
            
            return response
            
        except Exception as e:
            print(f"Error during tagging: {e}")
            raise

    async def _extract_categories(self, text: str) -> List[SuggestedTag]:
        """Extract macro-categories using multi-label classifier"""
        try:
            predictions = self.classifier.predict(
                text,
                top_k=settings.MAX_TAGS_PER_DOCUMENT
            )
            
            result = []
            for pred in predictions:
                result.append(SuggestedTag(
                    name=pred["category"],
                    score=pred["score"],
                    tag_type="category"
                ))
            
            return result
        except Exception as e:
            print(f"Category extraction error: {e}")
            return []

    async def _extract_micro_tags(self, text: str) -> List[SuggestedTag]:
        """Extract micro-tags using KeyBERT"""
        try:
            keywords = self.keyphrase_extractor.extract_keyphrases(
                text,
                top_n=settings.MAX_TAGS_PER_DOCUMENT,
                min_score=settings.KEYBERT_MIN_SCORE
            )
            
            result = []
            for keyword in keywords:
                # Resolve to canonical taxonomy node
                node_id, confidence = self.taxonomy.resolve_entity(keyword["phrase"])
                
                normalized_name = keyword["phrase"]
                if node_id:
                    node = self.taxonomy.get_node(node_id)
                    if node:
                        normalized_name = node.name
                
                result.append(SuggestedTag(
                    name=normalized_name,
                    score=keyword["score"] * confidence if node_id else keyword["score"],
                    tag_type="micro-tag"
                ))
            
            return result
        except Exception as e:
            print(f"Micro-tag extraction error: {e}")
            return []

    async def _extract_entities(self, text: str) -> List[SuggestedTag]:
        """Extract named entities using NER"""
        try:
            entities = self.ner.extract_entities(text)
            
            result = []
            for entity in entities:
                # Resolve to taxonomy
                node_id, confidence = self.taxonomy.resolve_entity(entity["text"])
                
                result.append(SuggestedTag(
                    name=entity["text"],
                    score=entity.get("score", 0.8) * confidence if node_id else entity.get("score", 0.8),
                    tag_type=f"entity:{entity['type']}"
                ))
            
            # Limit to max tags
            return result[:settings.MAX_TAGS_PER_DOCUMENT]
        except Exception as e:
            print(f"Entity extraction error: {e}")
            return []

    def _generate_jsonld(self, title: str, categories: List[SuggestedTag], tags: List[SuggestedTag]) -> dict:
        """
        Generate JSON-LD schema markup for SEO
        
        Returns schema-compliant structured data
        """
        keywords = [t.name for t in tags[:10]]  # Top 10 tags
        about = [
            {
                "@type": "Thing",
                "name": cat.name
            }
            for cat in categories[:5]  # Top 5 categories
        ]
        
        schema = {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": title,
            "keywords": keywords,
            "about": about,
            "datePublished": datetime.utcnow().isoformat()
        }
        
        return schema

    async def store_tagging_result(self, content_id: int, result: TaggingResponse):
        """Store tagging result in database for audit trail"""
        # This would connect to database in production
        print(f"Stored tagging result for content_id={content_id}")

    async def store_validation_feedback(self, feedback: ValidationFeedback) -> int:
        """Store editorial validation feedback for active learning"""
        # This would update database and trigger retraining pipeline
        print(f"Stored validation feedback: {feedback}")
        return feedback.tagging_result_id

    async def get_all_categories(self) -> List[dict]:
        """Get all available categories"""
        root_nodes = [n for n in self.taxonomy.nodes.values() if n.type == "root"]
        
        categories = []
        for root in root_nodes:
            children = self.taxonomy.get_children(root.id)
            categories.append({
                "name": root.name,
                "id": root.id,
                "subcategories": [
                    {"name": child.name, "id": child.id}
                    for child in children
                ]
            })
        
        return categories

    def get_taxonomy_json(self) -> str:
        """Export taxonomy as JSON"""
        return self.taxonomy.export_as_json()

    def resolve_entity(self, entity_text: str) -> Tuple[Optional[str], float]:
        """Resolve entity to canonical taxonomy node"""
        return self.taxonomy.resolve_entity(entity_text)

    def get_taxonomy_node(self, node_id: str) -> Optional[TaxonomyNode]:
        """Get taxonomy node by ID"""
        return self.taxonomy.get_node(node_id)
