"""
Enhanced NLP Classification Service - Aligned with Proposed System
Implements the proposed AI-Based Mapping using machine learning Text Classification
"""

import spacy
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from typing import List, Dict, Tuple, Optional
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer
from transformers import pipeline
import json

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
except:
    pass

class EnhancedClassificationService:
    """
    Enhanced NLP Classification Service
    Implements the proposed AI-Based Mapping using machine learning Text Classification
    """
    
    def __init__(self):
        # Load spaCy model for advanced NLP
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("spaCy model not found. Please install: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        # Initialize NLTK components
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        
        # Initialize advanced classification pipeline
        self.classifier = pipeline(
            "text-classification",
            model="distilbert-base-uncased-finetuned-sst-2-english",
            return_all_scores=True
        )
        
        # Zero-shot classification for better accuracy
        self.zero_shot_classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli"
        )
        
        # Bloom's Taxonomy mapping (as proposed)
        self.bloom_levels = {
            1: "Remembering",
            2: "Understanding", 
            3: "Applying",
            4: "Analyzing",
            5: "Evaluating",
            6: "Creating"
        }
        
        # Enhanced keyword patterns for better classification
        self.bloom_keywords = {
            1: ['define', 'list', 'recall', 'name', 'identify', 'recognize', 'memorize', 'state', 'write', 'repeat', 'what is', 'who is'],
            2: ['explain', 'describe', 'summarize', 'interpret', 'classify', 'compare', 'contrast', 'discuss', 'distinguish', 'illustrate', 'how does', 'why does'],
            3: ['solve', 'implement', 'apply', 'calculate', 'demonstrate', 'execute', 'use', 'construct', 'operate', 'practice', 'compute', 'derive'],
            4: ['analyze', 'compare', 'examine', 'differentiate', 'investigate', 'categorize', 'decompose', 'infer', 'organize', 'structure', 'break down'],
            5: ['evaluate', 'justify', 'critique', 'assess', 'judge', 'defend', 'support', 'conclude', 'recommend', 'validate', 'argue', 'defend'],
            6: ['design', 'create', 'develop', 'construct', 'formulate', 'invent', 'compose', 'generate', 'produce', 'build', 'synthesize', 'integrate']
        }
    
    def segregate_questions(self, ocr_text: str) -> List[Dict]:
        """
        Segregate text into distinct, individual questions
        This is the core NLP model for automatic segregation as proposed
        """
        # Split text into potential questions using multiple strategies
        questions = []
        
        # Strategy 1: Pattern-based segmentation
        question_patterns = [
            r'Q\d+[\.\)]\s*',  # Q1. Q2) etc.
            r'\(\d+\)\s*',     # (1) (2) etc.
            r'^\d+[\.\)]\s*',  # 1. 2) etc.
            r'Question\s+\d+[\.\)]\s*',  # Question 1. etc.
        ]
        
        # Split by question patterns
        segments = []
        current_segment = ""
        
        lines = ocr_text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if line starts a new question
            is_question_start = any(re.match(pattern, line, re.IGNORECASE) for pattern in question_patterns)
            
            if is_question_start and current_segment:
                segments.append(current_segment.strip())
                current_segment = line
            else:
                current_segment += " " + line if current_segment else line
        
        # Add the last segment
        if current_segment:
            segments.append(current_segment.strip())
        
        # Process each segment as a potential question
        for i, segment in enumerate(segments):
            if self._is_valid_question(segment):
                question = {
                    'question_number': self._extract_question_number(segment),
                    'question_text': self._clean_question_text(segment),
                    'confidence': self._calculate_question_confidence(segment),
                    'page_number': self._extract_page_number(segment),
                    'marks': self._extract_marks(segment)
                }
                questions.append(question)
        
        return questions
    
    def classify_question_to_unit(self, question_text: str, syllabus_data: Dict) -> Tuple[Optional[int], float]:
        """
        AI-Based Mapping: Machine learning Text Classification model 
        automatically maps each segregated question to the correct Unit within a Subject
        """
        if not syllabus_data or 'units' not in syllabus_data:
            return None, 0.0
        
        # Prepare corpus: question + unit texts
        corpus = [question_text]
        unit_texts = []
        unit_ids = []
        
        for unit in syllabus_data['units']:
            unit_text = f"{unit['name']} {unit.get('topics', '')}"
            corpus.append(unit_text)
            unit_texts.append(unit_text)
            unit_ids.append(unit['unit_id'])
        
        # Enhanced TF-IDF vectorization with better preprocessing
        vectorizer = TfidfVectorizer(
            stop_words='english', 
            max_features=2000,
            ngram_range=(1, 3),  # Include bigrams and trigrams
            min_df=1,
            max_df=0.8
        )
        
        try:
            tfidf_matrix = vectorizer.fit_transform(corpus)
            
            # Calculate similarity between question and each unit
            similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])
            
            # Find best match
            max_similarity = float(np.max(similarities))
            best_unit_idx = int(np.argmax(similarities))
            
            # Enhanced threshold with confidence scoring
            threshold = 0.3
            if max_similarity > threshold:
                unit_id = unit_ids[best_unit_idx]
                return unit_id, max_similarity
            
            return None, max_similarity
            
        except Exception as e:
            print(f"Classification error: {e}")
            return None, 0.0
    
    def classify_bloom_taxonomy(self, question_text: str) -> Tuple[Optional[int], Optional[str], float]:
        """
        Enhanced Bloom Taxonomy classification using multiple strategies
        """
        # Strategy 1: Keyword-based classification
        keyword_scores = self._classify_by_keywords(question_text)
        
        # Strategy 2: Zero-shot classification
        zero_shot_scores = self._classify_by_zero_shot(question_text)
        
        # Strategy 3: Pattern-based classification
        pattern_scores = self._classify_by_patterns(question_text)
        
        # Combine all strategies with weights
        combined_scores = {}
        for level in range(1, 7):
            combined_scores[level] = (
                0.4 * keyword_scores.get(level, 0) +
                0.4 * zero_shot_scores.get(level, 0) +
                0.2 * pattern_scores.get(level, 0)
            )
        
        # Find best match
        best_level = max(combined_scores.keys(), key=lambda k: combined_scores[k])
        confidence = combined_scores[best_level]
        
        if confidence > 0.3:  # Threshold for classification
            return best_level, self.bloom_levels[best_level], confidence
        
        return None, None, confidence
    
    def _classify_by_keywords(self, text: str) -> Dict[int, float]:
        """Enhanced keyword-based classification"""
        text_lower = text.lower()
        scores = {}
        
        for level, keywords in self.bloom_keywords.items():
            score = 0
            total_keywords = len(keywords)
            
            for keyword in keywords:
                if keyword in text_lower:
                    # Weight by keyword importance
                    if keyword in ['define', 'explain', 'solve', 'analyze', 'evaluate', 'design']:
                        score += 2  # Primary action words
                    else:
                        score += 1  # Secondary keywords
            
            scores[level] = score / (total_keywords * 2)  # Normalize
        
        return scores
    
    def _classify_by_zero_shot(self, text: str) -> Dict[int, float]:
        """Zero-shot classification using BART model"""
        labels = [
            "remembering facts and information",
            "understanding concepts and ideas", 
            "applying knowledge to solve problems",
            "analyzing information and relationships",
            "evaluating arguments and evidence",
            "creating new solutions and designs"
        ]
        
        try:
            result = self.zero_shot_classifier(text, labels)
            scores = {}
            for i, (label, score) in enumerate(zip(result['labels'], result['scores'])):
                scores[i + 1] = score
            return scores
        except Exception:
            return {i: 0.0 for i in range(1, 7)}
    
    def _classify_by_patterns(self, text: str) -> Dict[int, float]:
        """Pattern-based classification using linguistic patterns"""
        scores = {i: 0.0 for i in range(1, 7)}
        
        # Pattern matching for different Bloom levels
        patterns = {
            1: [r'\b(what|who|when|where|which)\b', r'\bdefine\b', r'\blist\b'],
            2: [r'\b(explain|describe|how)\b', r'\bcompare\b', r'\bcontrast\b'],
            3: [r'\b(solve|calculate|compute|derive)\b', r'\bapply\b', r'\buse\b'],
            4: [r'\b(analyze|examine|investigate)\b', r'\bbreak down\b', r'\bdecompose\b'],
            5: [r'\b(evaluate|assess|judge|critique)\b', r'\bjustify\b', r'\bdefend\b'],
            6: [r'\b(design|create|develop|construct)\b', r'\bformulate\b', r'\bsynthesize\b']
        }
        
        for level, level_patterns in patterns.items():
            for pattern in level_patterns:
                matches = len(re.findall(pattern, text, re.IGNORECASE))
                scores[level] += matches * 0.1
        
        return scores
    
    def _is_valid_question(self, text: str) -> bool:
        """Determine if text segment is a valid question"""
        if len(text.strip()) < 10:  # Too short
            return False
        
        # Check for question indicators
        question_indicators = [
            r'\?',  # Question mark
            r'\b(what|how|why|when|where|which|who)\b',  # Question words
            r'\b(explain|describe|solve|calculate|derive|prove)\b',  # Action words
            r'\b(define|list|compare|analyze|evaluate|design)\b'  # Bloom taxonomy words
        ]
        
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in question_indicators)
    
    def _extract_question_number(self, text: str) -> str:
        """Extract question number from text"""
        patterns = [
            r'Q(\d+)[\.\)]',
            r'\((\d+)\)',
            r'^(\d+)[\.\)]',
            r'Question\s+(\d+)[\.\)]'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return "1"  # Default
    
    def _clean_question_text(self, text: str) -> str:
        """Clean and normalize question text"""
        # Remove question number prefix
        text = re.sub(r'^(Q\d+[\.\)]|\(\d+\)|^\d+[\.\)]|Question\s+\d+[\.\)])\s*', '', text, flags=re.IGNORECASE)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _calculate_question_confidence(self, text: str) -> float:
        """Calculate confidence score for question validity"""
        confidence = 0.0
        
        # Length factor
        if 20 <= len(text) <= 500:
            confidence += 0.3
        
        # Question mark presence
        if '?' in text:
            confidence += 0.2
        
        # Question words presence
        question_words = ['what', 'how', 'why', 'when', 'where', 'which', 'who']
        if any(word in text.lower() for word in question_words):
            confidence += 0.2
        
        # Action words presence
        action_words = ['explain', 'describe', 'solve', 'calculate', 'derive', 'prove']
        if any(word in text.lower() for word in action_words):
            confidence += 0.2
        
        # Mathematical content
        if re.search(r'[∑∏∫∂∇αβγδεζηθικλμνξοπρστυφχψω²³⁴⁵⁶⁷⁸⁹⁰¹₀₁₂₃₄₅₆₇₈₉√∛∜∞±∓×÷≤≥≠≈≡∈∉⊂⊃⊆⊇]', text):
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _extract_page_number(self, text: str) -> Optional[int]:
        """Extract page number if present"""
        # Look for page indicators
        page_patterns = [
            r'page\s+(\d+)',
            r'p\.\s*(\d+)',
            r'pg\.\s*(\d+)'
        ]
        
        for pattern in page_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        return None
    
    def _extract_marks(self, text: str) -> Optional[int]:
        """Extract marks if present"""
        # Look for marks indicators
        marks_patterns = [
            r'(\d+)\s*marks?',
            r'(\d+)\s*points?',
            r'\[(\d+)\]',
            r'\((\d+)\)'
        ]
        
        for pattern in marks_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        return None
    
    def generate_ai_tag(self, question_text: str, unit_name: str = None) -> str:
        """
        Generate AI tag for question as specified in proposed schema
        Combines unit classification with Bloom taxonomy
        """
        # Get Bloom classification
        bloom_level, bloom_category, bloom_confidence = self.classify_bloom_taxonomy(question_text)
        
        # Create AI tag
        tag_parts = []
        
        if unit_name:
            tag_parts.append(f"Unit:{unit_name}")
        
        if bloom_category:
            tag_parts.append(f"Bloom:{bloom_category}")
        
        # Add confidence indicator
        if bloom_confidence > 0.8:
            tag_parts.append("HighConfidence")
        elif bloom_confidence > 0.5:
            tag_parts.append("MediumConfidence")
        else:
            tag_parts.append("LowConfidence")
        
        return "|".join(tag_parts)

# Global enhanced classification service instance
enhanced_classification_service = EnhancedClassificationService()
