from django.contrib import admin
from .models import Career, Subject, CareerPersonalityMatch, LearningStyle, StudentRecommendation

@admin.register(Career)
class CareerAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'job_outlook', 'kenyan_market_demand']
    list_filter = ['category', 'job_outlook', 'kenyan_market_demand']
    search_fields = ['name', 'description']
    filter_horizontal = ['required_subjects', 'recommended_subjects', 'personality_types']

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'category', 'difficulty_level']
    list_filter = ['category', 'difficulty_level']
    search_fields = ['name', 'code']

@admin.register(LearningStyle)
class LearningStyleAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    filter_horizontal = ['personality_types']

@admin.register(StudentRecommendation)
class StudentRecommendationAdmin(admin.ModelAdmin):
    list_display = ['student', 'career', 'overall_score', 'created_at']
    list_filter = ['created_at']
    search_fields = ['student__user__username', 'career__name']