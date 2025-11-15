from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.db import transaction

from .models import Conversation, Message, CoachingPlan
from .serializers import (
    ConversationSerializer, MessageSerializer, 
    CoachingPlanSerializer, ChatMessageSerializer
)
from .services import AICoachService

class ConversationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ConversationSerializer
    
    def get_queryset(self):
        return Conversation.objects.filter(
            student=self.request.user.studentprofile
        ).prefetch_related('messages')
    
    def perform_create(self, serializer):
        serializer.save(student=self.request.user.studentprofile)
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """Send a message in a conversation"""
        conversation = self.get_object()
        serializer = ChatMessageSerializer(data=request.data)
        
        if serializer.is_valid():
            message_content = serializer.validated_data['message']
            
            # Save user message
            user_message = Message.objects.create(
                conversation=conversation,
                content=message_content,
                is_from_ai=False
            )
            
            # Generate AI response
            coach_service = AICoachService(conversation.student)
            ai_response = coach_service.generate_ai_response(
                message_content,
                conversation_history=conversation.messages.all()
            )
            
            # Save AI response
            ai_message = Message.objects.create(
                conversation=conversation,
                content=ai_response,
                is_from_ai=True
            )
            
            # Update conversation title if it's the first message
            if conversation.messages.count() == 2:  # User + AI message
                conversation.title = message_content[:50] + "..."
                conversation.save()
            
            return Response({
                'user_message': MessageSerializer(user_message).data,
                'ai_message': MessageSerializer(ai_message).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CoachingPlanViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CoachingPlanSerializer
    
    def get_queryset(self):
        return CoachingPlan.objects.filter(
            student=self.request.user.studentprofile
        ).select_related('personality_type', 'learning_style').prefetch_related('resources')
    
    @action(detail=False, methods=['post'])
    def generate_plan(self, request):
        """Generate or update coaching plan"""
        student_profile = request.user.studentprofile
        
        # Check if assessment is completed
        try:
            assessment_result = student_profile.assessmentresult
        except:
            return Response(
                {'error': 'Complete personality assessment first'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        coach_service = AICoachService(student_profile)
        learning_style = coach_service.get_learning_style_recommendation()
        
        # Create or update coaching plan
        plan, created = CoachingPlan.objects.update_or_create(
            student=student_profile,
            defaults={
                'personality_type': assessment_result.personality_type,
                'learning_style': learning_style,
                'goals': request.data.get('goals', {}),
                'challenges': request.data.get('challenges', [])
            }
        )
        
        serializer = self.get_serializer(plan)
        return Response(serializer.data)

# Template Views
class AICoachView(LoginRequiredMixin, TemplateView):
    template_name = 'ai_coach/chat.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student_profile = self.request.user.studentprofile
        
        # Get or create coaching plan
        try:
            coaching_plan = student_profile.coachingplan
            context['coaching_plan'] = coaching_plan
        except CoachingPlan.DoesNotExist:
            context['coaching_plan'] = None
        
        # Get recent conversations
        conversations = Conversation.objects.filter(
            student=student_profile
        ).prefetch_related('messages')[:5]
        context['conversations'] = conversations
        
        return context

class LearningResourcesView(LoginRequiredMixin, TemplateView):
    template_name = 'ai_coach/resources.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student_profile = self.request.user.studentprofile
        
        try:
            coaching_plan = student_profile.coachingplan
            resources = coaching_plan.resources.all()
            context['resources'] = resources
        except CoachingPlan.DoesNotExist:
            context['resources'] = []
        
        return context