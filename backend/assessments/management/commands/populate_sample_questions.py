from django.core.management.base import BaseCommand
from assessments.models import Question, AnswerChoice

class Command(BaseCommand):
    help = 'Populate sample assessment questions'
    
    def handle(self, *args, **options):
        questions_data = [
            {
                'text': 'At social events, you usually:',
                'category': 'EI',
                'choices': [
                    {'text': 'Interact with many people, including strangers', 'value': 3},
                    {'text': 'Interact with a few people you know well', 'value': -3},
                    {'text': 'Try to avoid social interactions', 'value': -2},
                    {'text': 'Enjoy meeting new people', 'value': 2},
                ]
            },
            {
                'text': 'When learning something new, you prefer:',
                'category': 'SN',
                'choices': [
                    {'text': 'Practical, hands-on experience', 'value': 3},
                    {'text': 'Theoretical concepts and big ideas', 'value': -3},
                    {'text': 'Step-by-step instructions', 'value': 1},
                    {'text': 'Understanding the overall meaning', 'value': -2},
                ]
            },
            {
                'text': 'When making decisions, you typically:',
                'category': 'TF',
                'choices': [
                    {'text': 'Consider what is logical and reasonable', 'value': 3},
                    {'text': 'Consider how it will affect people emotionally', 'value': -3},
                    {'text': 'Weigh both logic and emotions equally', 'value': 0},
                    {'text': 'Go with your gut feeling', 'value': -1},
                ]
            },
            {
                'text': 'In your daily life, you prefer:',
                'category': 'JP',
                'choices': [
                    {'text': 'Having a clear plan and schedule', 'value': 3},
                    {'text': 'Keeping your options open and flexible', 'value': -3},
                    {'text': 'A balance of structure and spontaneity', 'value': 0},
                    {'text': 'Going with the flow as things happen', 'value': -2},
                ]
            },
            {
                'text': 'When working on projects, you are more likely to:',
                'category': 'JP',
                'choices': [
                    {'text': 'Start early and work steadily', 'value': 3},
                    {'text': 'Work in bursts of energy near the deadline', 'value': -3},
                    {'text': 'Set intermediate deadlines for yourself', 'value': 1},
                    {'text': 'Wait for inspiration to strike', 'value': -2},
                ]
            },
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
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {len(questions_data)} sample questions'))