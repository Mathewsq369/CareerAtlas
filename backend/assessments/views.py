from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from .models import AssessmentSession, Question, AnswerChoice, QuestionResponse
from .serializers import (
    QuestionSerializer, AssessmentSessionSerializer, 
    QuestionResponseSerializer, AssessmentResultSerializer
)
from .services import MBTICalculator

class QuestionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = QuestionSerializer
    
    def get_queryset(self):
        return Question.objects.prefetch_related('choices').all()

class AssessmentSessionViewSet(viewsets.ModelViewSet):
    serializer_class = AssessmentSessionSerializer
    
    def get_queryset(self):
        return AssessmentSession.objects.filter(
            student__user=self.request.user
        ).prefetch_related('responses')
    
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
        
        return Response({'status': 'Response saved'})
    
    @action(detail=True, methods=['post'])
    def complete_assessment(self, request, pk=None):
        """Complete assessment and generate results"""
        session = self.get_object()
        
        if session.responses.count() < 40:  # Minimum questions threshold
            return Response(
                {'error': 'Complete more questions before finishing'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate results
        calculator = MBTICalculator(session)
        result = calculator.generate_result()
        
        # Mark session as completed
        session.is_completed = True
        session.save()
        
        # Return results
        result_serializer = AssessmentResultSerializer(result)
        return Response(result_serializer.data)

class AssessmentResultViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AssessmentResultSerializer
    
    def get_queryset(self):
        return AssessmentResult.objects.filter(
            student__user=self.request.user
        ).select_related('personality_type')