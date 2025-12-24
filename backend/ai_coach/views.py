from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, DetailView
from django.views import View
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db import transaction
import json

from .models import Conversation, Message, CoachingPlan, ResourceRecommendation
from .serializers import (
    ConversationSerializer, MessageSerializer, 
    CoachingPlanSerializer, ChatMessageSerializer
)
from .services import AICoachService
from users.models import StudentProfile
from assessments.models import AssessmentResult

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
        )
    
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

# ==================== TEMPLATE VIEWS ====================

class AICoachChatView(LoginRequiredMixin, TemplateView):
    template_name = 'ai_coach/chat.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student_profile = self.request.user.studentprofile
        
        # Get conversation ID from URL or get/create one
        conversation_id = self.kwargs.get('conversation_id')
        
        if conversation_id:
            conversation = get_object_or_404(
                Conversation, 
                id=conversation_id, 
                student=student_profile
            )
        else:
            # Get or create a conversation
            conversation, created = Conversation.objects.get_or_create(
                student=student_profile,
                defaults={'title': 'Career Guidance Session'}
            )
        
        # Get or create coaching plan
        try:
            coaching_plan = student_profile.coachingplan
            context['coaching_plan'] = coaching_plan
        except CoachingPlan.DoesNotExist:
            context['coaching_plan'] = None
        
        # Get recent conversations for sidebar
        conversations = Conversation.objects.filter(
            student=student_profile
        ).order_by('-updated_at')[:5]
        
        context.update({
            'conversation': conversation,
            'conversations': conversations,
            'student': student_profile,
        })
        return context

class ConversationListView(LoginRequiredMixin, TemplateView):
    """View to list all conversations"""
    template_name = 'ai_coach/conversations.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student_profile = self.request.user.studentprofile
        
        conversations = Conversation.objects.filter(
            student=student_profile
        ).order_by('-updated_at')
        context['conversations'] = conversations
        context['student'] = student_profile
        return context

class CoachingPlanView(LoginRequiredMixin, TemplateView):
    """View to display and manage coaching plan"""
    template_name = 'ai_coach/coaching_plan.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student_profile = self.request.user.studentprofile
        
        coaching_plan, created = CoachingPlan.objects.get_or_create(
            student=student_profile
        )
        
        # Get learning style if not set
        if not coaching_plan.learning_style:
            try:
                coach_service = AICoachService(student_profile)
                learning_style = coach_service.get_learning_style_recommendation()
                coaching_plan.learning_style = learning_style
                coaching_plan.save()
            except:
                pass
        
        context.update({
            'coaching_plan': coaching_plan,
            'student': student_profile,
        })
        return context

class LearningResourcesView(LoginRequiredMixin, TemplateView):
    template_name = 'ai_coach/resources.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student_profile = self.request.user.studentprofile
        
        try:
            coaching_plan = student_profile.coachingplan
            resources = ResourceRecommendation.objects.filter(
                coaching_plan=coaching_plan
            )
            context['resources'] = resources
        except CoachingPlan.DoesNotExist:
            context['resources'] = []
        
        context['student'] = student_profile
        return context

# ==================== API VIEWS FOR TEMPLATES ====================

class AICoachAPIView(LoginRequiredMixin, View):
    """API endpoint for AI coach interactions (for templates)"""
    
    def post(self, request, conversation_id=None):
        try:
            data = json.loads(request.body)
            message = data.get('message', '')
            
            if not message:
                return JsonResponse({'error': 'Message is required'}, status=400)
            
            student = request.user.studentprofile
            
            # Get conversation
            if conversation_id:
                conversation = get_object_or_404(Conversation, id=conversation_id, student=student)
            else:
                conversation, created = Conversation.objects.get_or_create(
                    student=student,
                    defaults={'title': 'Career Guidance Session'}
                )
            
            # Save user message
            user_message = Message.objects.create(
                conversation=conversation,
                content=message,
                is_from_ai=False
            )
            
            # Generate AI response
            ai_coach = AICoachService(student)
            
            # Get conversation history for context
            previous_messages = Message.objects.filter(
                conversation=conversation
            ).order_by('timestamp')[:10]
            
            history = []
            for msg in previous_messages:
                history.append({
                    'role': 'ai' if msg.is_from_ai else 'user',
                    'content': msg.content
                })
            
            ai_response_text = ai_coach.generate_ai_response(message, history)
            
            # Save AI response
            ai_message = Message.objects.create(
                conversation=conversation,
                content=ai_response_text,
                is_from_ai=True
            )
            
            # Update conversation title if it's the first message
            if conversation.title == 'Career Guidance Session' and Message.objects.filter(conversation=conversation).count() == 2:
                conversation.title = f"Chat: {message[:30]}..."
                conversation.save()
            
            return JsonResponse({
                'success': True,
                'response': ai_response_text,
                'message_id': user_message.id,
                'ai_message_id': ai_message.id,
                'conversation_id': conversation.id
            })
            
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)

class UpdateGoalsView(LoginRequiredMixin, View):
    """API endpoint to update student goals"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            goals = data.get('goals', {})
            
            student = request.user.studentprofile
            coaching_plan, created = CoachingPlan.objects.get_or_create(student=student)
            
            coaching_plan.goals = goals
            coaching_plan.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Goals updated successfully'
            })
            
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)