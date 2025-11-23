import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import List, Dict, Tuple, Optional
import json
import re

# Lazy imports for ML models (only load when needed)
_sentence_transformer = None
_transformers_pipeline = None

def _get_sentence_transformer():
    """Lazy load SentenceTransformer"""
    global _sentence_transformer
    if _sentence_transformer is None:
        try:
            from sentence_transformers import SentenceTransformer
            _sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
        except ImportError:
            raise ImportError("sentence-transformers not installed. Install with: pip install sentence-transformers")
    return _sentence_transformer

def _get_classifier():
    """Lazy load zero-shot classifier"""
    global _transformers_pipeline
    if _transformers_pipeline is None:
        try:
            from transformers import pipeline
            _transformers_pipeline = pipeline("zero-shot-classification", 
                                             model="facebook/bart-large-mnli")
        except ImportError:
            raise ImportError("transformers not installed. Install with: pip install transformers")
    return _transformers_pipeline

class ClassificationService:
    def __init__(self):
        # Load spaCy model
        self.nlp = spacy.load("en_core_web_sm")
        
        # ML models will be loaded lazily when needed
        self.sentence_model = None
        self.classifier = None
        
        # Bloom taxonomy keywords
        self.bloom_keywords = {
            1: ['define', 'list', 'recall', 'name', 'identify', 'recognize', 'memorize', 'state', 'write', 'repeat'],
            2: ['explain', 'describe', 'summarize', 'interpret', 'classify', 'compare', 'contrast', 'discuss', 'distinguish', 'illustrate'],
            3: ['solve', 'implement', 'apply', 'calculate', 'demonstrate', 'execute', 'use', 'construct', 'operate', 'practice'],
            4: ['analyze', 'compare', 'examine', 'differentiate', 'investigate', 'categorize', 'decompose', 'infer', 'organize', 'structure'],
            5: ['evaluate', 'justify', 'critique', 'assess', 'judge', 'defend', 'support', 'conclude', 'recommend', 'validate'],
            6: ['design', 'create', 'develop', 'construct', 'formulate', 'invent', 'compose', 'generate', 'produce', 'build']
        }
        
        self.bloom_categories = {
            1: "Remembering",
            2: "Understanding", 
            3: "Applying",
            4: "Analyzing",
            5: "Evaluating",
            6: "Creating"
        }
    
    def classify_unit(self, question_text: str, course_code: str, syllabus_data: Dict) -> Tuple[Optional[int], float]:
        """Classify question to course unit using TF-IDF similarity"""
        if not syllabus_data or 'units' not in syllabus_data:
            return None, 0.0
        
        # Prepare corpus: question + unit texts
        corpus = [question_text]
        unit_texts = []
        
        for unit in syllabus_data['units']:
            unit_text = f"{unit['name']} {unit.get('topics', '')}"
            corpus.append(unit_text)
            unit_texts.append(unit_text)
        
        # TF-IDF vectorization
        vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        tfidf_matrix = vectorizer.fit_transform(corpus)
        
        # Calculate similarity between question and each unit
        similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])
        
        # Find best match
        max_similarity = float(np.max(similarities))
        best_unit_idx = int(np.argmax(similarities))
        
        if max_similarity > 0.3:  # Threshold for unit classification
            unit_id = syllabus_data['units'][best_unit_idx]['unit_id']
            return unit_id, max_similarity
        
        return None, max_similarity
    
    def classify_bloom_taxonomy(self, question_text: str) -> Tuple[Optional[int], Optional[str], float]:
        """Classify question to Bloom taxonomy level"""
        # Strategy 1: Keyword matching
        keyword_score = self._classify_by_keywords(question_text)
        
        # Strategy 2: Zero-shot classification
        zero_shot_score = self._classify_by_zero_shot(question_text)
        
        # Combine scores with weights
        combined_score = 0.7 * keyword_score + 0.3 * zero_shot_score
        
        # Find best match
        best_level = max(combined_score.keys(), key=lambda k: combined_score[k])
        confidence = combined_score[best_level]
        
        if confidence > 0.3:  # Threshold for classification
            return best_level, self.bloom_categories[best_level], confidence
        
        return None, None, confidence
    
    def _classify_by_keywords(self, text: str) -> Dict[int, float]:
        """Classify using keyword matching"""
        text_lower = text.lower()
        scores = {}
        
        for level, keywords in self.bloom_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    score += 1
            scores[level] = score / len(keywords)
        
        return scores
    
    def _classify_by_zero_shot(self, text: str) -> Dict[int, float]:
        """Classify using zero-shot classification"""
        labels = [
            "remembering", "understanding", "applying", 
            "analyzing", "evaluating", "creating"
        ]
        
        try:
            if self.classifier is None:
                self.classifier = _get_classifier()
            result = self.classifier(text, labels)
            scores = {}
            for i, label in enumerate(result['labels']):
                level = i + 1
                scores[level] = result['scores'][i]
            return scores
        except (ImportError, Exception) as e:
            # Fallback to equal scores if classification fails
            return {i: 0.0 for i in range(1, 7)}
    
    def estimate_difficulty(self, question: Dict) -> str:
        """Estimate question difficulty based on multiple factors"""
        score = 0
        
        # Factor 1: Marks (higher marks = more difficult)
        if question.get('marks'):
            if question['marks'] <= 5:
                score += 1
            elif question['marks'] <= 10:
                score += 2
            else:
                score += 3
        
        # Factor 2: Bloom level (higher level = more difficult)
        if question.get('bloom_level'):
            score += question['bloom_level']
        
        # Factor 3: Word count (more words = more complex)
        word_count = len(question['question_text'].split())
        if word_count > 50:
            score += 2
        elif word_count > 20:
            score += 1
        
        # Factor 4: Sub-parts (more parts = more difficult)
        if question.get('has_subparts'):
            score += 2
        
        # Factor 5: Mathematical notation (presence = more difficult)
        if question.get('has_mathematical_notation'):
            score += 1
        
        # Determine difficulty level
        if score <= 3:
            return "Easy"
        elif score <= 6:
            return "Medium"
        else:
            return "Hard"
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """Generate sentence embedding for semantic search"""
        if self.sentence_model is None:
            self.sentence_model = _get_sentence_transformer()
        return self.sentence_model.encode(text)
    
    def find_similar_questions(self, question_text: str, course_code: str, 
                             existing_embeddings: List[np.ndarray], 
                             threshold: float = 0.85) -> List[Tuple[int, float]]:
        """Find similar questions using cosine similarity"""
        # Generate embedding for new question
        new_embedding = self.generate_embedding(question_text)
        
        # Calculate similarities
        similarities = []
        for i, existing_embedding in enumerate(existing_embeddings):
            similarity = cosine_similarity([new_embedding], [existing_embedding])[0][0]
            if similarity > threshold:
                similarities.append((i, similarity))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities
    
    def extract_question_features(self, question_text: str) -> Dict:
        """Extract features from question text"""
        doc = self.nlp(question_text)
        
        features = {
            "word_count": len(question_text.split()),
            "sentence_count": len(list(doc.sents)),
            "has_question_words": any(token.text.lower() in ['what', 'how', 'why', 'when', 'where', 'which', 'who'] 
                                   for token in doc),
            "has_imperative": any(token.text.lower() in ['explain', 'describe', 'solve', 'calculate', 'derive', 'prove'] 
                                for token in doc),
            "has_mathematical": bool(re.search(r'[∑∏∫∂∇αβγδεζηθικλμνξοπρστυφχψω²³⁴⁵⁶⁷⁸⁹⁰¹₀₁₂₃₄₅₆₇₈₉√∛∜∞±∓×÷≤≥≠≈≡∈∉⊂⊃⊆⊇]', question_text)),
            "complexity_score": self._calculate_complexity_score(question_text)
        }
        
        return features
    
    def _calculate_complexity_score(self, text: str) -> float:
        """Calculate text complexity score"""
        doc = self.nlp(text)
        
        # Factors: sentence length, word complexity, technical terms
        avg_sentence_length = len(text.split()) / max(len(list(doc.sents)), 1)
        
        # Count technical/scientific words (simplified heuristic)
        technical_words = ['algorithm', 'function', 'variable', 'parameter', 'method', 'class', 'object', 
                          'database', 'query', 'index', 'normalization', 'optimization', 'implementation']
        technical_count = sum(1 for word in text.lower().split() if word in technical_words)
        
        complexity = (avg_sentence_length * 0.4) + (technical_count * 0.6)
        return min(complexity, 10.0)  # Normalize to 0-10 scale
