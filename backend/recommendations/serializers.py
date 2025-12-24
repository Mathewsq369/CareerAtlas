from rest_framework import serializers
from .models import Career, Subject, StudentRecommendation, LearningStyle
from assessments.models import PersonalityType

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'code', 'category', 'difficulty_level']

class PersonalityTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalityType
        fields = ['id', 'mbti_type', 'name', 'description']

class CareerSerializer(serializers.ModelSerializer):
    required_subjects = SubjectSerializer(many=True, read_only=True)
    recommended_subjects = SubjectSerializer(many=True, read_only=True)
    
    class Meta:
        model = Career
        fields = [
            'id', 'name', 'description', 'category', 
            'required_subjects', 'recommended_subjects',
            'average_salary', 'job_outlook', 'kenyan_market_demand'
        ]

class LearningStyleSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningStyle
        fields = ['id', 'name', 'description', 'study_recommendations']

class StudentRecommendationSerializer(serializers.ModelSerializer):
    career = CareerSerializer(read_only=True)
    recommended_subjects = SubjectSerializer(many=True, read_only=True)
    
    class Meta:
        model = StudentRecommendation
        fields = [
            'id', 'career', 'personality_match_score',
            'academic_match_score', 'overall_score', 'reasoning',
            'recommended_subjects', 'created_at'
        ]

class CareerRecommendationSerializer(serializers.Serializer):
    """Serializer for generated recommendations (not saved)"""
    career = CareerSerializer()
    personality_match_score = serializers.DecimalField(max_digits=3, decimal_places=2)
    academic_match_score = serializers.DecimalField(max_digits=3, decimal_places=2)
    overall_score = serializers.DecimalField(max_digits=3, decimal_places=2)
    reasoning = serializers.CharField()