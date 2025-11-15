from django.contrib import admin
from .models import Conversation, Message, CoachingPlan, ResourceRecommendation

class MessageInline(admin.TabularInline):
    model = Message
    extra = 0

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['student', 'title', 'created_at', 'updated_at']
    list_filter = ['created_at']
    inlines = [MessageInline]

@admin.register(CoachingPlan)
class CoachingPlanAdmin(admin.ModelAdmin):
    list_display = ['student', 'personality_type', 'learning_style', 'created_at']
    list_filter = ['created_at']

@admin.register(ResourceRecommendation)
class ResourceRecommendationAdmin(admin.ModelAdmin):
    list_display = ['title', 'coaching_plan', 'resource_type', 'relevance_score']
    list_filter = ['resource_type']