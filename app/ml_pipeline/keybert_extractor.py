"""
Semantic keyphrase extraction using KeyBERT with MMR
"""
from typing import List, Dict, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
from keybert import KeyBERT
import re


class SemanticKeyphraseExtractor:
    """
    Extract semantically relevant keyphrases using KeyBERT + Maximal Marginal Relevance (MMR).
    Generates diverse micro-tags with high relevance to document content.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the keyphrase extractor
        
        Args:
            model_name: Sentence-Transformers model identifier
        """
        self.model_name = model_name
        self.sentence_transformer = SentenceTransformer(model_name)
        self.keybert = KeyBERT(model=self.sentence_transformer)

    def extract_keyphrases(
        self,
        text: str,
        top_n: int = 10,
        min_score: float = 0.3,
        diversity: float = 0.5
    ) -> List[Dict[str, float]]:
        """
        Extract keyphrases using KeyBERT with MMR
        
        Args:
            text: Input document text
            top_n: Number of keyphrases to extract
            min_score: Minimum relevance score (0.0 to 1.0)
            diversity: Diversity parameter for MMR (0.0 = pure relevance, 1.0 = pure diversity)
        
        Returns:
            List of dicts with 'phrase' and 'score' keys
        """
        # Extract keyphrases with KeyBERT
        keywords = self.keybert.extract_keywords(
            text,
            language="english",
            ngram_range=(1, 3),  # 1 to 3-word phrases
            top_n=top_n,
            use_mmr=True,  # Enable MMR for diversity
            diversity=diversity,
            use_maxsum=False
        )
        
        # Filter by minimum score and format
        results = [
            {
                "phrase": phrase,
                "score": float(score)
            }
            for phrase, score in keywords
            if score >= min_score
        ]
        
        return results

    def extract_ngrams(self, text: str, max_ngram: int = 3) -> List[str]:
        """
        Extract n-gram candidates from text
        
        Args:
            text: Input text
            max_ngram: Maximum n-gram size
        
        Returns:
            List of candidate phrases
        """
        # Tokenize
        tokens = text.lower().split()
        
        candidates = []
        
        # Generate n-grams
        for n in range(1, max_ngram + 1):
            for i in range(len(tokens) - n + 1):
                ngram = ' '.join(tokens[i:i+n])
                
                # Filter out stopwords at start/end
                if not self._is_stopword(tokens[i]) and not self._is_stopword(tokens[i+n-1]):
                    candidates.append(ngram)
        
        return list(set(candidates))  # Remove duplicates

    @staticmethod
    def _is_stopword(token: str) -> bool:
        """Check if token is a stopword"""
        stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that',
            'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
        }
        return token.lower() in stopwords

    def calculate_mmr(
        self,
        document_embedding: np.ndarray,
        candidates_embeddings: List[np.ndarray],
        selected_indices: List[int],
        lambda_param: float = 0.7
    ) -> Tuple[int, float]:
        """
        Calculate Maximal Marginal Relevance for next candidate
        
        MMR = λ * Sim(candidate, document) - (1-λ) * max(Sim(candidate, selected))
        
        Args:
            document_embedding: Embedding of full document
            candidates_embeddings: List of candidate embeddings
            selected_indices: Indices of already selected candidates
            lambda_param: Balance between relevance (λ) and diversity (1-λ)
        
        Returns:
            Tuple of (best_candidate_index, mmr_score)
        """
        best_mmr = -np.inf
        best_idx = -1
        
        for i, candidate_emb in enumerate(candidates_embeddings):
            if i in selected_indices:
                continue
            
            # Relevance: similarity to document
            relevance = float(np.dot(candidate_emb, document_embedding) / 
                            (np.linalg.norm(candidate_emb) * np.linalg.norm(document_embedding)))
            
            # Diversity: penalize if similar to selected candidates
            max_similarity = 0.0
            if selected_indices:
                similarities = [
                    float(np.dot(candidate_emb, candidates_embeddings[j]) /
                          (np.linalg.norm(candidate_emb) * np.linalg.norm(candidates_embeddings[j])))
                    for j in selected_indices
                ]
                max_similarity = max(similarities)
            
            # MMR calculation
            mmr = lambda_param * relevance - (1 - lambda_param) * max_similarity
            
            if mmr > best_mmr:
                best_mmr = mmr
                best_idx = i
        
        return best_idx, best_mmr

    def extract_keyphrases_mmr(
        self,
        text: str,
        top_n: int = 10,
        lambda_param: float = 0.7
    ) -> List[Dict[str, float]]:
        """
        Extract keyphrases with manual MMR implementation
        
        Args:
            text: Input document text
            top_n: Number of keyphrases to extract
            lambda_param: MMR lambda parameter
        
        Returns:
            List of dicts with 'phrase' and 'score' keys
        """
        # Get document embedding
        doc_embedding = self.sentence_transformer.encode(text)
        
        # Extract candidate phrases
        candidates = self.extract_ngrams(text)
        
        # Get embeddings for all candidates
        candidate_embeddings = self.sentence_transformer.encode(candidates)
        
        # Select top_n using MMR
        selected_indices = []
        results = []
        
        for _ in range(min(top_n, len(candidates))):
            best_idx, mmr_score = self.calculate_mmr(
                doc_embedding,
                candidate_embeddings,
                selected_indices,
                lambda_param
            )
            
            if best_idx >= 0:
                selected_indices.append(best_idx)
                # Normalize MMR score to 0-1 range for consistency
                normalized_score = max(0.0, min(1.0, (mmr_score + 1) / 2))
                results.append({
                    "phrase": candidates[best_idx],
                    "score": normalized_score
                })
        
        return results

    def extract_batch(
        self,
        texts: List[str],
        top_n: int = 10,
        min_score: float = 0.3
    ) -> List[List[Dict[str, float]]]:
        """
        Extract keyphrases from multiple documents
        
        Args:
            texts: List of input texts
            top_n: Number of keyphrases per document
            min_score: Minimum score threshold
        
        Returns:
            List of keyphrase lists
        """
        results = []
        for text in texts:
            results.append(self.extract_keyphrases(text, top_n, min_score))
        return results
