from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import StudentRecommendation, Career, Subject
from .serializers import (
    CareerSerializer, StudentRecommendationSerializer, 
    SubjectSerializer
)
from .services import RecommendationEngine, SubjectRecommender

class CareerViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CareerSerializer
    queryset = Career.objects.all()

class StudentRecommendationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = StudentRecommendationSerializer
    
    def get_queryset(self):
        return StudentRecommendation.objects.filter(
            student__user=self.request.user
        ).select_related('career').prefetch_related('recommended_subjects')
    
    @action(detail=False, methods=['get'])
    def generate_recommendations(self, request):
        """Generate new career recommendations"""
        student_profile = request.user.studentprofile
        
        engine = RecommendationEngine(student_profile)
        recommendations = engine.generate_career_recommendations()
        
        # Get the saved recommendations
        saved_recommendations = self.get_queryset()
        serializer = self.get_serializer(saved_recommendations, many=True)
        
        return Response(serializer.data)

class SubjectRecommendationView(viewsets.ViewSet):
    @action(detail=False, methods=['get'])
    def get_recommendations(self, request):
        """Get subject recommendations"""
        student_profile = request.user.studentprofile
        
        recommender = SubjectRecommender(student_profile)
        recommended_subjects = recommender.recommend_subjects()
        
        # Get full subject objects
        subjects = Subject.objects.filter(name__in=recommended_subjects)
        serializer = SubjectSerializer(subjects, many=True)
        
        return Response(serializer.data)