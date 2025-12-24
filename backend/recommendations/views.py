from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, DetailView
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.http import JsonResponse

from .models import Career, Subject, StudentRecommendation, LearningStyle
from .serializers import (
    CareerSerializer, SubjectSerializer, StudentRecommendationSerializer,
    LearningStyleSerializer, CareerRecommendationSerializer
)
from .services import RecommendationEngine, SubjectRecommender
from users.models import StudentProfile

class CareerViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CareerSerializer
    queryset = Career.objects.prefetch_related(
        'required_subjects', 'recommended_subjects'
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

# ==================== TEMPLATE VIEWS ====================

class CareerRecommendationsView(LoginRequiredMixin, TemplateView):
    """View to display personalized career recommendations"""
    template_name = 'recommendations/career_recommendations.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student_profile = self.request.user.studentprofile
        
        # Generate recommendations if they don't exist
        recommendations = StudentRecommendation.objects.filter(
            student=student_profile
        ).select_related('career').prefetch_related('recommended_subjects').order_by('-overall_score')
        
        if not recommendations.exists():
            try:
                assessment_result = student_profile.assessmentresult
                engine = RecommendationEngine(student_profile)
                recommendations_data = engine.generate_career_recommendations(top_n=10)
                # Get the saved recommendations
                recommendations = StudentRecommendation.objects.filter(
                    student=student_profile
                ).select_related('career').prefetch_related('recommended_subjects').order_by('-overall_score')
            except:
                recommendations = StudentRecommendation.objects.none()
        
        # Get subject recommendations
        try:
            subject_recommender = SubjectRecommender(student_profile)
            recommended_subjects = subject_recommender.recommend_subjects()
        except:
            recommended_subjects = []
        
        context.update({
            'recommendations': recommendations,
            'recommended_subjects': recommended_subjects,
            'student': student_profile,
        })
        return context

class CareerDetailView(LoginRequiredMixin, DetailView):
    """View to display detailed information about a specific career"""
    model = Career
    template_name = 'recommendations/career_detail.html'
    context_object_name = 'career'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.request.user.studentprofile
        
        # Check if this career is recommended for the student
        try:
            recommendation = StudentRecommendation.objects.get(
                student=student,
                career=self.object
            )
            context['recommendation'] = recommendation
        except StudentRecommendation.DoesNotExist:
            context['recommendation'] = None
        
        # Get related careers
        related_careers = Career.objects.filter(
            Q(category=self.object.category) | 
            Q(required_subjects__in=self.object.required_subjects.all())
        ).distinct().exclude(id=self.object.id)[:5]
        
        context['related_careers'] = related_careers
        context['student'] = student
        return context

class CareerListView(LoginRequiredMixin, ListView):
    """View to browse all available careers"""
    model = Career
    template_name = 'recommendations/career_list.html'
    context_object_name = 'careers'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset().prefetch_related('required_subjects', 'recommended_subjects')
        
        # Apply filters
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        demand = self.request.GET.get('demand')
        if demand:
            queryset = queryset.filter(kenyan_market_demand=demand)
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search)
            )
        
        return queryset.order_by('name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Career.objects.values_list('category', flat=True).distinct()
        return context

class SubjectListView(LoginRequiredMixin, ListView):
    """View to browse available subjects"""
    model = Subject
    template_name = 'recommendations/subject_list.html'
    context_object_name = 'subjects'
    
    def get_queryset(self):
        return Subject.objects.all().order_by('name')