"""
Multi-label classification for macro-categories using DistilRoBERTa
"""
from typing import List, Dict, Tuple
import numpy as np
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch


class MultiLabelClassifier:
    """
    Fine-tuned BERT-based multi-label classifier for predefined taxonomy categories.
    Uses Binary Cross-Entropy loss with dynamic thresholding per class.
    """

    def __init__(self, model_name: str = "distilroberta-base", num_labels: int = 20):
        """
        Initialize the multi-label classifier
        
        Args:
            model_name: Transformer model identifier
            num_labels: Number of categories to classify
        """
        self.model_name = model_name
        self.num_labels = num_labels
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Initialize model (in production, use fine-tuned model)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_name, 
            num_labels=num_labels
        ).to(self.device)
        
        # Default category names (should be loaded from database in production)
        self.categories = [
            "Technology", "Cloud Computing", "DevOps", "Machine Learning",
            "Data Science", "Web Development", "Mobile Development", "Security",
            "Database", "API Design", "Performance", "Architecture",
            "Testing", "DevOps", "Kubernetes", "Docker",
            "Python", "JavaScript", "TypeScript", "Go"
        ][:num_labels]
        
        # Dynamic thresholds per class (calibrated from validation set)
        self.class_thresholds = {cat: 0.5 for cat in self.categories}

    def predict(self, text: str, top_k: int = None) -> List[Dict[str, float]]:
        """
        Predict category probabilities for input text
        
        Args:
            text: Input text to classify
            top_k: Return only top-k predictions (None for all)
        
        Returns:
            List of dicts with 'category' and 'score' keys
        """
        # Tokenize and truncate
        inputs = self.tokenizer(
            text,
            max_length=512,
            truncation=True,
            return_tensors="pt"
        ).to(self.device)
        
        # Get predictions
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits[0]
            probabilities = torch.sigmoid(logits).cpu().numpy()
        
        # Apply dynamic thresholds
        results = []
        for category, threshold in self.class_thresholds.items():
            idx = self.categories.index(category)
            score = float(probabilities[idx])
            
            if score >= threshold:
                results.append({
                    "category": category,
                    "score": score
                })
        
        # Sort by score and limit to top_k
        results = sorted(results, key=lambda x: x["score"], reverse=True)
        if top_k:
            results = results[:top_k]
        
        return results

    def predict_batch(self, texts: List[str], top_k: int = None) -> List[List[Dict[str, float]]]:
        """
        Predict categories for a batch of texts
        
        Args:
            texts: List of input texts
            top_k: Return only top-k predictions per text
        
        Returns:
            List of prediction lists
        """
        results = []
        for text in texts:
            results.append(self.predict(text, top_k))
        return results

    def set_class_threshold(self, category: str, threshold: float):
        """
        Set the decision threshold for a specific category
        
        Args:
            category: Category name
            threshold: Threshold value (0.0 to 1.0)
        """
        if category in self.class_thresholds:
            self.class_thresholds[category] = threshold

    def calibrate_thresholds(self, texts: List[str], ground_truth: List[List[str]]):
        """
        Calibrate thresholds based on validation set using F1-score optimization
        
        Args:
            texts: List of validation texts
            ground_truth: List of ground truth category lists
        """
        # Get predictions for all texts
        predictions_all = []
        for text in texts:
            inputs = self.tokenizer(
                text,
                max_length=512,
                truncation=True,
                return_tensors="pt"
            ).to(self.device)
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits[0]
                probabilities = torch.sigmoid(logits).cpu().numpy()
            predictions_all.append(probabilities)
        
        # For each category, find optimal threshold
        for idx, category in enumerate(self.categories):
            best_threshold = 0.5
            best_f1 = 0.0
            
            # Try different thresholds
            for threshold in np.arange(0.1, 0.95, 0.05):
                tp = fp = fn = 0
                
                for pred_idx, ground_truth_cats in enumerate(ground_truth):
                    pred = 1 if predictions_all[pred_idx][idx] >= threshold else 0
                    true = 1 if category in ground_truth_cats else 0
                    
                    if pred == 1 and true == 1:
                        tp += 1
                    elif pred == 1 and true == 0:
                        fp += 1
                    elif pred == 0 and true == 1:
                        fn += 1
                
                # Calculate F1
                precision = tp / (tp + fp) if (tp + fp) > 0 else 0
                recall = tp / (tp + fn) if (tp + fn) > 0 else 0
                f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
                
                if f1 > best_f1:
                    best_f1 = f1
                    best_threshold = threshold
            
            self.class_thresholds[category] = best_threshold
