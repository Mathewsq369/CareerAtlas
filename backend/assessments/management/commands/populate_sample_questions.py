from django.core.management.base import BaseCommand
from assessments.models import Question, AnswerChoice

class Command(BaseCommand):
    help = 'Populate sample assessment questions'
    
    def handle(self, *args, **options):
        questions_data = [
            {
                'text': 'At a party, do you typically:',
                'category': 'EI',
                'choices': [
                    {'text': 'Interact with many people, including strangers', 'value': 3},
                    {'text': 'Interact with a few people you know well', 'value': -3},
                    {'text': 'Have deep conversations with a small group', 'value': -2},
                    {'text': 'Circulate and meet new people', 'value': 2},
                    {'text': 'Stay with people you came with', 'value': -1},
                ]
            },
            {
                'text': 'When learning something new, you prefer:',
                'category': 'SN',
                'choices': [
                    {'text': 'Practical, hands-on experience', 'value': 3},
                    {'text': 'Theoretical concepts and big ideas', 'value': -3},
                    {'text': 'Step-by-step instructions', 'value': 2},
                    {'text': 'Understanding the overall meaning', 'value': -2},
                    {'text': 'A mix of theory and practice', 'value': 0},
                ]
            },
            # Add 58 more questions following this pattern...
        ]
        
        for q_data in questions_data:
            question, created = Question.objects.get_or_create(
                text=q_data['text'],
                category=q_data['category'],
                defaults={
                    'dimension_a_weight': 1,
                    'dimension_b_weight': 1
                }
            )
            
            for choice_data in q_data['choices']:
                AnswerChoice.objects.get_or_create(
                    question=question,
                    text=choice_data['text'],
                    defaults={'value': choice_data['value']}
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {len(questions_data)} questions')
        )