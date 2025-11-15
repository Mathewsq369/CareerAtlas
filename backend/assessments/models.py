from django.db import models
from users.models import CustomUser, StudentProfile

class MBTIDimension(models.Model):
    DIMENSION_CHOICES = [
        ('EI', 'Extraversion vs Introversion'),
        ('SN', 'Sensing vs Intuition'),
        ('TF', 'Thinking vs Feeling'),
        ('JP', 'Judging vs Perceiving'),
    ]
    
    code = models.CharField(max_length=2, choices=DIMENSION_CHOICES, unique=True)
    dimension_a = models.CharField(max_length=50)  # Extraversion
    dimension_b = models.CharField(max_length=50)  # Introversion
    description = models.TextField()
    
    def __str__(self):
        return f"{self.dimension_a} vs {self.dimension_b}"

class Question(models.Model):
    CATEGORY_CHOICES = [
        ('EI', 'Extraversion/Introversion'),
        ('SN', 'Sensing/Intuition'),
        ('TF', 'Thinking/Feeling'),
        ('JP', 'Judging/Perceiving'),
    ]
    
    text = models.TextField()
    category = models.CharField(max_length=2, choices=CATEGORY_CHOICES)
    dimension_a_weight = models.IntegerField(default=0)  # Positive for dimension A
    dimension_b_weight = models.IntegerField(default=0)  # Positive for dimension B
    
    def __str__(self):
        return f"{self.text[:50]}... ({self.category})"

class AnswerChoice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=200)
    value = models.IntegerField()  # -3 to +3 scale
    
    def __str__(self):
        return f"{self.text} (Value: {self.value})"

class AssessmentSession(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Assessment for {self.student.user.username}"

class QuestionResponse(models.Model):
    session = models.ForeignKey(AssessmentSession, on_delete=models.CASCADE, related_name='responses')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.ForeignKey(AnswerChoice, on_delete=models.CASCADE)
    response_time = models.IntegerField(default=0)  # Time taken in seconds
    
    class Meta:
        unique_together = ['session', 'question']

class PersonalityType(models.Model):
    mbti_type = models.CharField(max_length=4, unique=True)  # INTJ, ENFP, etc.
    name = models.CharField(max_length=100)  # "The Architect", "The Campaigner"
    description = models.TextField()
    strengths = models.TextField()
    weaknesses = models.TextField()
    career_recommendations = models.TextField()
    
    def __str__(self):
        return f"{self.mbti_type} - {self.name}"

class AssessmentResult(models.Model):
    student = models.OneToOneField(StudentProfile, on_delete=models.CASCADE)
    personality_type = models.ForeignKey(PersonalityType, on_delete=models.CASCADE)
    ei_score = models.DecimalField(max_digits=5, decimal_places=2)  # Extraversion-Introversion
    sn_score = models.DecimalField(max_digits=5, decimal_places=2)  # Sensing-Intuition
    tf_score = models.DecimalField(max_digits=5, decimal_places=2)  # Thinking-Feeling
    jp_score = models.DecimalField(max_digits=5, decimal_places=2)  # Judging-Perceiving
    confidence = models.DecimalField(max_digits=3, decimal_places=2)  # 0.00-1.00
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.student.user.username} - {self.personality_type.mbti_type}"