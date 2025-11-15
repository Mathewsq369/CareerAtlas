from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from .models import Career, Subject, StudentRecommendation, LearningStyle
from .serializers import (
    CareerSerializer, SubjectSerializer, StudentRecommendationSerializer,
    LearningStyleSerializer, CareerRecommendationSerializer
)
from .services import RecommendationEngine, SubjectRecommender

class CareerViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CareerSerializer
    queryset = Career.objects.prefetch_related(
        'required_subjects', 'recommended_subjects', 'personality_matches'
    ).all()
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        category = request.query_params.get('category')
        if category:
            careers = self.get_queryset().filter(category=category)
        else:
            careers = self.get_queryset()
        
        serializer = self.get_serializer(careers, many=True)
        return Response(serializer.data)

class SubjectViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SubjectSerializer
    queryset = Subject.objects.all()
    pagination_class = None

class StudentRecommendationViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = StudentRecommendationSerializer
    
    def get_queryset(self):
        return StudentRecommendation.objects.filter(
            student=self.request.user.studentprofile
        ).select_related('career').prefetch_related('recommended_subjects')
    
    @action(detail=False, methods=['get'])
    def generate(self, request):
        """Generate new career recommendations"""
        student_profile = request.user.studentprofile
        
        # Check if assessment is completed
        try:
            assessment_result = student_profile.assessmentresult
        except:
            return Response(
                {'error': 'Complete personality assessment first'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        engine = RecommendationEngine(student_profile)
        recommendations = engine.generate_career_recommendations(top_n=10)
        
        # Return the generated recommendations (not saved ones)
        serializer = CareerRecommendationSerializer(recommendations, many=True)
        return Response(serializer.data)

class LearningStyleViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LearningStyleSerializer
    queryset = LearningStyle.objects.all()
    pagination_class = None

# Template Views
class RecommendationsView(LoginRequiredMixin, TemplateView):
    template_name = 'recommendations/careers.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student_profile = self.request.user.studentprofile
        
        # Get recommendations
        recommendations = StudentRecommendation.objects.filter(
            student=student_profile
        ).select_related('career').prefetch_related('recommended_subjects')[:10]
        
        context['recommendations'] = recommendations
        
        # Get learning style
        from ai_coach.services import AICoachService
        try:
            coach = AICoachService(student_profile)
            learning_style = coach.get_learning_style_recommendation()
            context['learning_style'] = learning_style
        except:
            context['learning_style'] = None
        
        return context

class CareerDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'recommendations/career_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        career_id = self.kwargs.get('pk')
        
        try:
            career = Career.objects.prefetch_related(
                'required_subjects', 'recommended_subjects', 'personality_matches'
            ).get(id=career_id)
            context['career'] = career
        except Career.DoesNotExist:
            context['career'] = None
        
        return context