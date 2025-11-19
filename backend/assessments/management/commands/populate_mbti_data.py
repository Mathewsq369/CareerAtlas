from django.core.management.base import BaseCommand
from assessments.models import PersonalityType, MBTIDimension

class Command(BaseCommand):
    help = 'Populate MBTI personality types and dimensions'
    
    def handle(self, *args, **options):
        self.populate_dimensions()
        self.populate_personality_types()
        self.stdout.write(self.style.SUCCESS('Successfully populated MBTI data'))
    
    def populate_dimensions(self):
        """Create MBTI dimensions"""
        dimensions = [
            {'code': 'EI', 'dimension_a': 'Extraversion', 'dimension_b': 'Introversion', 'description': 'How you interact with others and where you get energy'},
            {'code': 'SN', 'dimension_a': 'Sensing', 'dimension_b': 'Intuition', 'description': 'How you process information and perceive the world'},
            {'code': 'TF', 'dimension_a': 'Thinking', 'dimension_b': 'Feeling', 'description': 'How you make decisions and evaluate information'},
            {'code': 'JP', 'dimension_a': 'Judging', 'dimension_b': 'Perceiving', 'description': 'How you approach life and structure your world'},
        ]
        
        for dim_data in dimensions:
            MBTIDimension.objects.get_or_create(
                code=dim_data['code'],
                defaults=dim_data
            )
        self.stdout.write("Created MBTI dimensions")
    
    def populate_personality_types(self):
        """Create personality types"""
        personality_types = [
            {
                'mbti_type': 'INTJ',
                'name': 'The Architect',
                'description': 'Imaginative and strategic thinkers, with a plan for everything.',
                'strengths': 'Rational, informed, independent, determined, curious',
                'weaknesses': 'Arrogant, dismissive of emotions, overly critical',
                'career_recommendations': 'Scientists, engineers, professors, judges, managers'
            },
            {
                'mbti_type': 'INTP',
                'name': 'The Logician', 
                'description': 'Innovative inventors with an unquenchable thirst for knowledge.',
                'strengths': 'Analytical, original, open-minded, curious, objective',
                'weaknesses': 'Insensitive, absent-minded, condescending, impatient',
                'career_recommendations': 'Physicists, programmers, mathematicians, philosophers'
            },
            {
                'mbti_type': 'ENTJ',
                'name': 'The Commander',
                'description': 'Bold, imaginative and strong-willed leaders, always finding a way.',
                'strengths': 'Efficient, energetic, self-confident, strong-willed, strategic',
                'weaknesses': 'Impatient, stubborn, dominant, intolerant',
                'career_recommendations': 'CEOs, entrepreneurs, lawyers, consultants'
            },
            {
                'mbti_type': 'ENTP',
                'name': 'The Debater',
                'description': 'Smart and curious thinkers who cannot resist an intellectual challenge.',
                'strengths': 'Knowledgeable, quick-thinking, original, excellent brainstormers',
                'weaknesses': 'Argumentative, insensitive, intolerant',
                'career_recommendations': 'Entrepreneurs, lawyers, psychologists, engineers'
            },
            {
                'mbti_type': 'INFJ',
                'name': 'The Advocate',
                'description': 'Quiet and mystical, yet very inspiring and tireless idealists.',
                'strengths': 'Creative, insightful, principled, passionate, altruistic',
                'weaknesses': 'Sensitive, extremely private, perfectionistic',
                'career_recommendations': 'Counselors, psychologists, writers, human resources'
            },
            {
                'mbti_type': 'INFP',
                'name': 'The Mediator',
                'description': 'Poetic, kind and altruistic people, always eager to help a good cause.',
                'strengths': 'Empathetic, creative, idealistic, passionate, open-minded',
                'weaknesses': 'Unrealistic, self-isolating, unfocused',
                'career_recommendations': 'Writers, artists, psychologists, social workers'
            },
            {
                'mbti_type': 'ENFJ',
                'name': 'The Protagonist',
                'description': 'Charismatic and inspiring leaders, able to mesmerize their listeners.',
                'strengths': 'Natural leaders, passionate, reliable, charismatic',
                'weaknesses': 'Overly idealistic, too selfless, fluctuating self-esteem',
                'career_recommendations': 'Teachers, consultants, psychologists, sales'
            },
            {
                'mbti_type': 'ENFP',
                'name': 'The Campaigner',
                'description': 'Enthusiastic, creative and sociable free spirits, who can always find a reason to smile.',
                'strengths': 'Curious, perceptive, enthusiastic, excellent communicators',
                'weaknesses': 'Poor practical skills, unfocused, easily stressed',
                'career_recommendations': 'Actors, journalists, consultants, entrepreneurs'
            },
        ]
        
        for type_data in personality_types:
            PersonalityType.objects.get_or_create(
                mbti_type=type_data['mbti_type'],
                defaults=type_data
            )
        self.stdout.write("Created personality types")