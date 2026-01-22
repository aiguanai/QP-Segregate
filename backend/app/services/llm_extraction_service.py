"""
LLM-Based Question Extraction Service
Uses OpenAI API to extract questions, marks, and Bloom's taxonomy from question papers
"""
import json
import re
from typing import List, Dict, Optional
from app.core.config import settings

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class LLMExtractionService:
    """Service to extract questions using OpenAI LLM"""
    
    def __init__(self):
        if not OPENAI_AVAILABLE:
            raise ImportError("openai package is required. Install with: pip install openai")
        
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set in environment variables")
        
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
    
    def extract_questions_with_llm(self, file_content: Dict) -> List[Dict]:
        """
        Extract questions from file content using LLM
        
        Args:
            file_content: Result from FileConversionService.prepare_for_llm()
        
        Returns:
            List of question dictionaries with:
            - question_number: str (e.g., "1", "2.a", "2.b")
            - question_text: str
            - marks: int
            - bloom_taxonomy_level: int (1-6)
            - bloom_category: str
            - has_diagram: bool
        """
        prompt = self._prepare_extraction_prompt()
        
        # Prepare messages for OpenAI API
        messages = [
            {
                "role": "system",
                "content": "You are an expert at extracting questions from academic question papers. Extract all questions including subparts as separate entries."
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt}
                ] + file_content.get("content", [])
            }
        ]
        
        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.1  # Low temperature for consistent extraction
            )
            
            # Parse response
            response_text = response.choices[0].message.content
            questions = self._parse_llm_response(response_text)
            
            # Handle subparts - ensure they're separate records
            processed_questions = self._handle_subparts(questions)
            
            return processed_questions
            
        except Exception as e:
            raise Exception(f"LLM extraction failed: {e}")
    
    def _prepare_extraction_prompt(self) -> str:
        """Prepare prompt for question extraction"""
        return """Extract all questions from this question paper. For each question, provide the following information in JSON format:

{
  "questions": [
    {
      "question_number": "1",
      "question_text": "Full question text including any diagrams or tables described in text",
      "marks": 10,
      "bloom_taxonomy_level": 3,
      "bloom_category": "Applying",
      "has_diagram": false
    }
  ]
}

Important instructions:
1. Extract ALL questions including subparts (2.a, 2.b, 3(i), 3(ii), etc.) as separate entries
2. For questions with diagrams or tables, describe them in the question_text field
3. Extract marks from the question (look for patterns like [10 marks], (10M), 10 marks, etc.)
4. Determine Bloom's taxonomy level (1=Remembering, 2=Understanding, 3=Applying, 4=Analyzing, 5=Evaluating, 6=Creating)
5. Set has_diagram to true if the question contains diagrams, figures, or tables
6. If marks are not found, set marks to null
7. If Bloom's level cannot be determined, use your best judgment based on question keywords

Return ONLY valid JSON, no additional text."""
    
    def _parse_llm_response(self, response_text: str) -> List[Dict]:
        """Parse LLM JSON response"""
        try:
            # Clean response text (remove markdown code blocks if present)
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            # Parse JSON
            data = json.loads(response_text)
            
            # Extract questions array
            if isinstance(data, dict) and "questions" in data:
                questions = data["questions"]
            elif isinstance(data, list):
                questions = data
            else:
                raise ValueError("Invalid response format")
            
            # Validate and clean each question
            validated_questions = []
            for q in questions:
                validated = self._validate_question(q)
                if validated:
                    validated_questions.append(validated)
            
            return validated_questions
            
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse LLM response as JSON: {e}")
        except Exception as e:
            raise Exception(f"Error processing LLM response: {e}")
    
    def _validate_question(self, question: Dict) -> Optional[Dict]:
        """Validate and clean question data"""
        # Required fields
        if "question_number" not in question or "question_text" not in question:
            return None
        
        # Clean and validate
        validated = {
            "question_number": str(question["question_number"]).strip(),
            "question_text": str(question["question_text"]).strip(),
            "marks": self._parse_marks(question.get("marks")),
            "bloom_taxonomy_level": self._parse_bloom_level(question.get("bloom_taxonomy_level")),
            "bloom_category": self._parse_bloom_category(question.get("bloom_category"), question.get("bloom_taxonomy_level")),
            "has_diagram": bool(question.get("has_diagram", False))
        }
        
        # Ensure question_text is not empty
        if not validated["question_text"]:
            return None
        
        return validated
    
    def _parse_marks(self, marks) -> Optional[int]:
        """Parse marks value"""
        if marks is None:
            return None
        
        try:
            marks_int = int(marks)
            return marks_int if marks_int > 0 else None
        except (ValueError, TypeError):
            return None
    
    def _parse_bloom_level(self, level) -> Optional[int]:
        """Parse Bloom's taxonomy level"""
        if level is None:
            return None
        
        try:
            level_int = int(level)
            if 1 <= level_int <= 6:
                return level_int
        except (ValueError, TypeError):
            pass
        
        return None
    
    def _parse_bloom_category(self, category: Optional[str], level: Optional[int]) -> Optional[str]:
        """Parse Bloom's category"""
        if category:
            # Map common variations
            category_lower = category.lower()
            bloom_map = {
                "remembering": "Remembering",
                "remember": "Remembering",
                "understanding": "Understanding",
                "understand": "Understanding",
                "applying": "Applying",
                "apply": "Applying",
                "analyzing": "Analyzing",
                "analyze": "Analyzing",
                "evaluating": "Evaluating",
                "evaluate": "Evaluating",
                "creating": "Creating",
                "create": "Creating"
            }
            if category_lower in bloom_map:
                return bloom_map[category_lower]
        
        # Fallback to level-based mapping
        if level:
            level_to_category = {
                1: "Remembering",
                2: "Understanding",
                3: "Applying",
                4: "Analyzing",
                5: "Evaluating",
                6: "Creating"
            }
            return level_to_category.get(level)
        
        return None
    
    def _handle_subparts(self, questions: List[Dict]) -> List[Dict]:
        """
        Ensure subparts are handled as separate question records
        Subparts like 2.a, 2.b should already be separate entries from LLM
        This method just ensures proper formatting
        """
        processed = []
        
        for question in questions:
            # Check if this is a subpart (contains . or ( or letters after numbers)
            question_num = question["question_number"]
            
            # Ensure subparts are marked
            if re.search(r'[a-z]|\(|\)', question_num.lower()):
                question["has_subparts"] = True
                # Try to extract parent question number
                parent_match = re.match(r'^(\d+)', question_num)
                if parent_match:
                    question["parent_question_number"] = parent_match.group(1)
            else:
                question["has_subparts"] = False
            
            processed.append(question)
        
        return processed

