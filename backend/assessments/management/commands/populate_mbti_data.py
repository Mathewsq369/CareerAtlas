from django.core.management.base import BaseCommand
from assessments.models import PersonalityType, MBTIDimension, Question, AnswerChoice

class Command(BaseCommand):
    help = 'Populate MBTI personality types and questions'
    
    def handle(self, *args, **options):
        self.populate_dimensions()
        self.populate_personality_types()
        self.populate_questions()
        self.stdout.write(self.style.SUCCESS('Successfully populated MBTI data'))
    
    def populate_dimensions(self):
        dimensions = [
            {
                'code': 'EI',
                'dimension_a': 'Extraversion',
                'dimension_b': 'Introversion',
                'description': 'How you interact with others and where you get energy'
            },
            {
                'code': 'SN', 
                'dimension_a': 'Sensing',
                'dimension_b': 'Intuition',
                'description': 'How you process information and perceive the world'
            },
            {
                'code': 'TF',
                'dimension_a': 'Thinking', 
                'dimension_b': 'Feeling',
                'description': 'How you make decisions and evaluate information'
            },
            {
                'code': 'JP',
                'dimension_a': 'Judging',
                'dimension_b': 'Perceiving', 
                'description': 'How you approach life and structure your world'
            },
        ]
        
        for dim_data in dimensions:
            MBTIDimension.objects.update_or_create(
                code=dim_data['code'],
                defaults=dim_data
            )
    
    def populate_personality_types(self):
        # Sample personality types data (simplified)
        types_data = [
            {
                'mbti_type': 'INTJ',
                'name': 'The Architect',
                'description': 'Innovative, strategic thinkers with a plan for everything.',
                'strengths': 'Strategic, knowledgeable, determined, independent',
                'weaknesses': 'Arrogant, dismissive of emotions, overly critical',
                'career_recommendations': 'Scientists, engineers, professors, judges'
            },
            # Add all 16 types here...
        ]
        
        for type_data in types_data:
            PersonalityType.objects.update_or_create(
                mbti_type=type_data['mbti_type'],
                defaults=type_data
            )