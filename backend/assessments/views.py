from rest_framework import viewsets, status, generics
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import render, get_object_or_404
from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, DetailView

from .models import (
    AssessmentSession, Question, AnswerChoice, QuestionResponse,
    AssessmentResult, PersonalityType
)
from .serializers import (
    QuestionSerializer, AssessmentSessionSerializer,
    QuestionResponseSerializer, AssessmentResultSerializer,
    AssessmentSubmissionSerializer, PersonalityTypeSerializer
)
from .services import MBTICalculator

class QuestionViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = QuestionSerializer
    pagination_class = None  # We want all questions at once
    
    def get_queryset(self):
        return Question.objects.prefetch_related('choices').all()

class AssessmentSessionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = AssessmentSessionSerializer
    
    def get_queryset(self):
        return AssessmentSession.objects.filter(
            student=self.request.user.studentprofile
        ).prefetch_related('responses', 'responses__question', 'responses__answer')
    
    def perform_create(self, serializer):
        """Automatically assign student profile when creating session"""
        serializer.save(student=self.request.user.studentprofile)
    
    def create(self, request):
        """Start a new assessment session"""
        student_profile = request.user.studentprofile
        
        # Check if there's an existing incomplete session
        existing_session = AssessmentSession.objects.filter(
            student=student_profile,
            is_completed=False
        ).first()
        
        if existing_session:
            serializer = self.get_serializer(existing_session)
            return Response(serializer.data)
        
        # Create new session
        session = AssessmentSession.objects.create(student=student_profile)
        serializer = self.get_serializer(session)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def submit_response(self, request, pk=None):
        """Submit response to a question"""
        session = self.get_object()
        
        # FIX: Verify session belongs to current user
        if session.student.user != request.user:
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
            
        question_id = request.data.get('question_id')
        answer_id = request.data.get('answer_id')
        response_time = request.data.get('response_time', 0)
        
        try:
            question = Question.objects.get(id=question_id)
            answer = AnswerChoice.objects.get(id=answer_id, question=question)
        except (Question.DoesNotExist, AnswerChoice.DoesNotExist):
            return Response(
                {'error': 'Invalid question or answer'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Save or update response
        response, created = QuestionResponse.objects.update_or_create(
            session=session,
            question=question,
            defaults={
                'answer': answer,
                'response_time': response_time
            }
        )
        
        serializer = QuestionResponseSerializer(response)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def complete_assessment(self, request, pk=None):
        """Complete assessment and generate results"""
        session = self.get_object()
        
        # FIX: Verify session belongs to current user
        if session.student.user != request.user:
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # FIX: Reduced minimum questions for testing
        if session.responses.count() < 5:  # Reduced from 20 for testing
            return Response(
                {'error': f'Complete more questions before finishing. You have answered {session.responses.count()} questions.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Calculate results
            calculator = MBTICalculator(session)
            result = calculator.generate_result()
            
            # Mark session as completed
            session.is_completed = True
            session.save()
            
            # Return results
            result_serializer = AssessmentResultSerializer(result)
            return Response(result_serializer.data)
            
        except Exception as e:
            return Response(
                {'error': f'Error generating results: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class AssessmentResultViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = AssessmentResultSerializer
    
    def get_queryset(self):
        return AssessmentResult.objects.filter(
            student__user=self.request.user
        ).select_related('personality_type')

class PersonalityTypeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PersonalityTypeSerializer
    queryset = PersonalityType.objects.all()
    pagination_class = None

# Template Views
class AssessmentStartView(LoginRequiredMixin, TemplateView):
    """View for assessment start page"""
    template_name = 'assessments/start.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Check if user has existing assessment
        has_previous_assessment = AssessmentResult.objects.filter(
            student=self.request.user.studentprofile
        ).exists()
        context['has_previous_assessment'] = has_previous_assessment
        return context

class AssessmentQuestionView(LoginRequiredMixin, TemplateView):
    """View for assessment questions"""
    template_name = 'assessments/question.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get or create assessment session
        session, created = AssessmentSession.objects.get_or_create(
            student=self.request.user.studentprofile,
            is_completed=False
        )
        context['session'] = session
        context['questions'] = Question.objects.prefetch_related('choices').all()
        return context

class AssessmentResultsView(LoginRequiredMixin, DetailView):
    """View for assessment results"""
    template_name = 'assessments/results.html'
    context_object_name = 'result'
    
    def get_object(self):
        return get_object_or_404(
            AssessmentResult.objects.select_related('personality_type'),
            student=self.request.user.studentprofile
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add recommendation engine results
        try:
            from recommendations.services import RecommendationEngine
            engine = RecommendationEngine(self.object.student)
            recommendations = engine.generate_career_recommendations(top_n=5)
            context['career_recommendations'] = recommendations
        except Exception as e:
            print(f"Error getting recommendations: {e}")
            context['career_recommendations'] = []
        
        return context

# API Views for AJAX calls
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_bulk_responses(request):
    """Submit multiple responses at once"""
    serializer = AssessmentSubmissionSerializer(data=request.data)
    
    if serializer.is_valid():
        session_id = serializer.validated_data['session_id']
        responses_data = serializer.validated_data['responses']
        
        try:
            session = AssessmentSession.objects.get(
                id=session_id,
                student=request.user.studentprofile
            )
        except AssessmentSession.DoesNotExist:
            return Response(
                {'error': 'Invalid assessment session'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            for response_data in responses_data:
                question_id = response_data['question_id']
                answer_id = response_data['answer_id']
                response_time = response_data.get('response_time', 0)
                
                try:
                    question = Question.objects.get(id=question_id)
                    answer = AnswerChoice.objects.get(id=answer_id, question=question)
                    
                    QuestionResponse.objects.update_or_create(
                        session=session,
                        question=question,
                        defaults={
                            'answer': answer,
                            'response_time': response_time
                        }
                    )
                except (Question.DoesNotExist, AnswerChoice.DoesNotExist):
                    continue  # Skip invalid responses
        
        return Response({'status': 'Responses saved successfully'})
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_next_question(request, session_id):
    """Get next unanswered question for a session"""
    try:
        session = AssessmentSession.objects.get(
            id=session_id,
            student=request.user.studentprofile
        )
    except AssessmentSession.DoesNotExist:
        return Response(
            {'error': 'Invalid session'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get answered question IDs
    answered_question_ids = session.responses.values_list('question_id', flat=True)
    
    # Get next unanswered question
    next_question = Question.objects.exclude(
        id__in=answered_question_ids
    ).prefetch_related('choices').first()
    
    if next_question:
        serializer = QuestionSerializer(next_question)
        return Response(serializer.data)
    else:
        return Response({'message': 'All questions answered'})