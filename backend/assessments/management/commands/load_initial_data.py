from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Load all initial data for EduPersona'
    
    def handle(self, *args, **options):
        self.stdout.write('Loading initial data for EduPersona Kenya...')
        
        # Load MBTI data
        call_command('populate_mbti_data')
        
        # Load Kenyan careers
        call_command('populate_kenyan_careers')
        
        # Load sample questions
        call_command('populate_sample_questions')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully loaded all initial data!')
        )