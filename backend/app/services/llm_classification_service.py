"""
LLM-Based Classification Service
Uses OpenAI API to classify questions into units and generate topic tags
"""
import json
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.course import CourseUnit

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class LLMClassificationService:
    """Service to classify questions using OpenAI LLM"""
    
    def __init__(self):
        if not OPENAI_AVAILABLE:
            raise ImportError("openai package is required. Install with: pip install openai")
        
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set in environment variables")
        
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
    
    def classify_questions_with_llm(
        self, 
        questions: List[Dict], 
        course_code: str,
        db: Session
    ) -> List[Dict]:
        """
        Classify questions to units and generate topic tags using LLM
        
        Args:
            questions: List of extracted questions
            course_code: Course code to load syllabus for
            db: Database session
        
        Returns:
            List of questions with added classification data:
            - unit_id: int
            - unit_name: str
            - topic_tags: List[str]
            - classification_confidence: float
        """
        # Load syllabus (units + topics) from database
        syllabus_data = self._load_syllabus(course_code, db)
        
        if not syllabus_data or not syllabus_data.get('units'):
            # If no syllabus, return questions without classification
            for q in questions:
                q['unit_id'] = None
                q['unit_name'] = None
                q['topic_tags'] = []
                q['classification_confidence'] = 0.0
            return questions
        
        # Prepare prompt with syllabus and questions
        prompt = self._prepare_classification_prompt(syllabus_data, questions)
        
        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at classifying academic questions into course units and topics based on syllabus content."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.1  # Low temperature for consistent classification
            )
            
            # Parse response
            response_text = response.choices[0].message.content
            classifications = self._parse_classification_response(response_text)
            
            # Apply classifications to questions
            classified_questions = self._apply_classifications(questions, classifications, syllabus_data)
            
            return classified_questions
            
        except Exception as e:
            raise Exception(f"LLM classification failed: {e}")
    
    def _load_syllabus(self, course_code: str, db: Session) -> Dict:
        """Load course syllabus (units and topics) from PostgreSQL"""
        # Get course units
        units = db.query(CourseUnit).filter(
            CourseUnit.course_code == course_code.upper(),
            CourseUnit.is_active == True
        ).order_by(CourseUnit.unit_number).all()
        
        if not units:
            return None
        
        # Parse units and topics
        syllabus_units = []
        for unit in units:
            # Parse topics from JSON string
            topics = []
            if unit.topics:
                try:
                    topics = json.loads(unit.topics) if isinstance(unit.topics, str) else unit.topics
                    if not isinstance(topics, list):
                        topics = [topics] if topics else []
                except (json.JSONDecodeError, TypeError):
                    # If not JSON, try to split by comma or newline
                    if isinstance(unit.topics, str):
                        topics = [t.strip() for t in unit.topics.replace('\n', ',').split(',') if t.strip()]
                    else:
                        topics = []
            
            syllabus_units.append({
                'unit_id': unit.unit_id,
                'unit_number': unit.unit_number,
                'unit_name': unit.unit_name,
                'topics': topics
            })
        
        return {
            'course_code': course_code,
            'units': syllabus_units
        }
    
    def _prepare_classification_prompt(self, syllabus_data: Dict, questions: List[Dict]) -> str:
        """Prepare prompt for classification"""
        # Format syllabus
        syllabus_text = "Syllabus:\n"
        for unit in syllabus_data['units']:
            syllabus_text += f"\nUnit {unit['unit_number']} (ID: {unit['unit_id']}): {unit['unit_name']}\n"
            if unit.get('topics'):
                syllabus_text += "Topics: " + ", ".join(unit['topics']) + "\n"
        
        # Format questions
        questions_text = "Questions to classify:\n"
        for i, q in enumerate(questions):
            questions_text += f"\nQuestion {i+1}:\n"
            questions_text += f"Number: {q.get('question_number', 'N/A')}\n"
            questions_text += f"Text: {q.get('question_text', '')[:500]}...\n"  # Limit text length
            questions_text += f"Marks: {q.get('marks', 'N/A')}\n"
        
        prompt = f"""Given the syllabus and questions below, classify each question into the appropriate unit and assign relevant topic tags.

{syllabus_text}

{questions_text}

For each question, provide:
- unit_id: The ID of the unit this question belongs to (must match one of the unit IDs from syllabus)
- unit_name: The name of the unit
- topic_tags: Array of relevant topics from the unit's topics list that match this question
- confidence: Your confidence in this classification (0.0 to 1.0)

Return the classification in this JSON format:
{{
  "classifications": [
    {{
      "question_index": 0,
      "unit_id": 1,
      "unit_name": "Unit Name",
      "topic_tags": ["Topic 1", "Topic 2"],
      "confidence": 0.85
    }}
  ]
}}

Important:
1. Match questions to units based on content similarity
2. Only include topics that are actually listed in the unit's topics
3. If a question doesn't clearly match any unit, set unit_id to null and confidence to a low value
4. Topic tags should be exact matches from the unit's topics list
5. Return classifications for ALL questions in the same order"""
        
        return prompt
    
    def _parse_classification_response(self, response_text: str) -> Dict:
        """Parse LLM classification response"""
        try:
            # Clean response text
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
            
            # Extract classifications
            if isinstance(data, dict) and "classifications" in data:
                return {c["question_index"]: c for c in data["classifications"]}
            elif isinstance(data, list):
                return {i: c for i, c in enumerate(data)}
            else:
                raise ValueError("Invalid response format")
                
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse classification response as JSON: {e}")
        except Exception as e:
            raise Exception(f"Error processing classification response: {e}")
    
    def _apply_classifications(
        self, 
        questions: List[Dict], 
        classifications: Dict,
        syllabus_data: Dict
    ) -> List[Dict]:
        """Apply classifications to questions"""
        # Create unit lookup
        unit_lookup = {u['unit_id']: u for u in syllabus_data['units']}
        
        classified_questions = []
        
        for i, question in enumerate(questions):
            classification = classifications.get(i, {})
            
            unit_id = classification.get('unit_id')
            unit_name = None
            topic_tags = classification.get('topic_tags', [])
            confidence = classification.get('confidence', 0.0)
            
            # Validate unit_id exists in syllabus
            if unit_id and unit_id in unit_lookup:
                unit_name = unit_lookup[unit_id]['unit_name']
                # Validate topic tags are from the unit's topics
                valid_topics = unit_lookup[unit_id].get('topics', [])
                topic_tags = [tag for tag in topic_tags if tag in valid_topics]
            else:
                unit_id = None
                topic_tags = []
                confidence = 0.0
            
            # Add classification data to question
            question['unit_id'] = unit_id
            question['unit_name'] = unit_name
            question['topic_tags'] = topic_tags
            question['classification_confidence'] = float(confidence) if confidence else 0.0
            
            classified_questions.append(question)
        
        return classified_questions

