from django.db import models
from users.models import StudentProfile

class Conversation(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.student.user.username}"

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    is_from_ai = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['timestamp']

class CoachingPlan(models.Model):
    student = models.OneToOneField(StudentProfile, on_delete=models.CASCADE)
    personality_type = models.ForeignKey('assessments.PersonalityType', on_delete=models.CASCADE)
    learning_style = models.ForeignKey('recommendations.LearningStyle', on_delete=models.CASCADE)
    goals = models.JSONField(default=dict)  # Store student goals
    challenges = models.JSONField(default=list)  # Store identified challenges
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Coaching Plan for {self.student.user.username}"

class ResourceRecommendation(models.Model):
    coaching_plan = models.ForeignKey(CoachingPlan, on_delete=models.CASCADE, related_name='resources')
    title = models.CharField(max_length=200)
    description = models.TextField()
    url = models.URLField(blank=True)
    resource_type = models.CharField(max_length=50, choices=[
        ('article', 'Article'),
        ('video', 'Video'),
        ('book', 'Book'),
        ('course', 'Online Course'),
        ('tool', 'Tool/Software'),
    ])
    relevance_score = models.DecimalField(max_digits=3, decimal_places=2)
    
    def __str__(self):
        return self.title