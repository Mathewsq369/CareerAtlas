from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Load all initial data for CareerAtlas'
    
    def handle(self, *args, **options):
        self.stdout.write('Loading initial data for CareerAtlas Kenya...')
        
        # Load data in correct order to maintain foreign key relationships
        call_command('populate_mbti_data')
        call_command('populate_learning_styles')
        call_command('populate_kenyan_careers')
        call_command('populate_sample_questions')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully loaded all initial data!')
        )