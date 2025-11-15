import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from django.db.models import Q
from assessments.models import AssessmentResult
from .models import Career, CareerPersonalityMatch, StudentRecommendation, Subject

class RecommendationEngine:
    def __init__(self, student):
        self.student = student
        self.assessment_result = AssessmentResult.objects.get(student=student)
    
    def calculate_personality_match(self, career):
        """Calculate personality compatibility with career"""
        try:
            match = CareerPersonalityMatch.objects.get(
                career=career,
                personality_type=self.assessment_result.personality_type
            )
            return match.compatibility_score
        except CareerPersonalityMatch.DoesNotExist:
            # Default compatibility for unknown combinations
            return 0.5
    
    def calculate_academic_match(self, career):
        """Calculate academic suitability based on student's subjects and performance"""
        student_subjects = set(self.student.subjects.all())
        required_subjects = set(career.required_subjects.all())
        recommended_subjects = set(career.recommended_subjects.all())
        
        # Check if student meets required subjects
        if not required_subjects.issubset(student_subjects):
            return 0.0
        
        # Calculate overlap with recommended subjects
        overlap = len(student_subjects.intersection(recommended_subjects))
        total_recommended = len(recommended_subjects)
        
        if total_recommended == 0:
            return 1.0  # No specific recommendations
        
        return overlap / total_recommended
    
    def generate_career_recommendations(self, top_n=10):
        """Generate personalized career recommendations"""
        all_careers = Career.objects.all()
        recommendations = []
        
        for career in all_careers:
            personality_score = float(self.calculate_personality_match(career))
            academic_score = float(self.calculate_academic_match(career))
            
            # Weighted overall score (personality: 60%, academic: 40%)
            overall_score = (personality_score * 0.6) + (academic_score * 0.4)
            
            recommendations.append({
                'career': career,
                'personality_match_score': personality_score,
                'academic_match_score': academic_score,
                'overall_score': overall_score,
                'reasoning': self.generate_reasoning(career, personality_score, academic_score)
            })
        
        # Sort by overall score and get top N
        recommendations.sort(key=lambda x: x['overall_score'], reverse=True)
        top_recommendations = recommendations[:top_n]
        
        # Save to database
        self.save_recommendations(top_recommendations)
        
        return top_recommendations
    
    def generate_reasoning(self, career, personality_score, academic_score):
        """Generate explanation for recommendation"""
        reasoning_parts = []
        
        if personality_score >= 0.8:
            reasoning_parts.append(f"Excellent personality match with {career.name}")
        elif personality_score >= 0.6:
            reasoning_parts.append(f"Good personality alignment with {career.name}")
        else:
            reasoning_parts.append(f"Moderate personality fit for {career.name}")
        
        if academic_score >= 0.8:
            reasoning_parts.append("Strong academic preparation")
        elif academic_score >= 0.6:
            reasoning_parts.append("Good academic foundation")
        else:
            reasoning_parts.append("May need additional subject preparation")
        
        # Add market insights for Kenya
        if career.kenyan_market_demand == 'growing':
            reasoning_parts.append("High growth potential in Kenyan market")
        elif career.kenyan_market_demand == 'stable':
            reasoning_parts.append("Stable career opportunities in Kenya")
        
        return ". ".join(reasoning_parts) + "."
    
    def save_recommendations(self, recommendations):
        """Save recommendations to database"""
        for rec in recommendations:
            student_rec, created = StudentRecommendation.objects.update_or_create(
                student=self.student,
                career=rec['career'],
                defaults={
                    'personality_match_score': rec['personality_match_score'],
                    'academic_match_score': rec['academic_match_score'],
                    'overall_score': rec['overall_score'],
                    'reasoning': rec['reasoning'],
                }
            )
            # Add recommended subjects
            student_rec.recommended_subjects.set(rec['career'].recommended_subjects.all())

class SubjectRecommender:
    def __init__(self, student):
        self.student = student
        self.assessment_result = AssessmentResult.objects.get(student=student)
    
    def recommend_subjects(self):
        """Recommend subjects based on personality and career goals"""
        personality_type = self.assessment_result.personality_type
        
        # Personality-based subject preferences
        personality_preferences = {
            'INTJ': ['Mathematics', 'Physics', 'Computer Studies', 'Chemistry'],
            'INTP': ['Mathematics', 'Physics', 'Computer Studies', 'Biology'],
            'ENTJ': ['Business Studies', 'Mathematics', 'Economics', 'History'],
            'ENTP': ['Computer Studies', 'Physics', 'Geography', 'Business Studies'],
            'INFJ': ['Languages', 'History', 'Biology', 'CRE'],
            'INFP': ['Languages', 'Literature', 'Art', 'Music'],
            'ENFJ': ['Languages', 'History', 'Business Studies', 'CRE'],
            'ENFP': ['Languages', 'Geography', 'Business Studies', 'Drama'],
            'ISTJ': ['Mathematics', 'Chemistry', 'Business Studies', 'Geography'],
            'ISFJ': ['Biology', 'Home Science', 'Languages', 'CRE'],
            'ESTJ': ['Business Studies', 'Mathematics', 'Geography', 'History'],
            'ESFJ': ['Languages', 'Home Science', 'Business Studies', 'CRE'],
            'ISTP': ['Physics', 'Chemistry', 'Technical Drawing', 'Computer Studies'],
            'ISFP': ['Art', 'Music', 'Home Science', 'Biology'],
            'ESTP': ['Business Studies', 'Physical Education', 'Geography', 'Computer Studies'],
            'ESFP': ['Music', 'Drama', 'Business Studies', 'Languages'],
        }
        
        base_subjects = personality_preferences.get(personality_type.mbti_type, [])
        
        # Add career-aligned subjects
        engine = RecommendationEngine(self.student)
        career_recs = engine.generate_career_recommendations(top_n=3)
        
        career_subjects = set()
        for rec in career_recs:
            career_subjects.update(
                rec['career'].recommended_subjects.values_list('name', flat=True)
            )
        
        # Combine and prioritize
        all_recommended = list(set(base_subjects + list(career_subjects)))
        
        return all_recommended[:8]  # Return top 8 subjects