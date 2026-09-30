"""
Document preprocessing and text normalization
"""
import re
from typing import Tuple, List
from bs4 import BeautifulSoup
import spacy


class DocumentPreprocessor:
    """Handles HTML/Markdown stripping and linguistic cleansing"""

    def __init__(self):
        """Initialize preprocessor with spaCy model"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Warning: spaCy model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None

    @staticmethod
    def extract_html_structure(html_content: str) -> Tuple[str, dict]:
        """
        Extract text from HTML while preserving structural information
        
        Returns:
            Tuple of (cleaned_text, structural_weights)
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        structural_weights = {
            "h1": [],
            "h2": [],
            "h3": [],
            "title": [],
            "body": []
        }
        
        # Extract headings with weight info
        for h1 in soup.find_all('h1'):
            structural_weights["h1"].append(h1.get_text(strip=True))
        
        for h2 in soup.find_all('h2'):
            structural_weights["h2"].append(h2.get_text(strip=True))
        
        for h3 in soup.find_all('h3'):
            structural_weights["h3"].append(h3.get_text(strip=True))
        
        # Extract title tag
        title = soup.find('title')
        if title:
            structural_weights["title"].append(title.get_text(strip=True))
        
        # Get all text
        text = soup.get_text(separator=' ', strip=True)
        
        return text, structural_weights

    @staticmethod
    def extract_markdown(markdown_content: str) -> Tuple[str, dict]:
        """
        Extract text from Markdown while preserving structural information
        
        Returns:
            Tuple of (cleaned_text, structural_weights)
        """
        structural_weights = {
            "h1": [],
            "h2": [],
            "h3": [],
            "title": [],
            "body": []
        }
        
        lines = markdown_content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            if line.startswith('# '):
                structural_weights["h1"].append(line[2:].strip())
            elif line.startswith('## '):
                structural_weights["h2"].append(line[3:].strip())
            elif line.startswith('### '):
                structural_weights["h3"].append(line[4:].strip())
            elif line.startswith('[') and line.endswith(')'):
                # Skip markdown links
                continue
            else:
                cleaned_lines.append(line)
        
        # Remove code blocks and inline code
        text = '\n'.join(cleaned_lines)
        text = re.sub(r'```[\s\S]*?```', '', text)  # Remove code blocks
        text = re.sub(r'`[^`]+`', '', text)  # Remove inline code
        text = re.sub(r'[*_]{1,2}([^*_]+)[*_]{1,2}', r'\1', text)  # Remove bold/italic
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)  # Extract link text
        
        return text, structural_weights

    @staticmethod
    def clean_stopwords(text: str) -> str:
        """Remove publishing-specific stopwords"""
        publishing_stopwords = {
            'share', 'subscribe', 'comment', 'click here', 'written by',
            'updated', 'published', 'author', 'editor', 'posted',
            'read more', 'continue reading', 'comments', 'likes',
            'follow us', 'get updates', 'newsletter'
        }
        
        # Remove stopwords (case-insensitive)
        for stopword in publishing_stopwords:
            text = re.sub(r'\b' + stopword + r'\b', '', text, flags=re.IGNORECASE)
        
        return text

    def lemmatize_text(self, text: str) -> str:
        """Lemmatize text using spaCy"""
        if self.nlp is None:
            return text
        
        doc = self.nlp(text)
        lemmatized = " ".join([token.lemma_ for token in doc if not token.is_punct])
        return lemmatized

    def preprocess_document(self, content: str, is_html: bool = False) -> Tuple[str, dict]:
        """
        Complete preprocessing pipeline
        
        Args:
            content: Raw HTML or Markdown content
            is_html: Whether content is HTML (default: False for Markdown)
        
        Returns:
            Tuple of (cleaned_text, structural_info)
        """
        # Extract structure
        if is_html:
            text, structure = self.extract_html_structure(content)
        else:
            text, structure = self.extract_markdown(content)
        
        # Clean stopwords
        text = self.clean_stopwords(text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Lemmatize
        text = self.lemmatize_text(text)
        
        return text, structure


def preprocess_batch(documents: List[str], is_html: bool = False) -> List[Tuple[str, dict]]:
    """Preprocess a batch of documents"""
    preprocessor = DocumentPreprocessor()
    results = []
    
    for doc in documents:
        cleaned_text, structure = preprocessor.preprocess_document(doc, is_html)
        results.append((cleaned_text, structure))
    
    return results
