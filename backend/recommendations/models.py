from django.db import models
from assessments.models import PersonalityType

class Career(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=100, choices=[
        ('stem', 'STEM'),
        ('arts', 'Arts & Humanities'),
        ('business', 'Business & Commerce'),
        ('health', 'Health Sciences'),
        ('education', 'Education'),
        ('technical', 'Technical & Vocational'),
    ])
    required_subjects = models.ManyToManyField('Subject', related_name='careers_requiring')
    recommended_subjects = models.ManyToManyField('Subject', related_name='careers_recommending')
    personality_types = models.ManyToManyField(PersonalityType, through='CareerPersonalityMatch')
    average_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    job_outlook = models.CharField(max_length=50, choices=[
        ('high', 'High Demand'),
        ('medium', 'Medium Demand'),
        ('low', 'Low Demand'),
    ])
    kenyan_market_demand = models.CharField(max_length=50, choices=[
        ('growing', 'Growing'),
        ('stable', 'Stable'),
        ('declining', 'Declining'),
    ])
    
    def __str__(self):
        return self.name

class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)  # KCSE subject code
    category = models.CharField(max_length=50, choices=[
        ('sciences', 'Sciences'),
        ('humanities', 'Humanities'),
        ('languages', 'Languages'),
        ('technical', 'Technical'),
        ('business', 'Business'),
    ])
    difficulty_level = models.CharField(max_length=20, choices=[
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ])
    
    def __str__(self):
        return self.name

class CareerPersonalityMatch(models.Model):
    career = models.ForeignKey(Career, on_delete=models.CASCADE)
    personality_type = models.ForeignKey(PersonalityType, on_delete=models.CASCADE)
    compatibility_score = models.DecimalField(max_digits=3, decimal_places=2)  # 0.00-1.00
    reasoning = models.TextField()
    
    class Meta:
        unique_together = ['career', 'personality_type']

class LearningStyle(models.Model):
    STYLE_CHOICES = [
        ('visual', 'Visual'),
        ('auditory', 'Auditory'),
        ('reading', 'Reading/Writing'),
        ('kinesthetic', 'Kinesthetic'),
    ]
    
    name = models.CharField(max_length=50, choices=STYLE_CHOICES)
    description = models.TextField()
    #personality_types = models.ManyToManyField(PersonalityType)
    study_recommendations = models.TextField()
    
    def __str__(self):
        return self.name

class StudentRecommendation(models.Model):
    student = models.ForeignKey('users.StudentProfile', on_delete=models.CASCADE)
    career = models.ForeignKey(Career, on_delete=models.CASCADE)
    personality_match_score = models.DecimalField(max_digits=3, decimal_places=2)
    academic_match_score = models.DecimalField(max_digits=3, decimal_places=2, null=True)
    overall_score = models.DecimalField(max_digits=3, decimal_places=2)
    reasoning = models.TextField()
    recommended_subjects = models.ManyToManyField(Subject)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['student', 'career']