from django.db import transaction
from .models import AssessmentSession, AssessmentResult, PersonalityType

class MBTICalculator:
    def __init__(self, assessment_session):
        self.session = assessment_session
        self.scores = {
            'EI': 0,  # Positive: Extraversion, Negative: Introversion
            'SN': 0,  # Positive: Sensing, Negative: Intuition
            'TF': 0,  # Positive: Thinking, Negative: Feeling
            'JP': 0,  # Positive: Judging, Negative: Perceiving
        }
    
    def calculate_scores(self):
        """Calculate raw scores for each dimension"""
        responses = self.session.responses.select_related('question', 'answer').all()
        
        for response in responses:
            category = response.question.category
            value = response.answer.value
            self.scores[category] += value
        
        return self.scores
    
    def determine_personality_type(self, scores):
        """Convert scores to MBTI type"""
        mbti_code = ""
        
        # EI Dimension
        mbti_code += 'E' if scores['EI'] > 0 else 'I'
        
        # SN Dimension
        mbti_code += 'S' if scores['SN'] > 0 else 'N'
        
        # TF Dimension
        mbti_code += 'T' if scores['TF'] > 0 else 'F'
        
        # JP Dimension
        mbti_code += 'J' if scores['JP'] > 0 else 'P'
        
        return mbti_code
    
    def calculate_confidence(self, scores):
        """Calculate confidence level based on score magnitudes"""
        total_absolute = sum(abs(score) for score in scores.values())
        max_possible = 60  # Assuming 20 questions per dimension * max score of 3
        confidence = min(total_absolute / max_possible, 1.0)
        return round(confidence, 2)
    
    @transaction.atomic
    def generate_result(self):
        """Generate final assessment result"""
        scores = self.calculate_scores()
        mbti_type_code = self.determine_personality_type(scores)
        confidence = self.calculate_confidence(scores)
        
        try:
            personality_type = PersonalityType.objects.get(mbti_type=mbti_type_code)
        except PersonalityType.DoesNotExist:
            # Fallback or create default
            personality_type = PersonalityType.objects.first()
        
        result, created = AssessmentResult.objects.update_or_create(
            student=self.session.student,
            defaults={
                'personality_type': personality_type,
                'ei_score': scores['EI'],
                'sn_score': scores['SN'],
                'tf_score': scores['TF'],
                'jp_score': scores['JP'],
                'confidence': confidence,
            }
        )
        
        return result