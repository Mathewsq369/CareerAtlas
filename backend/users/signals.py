from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import StudentProfile

User = get_user_model()

@receiver(post_save, sender=User)
def create_student_profile(sender, instance, created, **kwargs):
    """Automatically create a student profile when a new user is created"""
    if created and instance.user_type == 'student':
        StudentProfile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_student_profile(sender, instance, **kwargs):
    """Save the student profile when the user is saved"""
    if hasattr(instance, 'studentprofile'):
        instance.studentprofile.save()