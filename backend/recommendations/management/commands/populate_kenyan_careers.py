from django.core.management.base import BaseCommand
from recommendations.models import Career, Subject, CareerPersonalityMatch
from assessments.models import PersonalityType

class Command(BaseCommand):
    help = 'Populate Kenyan career data with local context'
    
    def handle(self, *args, **options):
        self.populate_subjects()
        self.populate_careers()
        self.stdout.write(self.style.SUCCESS('Successfully populated Kenyan career data'))
    
    def populate_subjects(self):
        """Create common Kenyan high school subjects"""
        kenyan_subjects = [
            {'name': 'Mathematics', 'code': '121', 'category': 'sciences', 'difficulty_level': 'hard'},
            {'name': 'English', 'code': '101', 'category': 'languages', 'difficulty_level': 'medium'},
            {'name': 'Kiswahili', 'code': '102', 'category': 'languages', 'difficulty_level': 'medium'},
            {'name': 'Physics', 'code': '232', 'category': 'sciences', 'difficulty_level': 'hard'},
            {'name': 'Chemistry', 'code': '233', 'category': 'sciences', 'difficulty_level': 'hard'},
            {'name': 'Biology', 'code': '231', 'category': 'sciences', 'difficulty_level': 'medium'},
            {'name': 'Geography', 'code': '312', 'category': 'humanities', 'difficulty_level': 'medium'},
            {'name': 'History', 'code': '311', 'category': 'humanities', 'difficulty_level': 'medium'},
            {'name': 'Business Studies', 'code': '565', 'category': 'business', 'difficulty_level': 'medium'},
            {'name': 'Computer Studies', 'code': '451', 'category': 'technical', 'difficulty_level': 'medium'},
        ]
        
        for subject_data in kenyan_subjects:
            Subject.objects.get_or_create(
                code=subject_data['code'],
                defaults=subject_data
            )
        self.stdout.write("✅ Created Kenyan subjects")
    
    def populate_careers(self):
        """Create Kenyan career paths"""
        kenyan_careers = [
            {
                'name': 'Software Developer',
                'description': 'Design and develop software applications and systems for various industries.',
                'category': 'stem',
                'job_outlook': 'high',
                'kenyan_market_demand': 'growing',
                'average_salary': 120000,
                'required_subjects': ['Mathematics', 'Physics'],
                'recommended_subjects': ['Computer Studies', 'English'],
                'personality_matches': [
                    {'type': 'INTJ', 'score': 0.9},
                    {'type': 'INTP', 'score': 0.8},
                    {'type': 'ENTJ', 'score': 0.7},
                ]
            },
            {
                'name': 'Doctor',
                'description': 'Medical professional diagnosing and treating patients in healthcare settings.',
                'category': 'health', 
                'job_outlook': 'high',
                'kenyan_market_demand': 'high',
                'average_salary': 150000,
                'required_subjects': ['Biology', 'Chemistry'],
                'recommended_subjects': ['Mathematics', 'Physics', 'English'],
                'personality_matches': [
                    {'type': 'ISFJ', 'score': 0.9},
                    {'type': 'ESFJ', 'score': 0.8},
                    {'type': 'ISTJ', 'score': 0.7},
                ]
            },
            {
                'name': 'Teacher',
                'description': 'Educate students in various subjects and grade levels.',
                'category': 'education',
                'job_outlook': 'medium',
                'kenyan_market_demand': 'stable',
                'average_salary': 80000,
                'required_subjects': ['English'],
                'recommended_subjects': ['Mathematics', 'History', 'Geography'],
                'personality_matches': [
                    {'type': 'ENFJ', 'score': 0.9},
                    {'type': 'ESFJ', 'score': 0.8},
                    {'type': 'INFJ', 'score': 0.7},
                ]
            },
        ]
        
        for career_data in kenyan_careers:
            career, created = Career.objects.get_or_create(
                name=career_data['name'],
                defaults={
                    'description': career_data['description'],
                    'category': career_data['category'],
                    'job_outlook': career_data['job_outlook'],
                    'kenyan_market_demand': career_data['kenyan_market_demand'],
                    'average_salary': career_data['average_salary'],
                }
            )
            
            # Add subjects
            required_subjects = Subject.objects.filter(name__in=career_data['required_subjects'])
            recommended_subjects = Subject.objects.filter(name__in=career_data['recommended_subjects'])
            
            career.required_subjects.set(required_subjects)
            career.recommended_subjects.set(recommended_subjects)
            
            # Add personality matches
            for match in career_data['personality_matches']:
                try:
                    personality_type = PersonalityType.objects.get(mbti_type=match['type'])
                    CareerPersonalityMatch.objects.get_or_create(
                        career=career,
                        personality_type=personality_type,
                        defaults={'compatibility_score': match['score']}
                    )
                except PersonalityType.DoesNotExist:
                    continue
        
        self.stdout.write("Created Kenyan careers")