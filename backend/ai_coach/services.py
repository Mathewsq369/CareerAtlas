import requests
import json
import os
from django.conf import settings
from django.core.cache import cache
from assessments.models import AssessmentResult
from recommendations.models import LearningStyle

class AICoachService:
    def __init__(self, student):
        self.student = student
        self.assessment_result = AssessmentResult.objects.get(student=student)
        self.personality_type = self.assessment_result.personality_type
        
    def get_learning_style_recommendation(self):
        """Determine learning style based on personality"""
        # MBTI to learning style mapping
        learning_style_map = {
            'INTJ': 'reading',    # Prefer structured, theoretical learning
            'INTP': 'reading',    # Enjoy independent research
            'ENTJ': 'visual',     # Like big picture and diagrams
            'ENTP': 'kinesthetic',# Learn by doing and experimenting
            'INFJ': 'reading',    # Prefer meaningful, conceptual learning
            'INFP': 'reading',    # Enjoy creative and independent study
            'ENFJ': 'auditory',   # Learn well through discussion
            'ENFP': 'kinesthetic',# Prefer interactive learning
            'ISTJ': 'reading',    # Like structured, sequential learning
            'ISFJ': 'reading',    # Prefer practical, hands-on with structure
            'ESTJ': 'visual',     # Like organized, factual presentations
            'ESFJ': 'auditory',   # Learn well in social settings
            'ISTP': 'kinesthetic',# Prefer learning through hands-on experience
            'ISFP': 'kinesthetic',# Learn by doing and experiencing
            'ESTP': 'kinesthetic',# Prefer active, practical learning
            'ESFP': 'kinesthetic',# Learn through interaction and experience
        }
        
        recommended_style = learning_style_map.get(
            self.personality_type.mbti_type, 
            'reading'  # Default fallback
        )
        
        return LearningStyle.objects.get(name=recommended_style)
    
    def generate_ai_response(self, message, conversation_history=None):
        """
        Generate AI response using free API (Hugging Face Inference API)
        Fallback to rule-based if API fails
        """
        # Try Hugging Face API first (free tier available)
        ai_response = self._try_hugging_face_api(message, conversation_history)
        
        if not ai_response:
            # Fallback to rule-based response
            ai_response = self._generate_rule_based_response(message)
        
        return ai_response
    
    def _try_hugging_face_api(self, message, conversation_history):
        """Use Hugging Face Inference API with a small model"""
        try:
            # You'll need to create a free account and get an API token
            API_TOKEN = os.getenv('HUGGINGFACE_API_TOKEN')
            if not API_TOKEN:
                return None
                
            API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
            headers = {"Authorization": f"Bearer {API_TOKEN}"}
            
            # Prepare conversation context
            context = self._build_conversation_context(conversation_history)
            full_prompt = f"{context}\nStudent: {message}\nAI Coach:"
            
            payload = {
                "inputs": full_prompt,
                "parameters": {
                    "max_length": 150,
                    "temperature": 0.7,
                    "do_sample": True,
                },
                "options": {
                    "wait_for_model": True
                }
            }
            
            response = requests.post(API_URL, headers=headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get('generated_text', '').split('AI Coach:')[-1].strip()
            
            return None
            
        except Exception as e:
            print(f"Hugging Face API error: {e}")
            return None
    
    def _build_conversation_context(self, conversation_history):
        """Build context for the AI based on student profile"""
        context = f"""
        You are an AI career and academic coach for Kenyan students.
        Student Profile:
        - Personality Type: {self.personality_type.mbti_type} ({self.personality_type.name})
        - Strengths: {self.personality_type.strengths[:200]}
        - Career Interests: {self.student.career_aspirations[:100] if self.student.career_aspirations else 'Not specified'}
        
        Your role is to provide:
        1. Career guidance based on personality and Kenyan market
        2. Study tips and learning strategies
        3. Subject combination advice
        4. Motivation and personal development guidance
        5. Kenyan education system specific advice
        
        Be supportive, practical, and culturally appropriate for Kenyan students.
        Keep responses concise and actionable.
        """
        return context
    
    def _generate_rule_based_response(self, message):
        """Fallback rule-based response system"""
        message_lower = message.lower()
        
        # Career-related queries
        if any(word in message_lower for word in ['career', 'job', 'work', 'profession']):
            return self._generate_career_advice()
        
        # Study-related queries
        elif any(word in message_lower for word in ['study', 'learn', 'exam', 'subject']):
            return self._generate_study_advice()
        
        # Motivation-related queries
        elif any(word in message_lower for word in ['motivate', 'encourage', 'stressed', 'tired']):
            return self._generate_motivational_message()
        
        # Default response
        else:
            return "I understand you're looking for guidance. Could you tell me more about what specific area you'd like help with - career choices, study strategies, or personal development?"
    
    def _generate_career_advice(self):
        """Generate career advice based on personality"""
        base_advice = f"Based on your {self.personality_type.mbti_type} personality, "
        
        advice_map = {
            'INTJ': "you excel in strategic planning and complex problem-solving. Consider careers in engineering, architecture, or research where you can develop innovative solutions.",
            'INTP': "your analytical thinking and curiosity make you great in theoretical fields. Look into computer science, research, or academic careers.",
            'ENTJ': "your leadership and organizational skills are assets. Business management, law, or entrepreneurship could be excellent fits.",
            'ENTP': "you thrive on innovation and debate. Consider marketing, law, or technology roles that challenge your creativity.",
            'INFJ': "your empathy and insight are valuable. Counseling, teaching, or humanitarian work might be fulfilling.",
            'INFP': "your creativity and values drive you. Writing, arts, or psychology could align well with your personality.",
            'ENFJ': "your people skills and idealism are strengths. Consider teaching, human resources, or community development.",
            'ENFP': "your enthusiasm and creativity are infectious. Marketing, event planning, or counseling might suit you.",
            'ISTJ': "your reliability and attention to detail are valuable. Accounting, administration, or technical fields could be good fits.",
            'ISFJ': "your compassion and practicality are assets. Healthcare, teaching, or social work might be rewarding.",
            'ESTJ': "your organizational skills and practicality are strengths. Business management, law enforcement, or project management could suit you.",
            'ESFJ': "your sociability and care for others are valuable. Teaching, healthcare, or customer service roles might be fulfilling.",
            'ISTP': "your hands-on problem-solving is a strength. Engineering, mechanics, or technology roles could be good fits.",
            'ISFP': "your artistic sensitivity and practicality combine well. Design, healthcare, or environmental work might appeal to you.",
            'ESTP': "your energy and practicality are assets. Sales, entrepreneurship, or emergency services could be exciting.",
            'ESFP': "your enthusiasm and people skills are strengths. Entertainment, hospitality, or teaching might be fulfilling.",
        }
        
        return base_advice + advice_map.get(self.personality_type.mbti_type, "you have unique strengths that can succeed in many fields. Let's explore your specific interests further.")
    
    def _generate_study_advice(self):
        """Generate study advice based on learning style"""
        learning_style = self.get_learning_style_recommendation()
        
        advice_map = {
            'visual': "Try using mind maps, diagrams, and color-coded notes. Watch educational videos and create visual summaries of your topics.",
            'auditory': "Record your notes and listen to them. Study in groups and explain concepts aloud. Use rhymes or songs to remember information.",
            'reading': "Focus on textbooks and written materials. Take detailed notes and rewrite them. Create summaries and read them repeatedly.",
            'kinesthetic': "Use hands-on activities and experiments. Take frequent breaks to move around. Create physical models or use flashcards you can handle.",
        }
        
        base_advice = f"As a {learning_style.name} learner, "
        return base_advice + advice_map.get(learning_style.name, "experiment with different study methods to find what works best for you.")
    
    def _generate_motivational_message(self):
        """Generate culturally appropriate motivational messages"""
        motivations = [
            "Remember the Swahili proverb: 'Kidole kimoja hakivunji chawa' - one finger can't crush a louse. Success comes through persistent effort!",
            "You're building your future step by step. Every subject you master opens new doors in Kenya's growing economy.",
            "Greatness takes time. Even the tallest building in Nairobi started with a single foundation. Keep building yours!",
            "Your unique personality strengths are exactly what Kenya needs. The country is growing fast and needs diverse talents like yours.",
            "Remember that challenges are what make success meaningful. Every successful Kenyan professional once sat where you are now.",
            "Education is your passport to the future. Each day of study is stamping that passport for journeys you haven't even imagined yet.",
        ]
        
        import random
        return random.choice(motivations)