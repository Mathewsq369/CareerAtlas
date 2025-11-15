from django.contrib import admin
from .models import (
    MBTIDimension, Question, AnswerChoice, AssessmentSession,
    QuestionResponse, PersonalityType, AssessmentResult
)

@admin.register(MBTIDimension)
class MBTIDimensionAdmin(admin.ModelAdmin):
    list_display = ['code', 'dimension_a', 'dimension_b']

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'category']
    list_filter = ['category']
    search_fields = ['text']

@admin.register(AnswerChoice)
class AnswerChoiceAdmin(admin.ModelAdmin):
    list_display = ['question', 'text', 'value']
    list_filter = ['question__category']

class QuestionResponseInline(admin.TabularInline):
    model = QuestionResponse
    extra = 0

@admin.register(AssessmentSession)
class AssessmentSessionAdmin(admin.ModelAdmin):
    list_display = ['student', 'started_at', 'completed_at', 'is_completed']
    list_filter = ['is_completed', 'started_at']
    inlines = [QuestionResponseInline]

@admin.register(PersonalityType)
class PersonalityTypeAdmin(admin.ModelAdmin):
    list_display = ['mbti_type', 'name']
    search_fields = ['mbti_type', 'name']

@admin.register(AssessmentResult)
class AssessmentResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'personality_type', 'confidence', 'created_at']
    list_filter = ['personality_type', 'created_at']
    search_fields = ['student__user__username']