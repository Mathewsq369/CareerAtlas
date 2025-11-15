from rest_framework import serializers
from .models import Career, Subject, CareerPersonalityMatch, LearningStyle, StudentRecommendation

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'code', 'category', 'difficulty_level']

class CareerPersonalityMatchSerializer(serializers.ModelSerializer):
    personality_type_name = serializers.CharField(source='personality_type.name', read_only=True)
    personality_type_code = serializers.CharField(source='personality_type.mbti_type', read_only=True)
    
    class Meta:
        model = CareerPersonalityMatch
        fields = ['id', 'personality_type', 'personality_type_name', 'personality_type_code', 'compatibility_score', 'reasoning']

class CareerSerializer(serializers.ModelSerializer):
    required_subjects = SubjectSerializer(many=True, read_only=True)
    recommended_subjects = SubjectSerializer(many=True, read_only=True)
    personality_matches = CareerPersonalityMatchSerializer(many=True, read_only=True)
    
    class Meta:
        model = Career
        fields = [
            'id', 'name', 'description', 'category', 'required_subjects',
            'recommended_subjects', 'personality_matches', 'average_salary',
            'job_outlook', 'kenyan_market_demand'
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
            'id', 'student', 'career', 'personality_match_score',
            'academic_match_score', 'overall_score', 'reasoning',
            'recommended_subjects', 'created_at'
        ]

class CareerRecommendationSerializer(serializers.Serializer):
    career = CareerSerializer()
    personality_match_score = serializers.DecimalField(max_digits=3, decimal_places=2)
    academic_match_score = serializers.DecimalField(max_digits=3, decimal_places=2)
    overall_score = serializers.DecimalField(max_digits=3, decimal_places=2)
    reasoning = serializers.CharField()