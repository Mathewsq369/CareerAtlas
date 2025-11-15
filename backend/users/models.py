from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('admin', 'Administrator'),
        ('school', 'School'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='student')
    phone_number = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.username} ({self.user_type})"

class StudentProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    school = models.ForeignKey('School', on_delete=models.SET_NULL, null=True)
    grade_level = models.CharField(max_length=50)  # Form 1-4, College year, etc.
    subjects = models.ManyToManyField('Subject', blank=True)
    career_aspirations = models.TextField(blank=True)
    kcpe_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    kcse_score = models.CharField(max_length=10, blank=True)  # A, A-, B+, etc.
    
    def __str__(self):
        return f"Student Profile: {self.user.username}"

class School(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20, unique=True)  # KNEC school code
    county = models.CharField(max_length=100)
    type = models.CharField(max_length=50, choices=[
        ('national', 'National'),
        ('county', 'County'),
        ('private', 'Private'),
    ])
    
    def __str__(self):
        return self.name