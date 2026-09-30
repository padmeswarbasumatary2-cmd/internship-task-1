"""
Named Entity Recognition (NER) using spaCy and transformers
"""
from typing import List, Dict
import spacy
from transformers import pipeline


class NamedEntityRecognizer:
    """
    Extract named entities (PERSON, ORG, PRODUCT, GPE) from text.
    Provides detailed entity metadata for tagging specific named references.
    """

    def __init__(self, model_name: str = "en_core_web_sm"):
        """
        Initialize the NER extractor
        
        Args:
            model_name: spaCy model identifier
        """
        self.model_name = model_name
        
        try:
            self.nlp = spacy.load(model_name)
        except OSError:
            print(f"Warning: spaCy model '{model_name}' not found.")
            print(f"Install with: python -m spacy download {model_name}")
            self.nlp = None
        
        # Supported entity types for tagging
        self.supported_entities = {
            "PERSON": "person",
            "ORG": "organization",
            "PRODUCT": "product",
            "GPE": "location",
            "EVENT": "event"
        }

    def extract_entities(self, text: str) -> List[Dict[str, str]]:
        """
        Extract named entities from text
        
        Args:
            text: Input text
        
        Returns:
            List of dicts with 'text', 'type', and 'score' keys
        """
        if self.nlp is None:
            return []
        
        doc = self.nlp(text)
        entities = []
        
        # Extract entities
        for ent in doc.ents:
            if ent.label_ in self.supported_entities:
                entity_dict = {
                    "text": ent.text,
                    "type": self.supported_entities[ent.label_],
                    "label": ent.label_,
                    "start_char": ent.start_char,
                    "end_char": ent.end_char,
                    "score": 0.9  # spaCy doesn't provide confidence scores by default
                }
                entities.append(entity_dict)
        
        return entities

    def extract_entities_by_type(self, text: str, entity_type: str) -> List[Dict[str, str]]:
        """
        Extract entities of a specific type
        
        Args:
            text: Input text
            entity_type: Entity type to extract (PERSON, ORG, PRODUCT, GPE, EVENT)
        
        Returns:
            List of entity dicts of the specified type
        """
        all_entities = self.extract_entities(text)
        return [e for e in all_entities if e["label"] == entity_type]

    def get_entity_context(self, text: str, entity: Dict[str, str], context_window: int = 50) -> str:
        """
        Get surrounding context for an entity
        
        Args:
            text: Full text
            entity: Entity dict
            context_window: Number of characters before/after entity
        
        Returns:
            Context string
        """
        start = max(0, entity["start_char"] - context_window)
        end = min(len(text), entity["end_char"] + context_window)
        return text[start:end]

    def extract_batch(self, texts: List[str]) -> List[List[Dict[str, str]]]:
        """
        Extract entities from multiple texts
        
        Args:
            texts: List of input texts
        
        Returns:
            List of entity lists
        """
        results = []
        for text in texts:
            results.append(self.extract_entities(text))
        return results

    def extract_unique_entities(self, text: str, lowercase: bool = True) -> List[str]:
        """
        Extract unique entity mentions
        
        Args:
            text: Input text
            lowercase: Whether to lowercase entity text
        
        Returns:
            List of unique entity strings
        """
        entities = self.extract_entities(text)
        unique_entities = set()
        
        for entity in entities:
            entity_text = entity["text"]
            if lowercase:
                entity_text = entity_text.lower()
            unique_entities.add(entity_text)
        
        return list(unique_entities)


class TransformerNER:
    """
    Alternative NER using Hugging Face transformer models
    Provides entity classification with confidence scores
    """

    def __init__(self, model_name: str = "dbmdz/bert-base-cased-finetuned-conll03-english"):
        """
        Initialize transformer-based NER
        
        Args:
            model_name: Hugging Face model identifier
        """
        try:
            self.ner_pipeline = pipeline("ner", model=model_name, aggregation_strategy="simple")
        except Exception as e:
            print(f"Warning: Could not load transformer NER model: {e}")
            self.ner_pipeline = None

    def extract_entities(self, text: str) -> List[Dict[str, str]]:
        """
        Extract entities using transformer model
        
        Args:
            text: Input text
        
        Returns:
            List of entity dicts with scores
        """
        if self.ner_pipeline is None:
            return []
        
        results = self.ner_pipeline(text)
        
        # Format results
        entities = []
        for result in results:
            if result['entity_group'] in {'PER', 'ORG', 'LOC', 'MISC'}:
                entity_type_map = {
                    'PER': 'person',
                    'ORG': 'organization',
                    'LOC': 'location',
                    'MISC': 'miscellaneous'
                }
                
                entities.append({
                    "text": result['word'],
                    "type": entity_type_map.get(result['entity_group']),
                    "label": result['entity_group'],
                    "score": float(result['score'])
                })
        
        return entities
