"""
Management command to create sample data for MedPrep
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import (
    Subject, Topic, Question, Option, UserProfile, 
    SubscriptionPlan, Note, VideoResource, Flashcard
)


class Command(BaseCommand):
    help = 'Create sample data for MedPrep application'
    
    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create subscription plans
        self.create_subscription_plans()
        
        # Create subjects and topics
        self.create_subjects_and_topics()
        
        # Create sample questions
        self.create_sample_questions()
        
        # Create sample resources
        self.create_sample_resources()
        
        # Create admin user
        self.create_admin_user()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created sample data!')
        )
    
    def create_subscription_plans(self):
        plans_data = [
            {
                'name': 'Free Plan',
                'plan_type': 'free',
                'price': 0.00,
                'duration_days': 0,
                'features': 'Basic MCQs, Limited access'
            },
            {
                'name': 'Monthly Premium',
                'plan_type': 'monthly',
                'price': 500.00,
                'duration_days': 30,
                'features': 'All MCQs, Study materials, Video lectures, Performance analytics'
            },
            {
                'name': 'Quarterly Premium',
                'plan_type': 'quarterly',
                'price': 1200.00,
                'duration_days': 90,
                'features': 'All MCQs, Study materials, Video lectures, Performance analytics, Priority support'
            },
            {
                'name': 'Yearly Premium',
                'plan_type': 'yearly',
                'price': 4000.00,
                'duration_days': 365,
                'features': 'All MCQs, Study materials, Video lectures, Performance analytics, Priority support, Exclusive content'
            }
        ]
        
        for plan_data in plans_data:
            SubscriptionPlan.objects.get_or_create(
                plan_type=plan_data['plan_type'],
                defaults=plan_data
            )
        
        self.stdout.write('Created subscription plans')
    
    def create_subjects_and_topics(self):
        subjects_data = [
            {
                'name': 'Anatomy',
                'code': 'ANAT',
                'description': 'Human anatomy and structure',
                'year_applicable': '1st',
                'topics': [
                    'Basic Histology',
                    'Cardiovascular System',
                    'Respiratory System',
                    'Nervous System',
                    'Musculoskeletal System'
                ]
            },
            {
                'name': 'Physiology',
                'code': 'PHYS',
                'description': 'Human body functions and processes',
                'year_applicable': '1st',
                'topics': [
                    'Cell Physiology',
                    'Blood and Circulation',
                    'Respiratory Physiology',
                    'Renal Physiology',
                    'Endocrine System'
                ]
            },
            {
                'name': 'Biochemistry',
                'code': 'BIOC',
                'description': 'Chemical processes in living organisms',
                'year_applicable': '1st',
                'topics': [
                    'Carbohydrate Metabolism',
                    'Protein Structure',
                    'Lipid Metabolism',
                    'Enzyme Kinetics',
                    'Molecular Biology'
                ]
            },
            {
                'name': 'Pathology',
                'code': 'PATH',
                'description': 'Study of disease processes',
                'year_applicable': '2nd',
                'topics': [
                    'General Pathology',
                    'Inflammation',
                    'Neoplasia',
                    'Immunopathology',
                    'Infectious Diseases'
                ]
            },
            {
                'name': 'Pharmacology',
                'code': 'PHAR',
                'description': 'Drug actions and interactions',
                'year_applicable': '2nd',
                'topics': [
                    'General Pharmacology',
                    'Autonomic Drugs',
                    'Cardiovascular Drugs',
                    'Antimicrobials',
                    'CNS Drugs'
                ]
            },
            {
                'name': 'Internal Medicine',
                'code': 'MED',
                'description': 'Internal medicine and clinical practice',
                'year_applicable': '3rd',
                'topics': [
                    'Cardiology',
                    'Gastroenterology',
                    'Pulmonology',
                    'Nephrology',
                    'Endocrinology'
                ]
            }
        ]
        
        for subject_data in subjects_data:
            subject, created = Subject.objects.get_or_create(
                code=subject_data['code'],
                defaults={
                    'name': subject_data['name'],
                    'description': subject_data['description'],
                    'year_applicable': subject_data['year_applicable']
                }
            )
            
            for i, topic_name in enumerate(subject_data['topics']):
                Topic.objects.get_or_create(
                    subject=subject,
                    name=topic_name,
                    defaults={'order': i + 1}
                )
        
        self.stdout.write('Created subjects and topics')
    
    def create_sample_questions(self):
        # Get some topics
        topics = Topic.objects.all()[:10]
        
        questions_data = [
            {
                'text': 'Which of the following is the powerhouse of the cell?',
                'options': [
                    ('Nucleus', False),
                    ('Mitochondria', True),
                    ('Ribosome', False),
                    ('Endoplasmic Reticulum', False)
                ],
                'explanation': 'Mitochondria are known as the powerhouse of the cell because they produce ATP through cellular respiration.',
                'difficulty': 'easy'
            },
            {
                'text': 'What is the normal heart rate for a healthy adult at rest?',
                'options': [
                    ('40-50 beats per minute', False),
                    ('60-100 beats per minute', True),
                    ('120-140 beats per minute', False),
                    ('150-180 beats per minute', False)
                ],
                'explanation': 'The normal resting heart rate for adults ranges from 60 to 100 beats per minute.',
                'difficulty': 'easy'
            },
            {
                'text': 'Which enzyme is responsible for breaking down starch?',
                'options': [
                    ('Pepsin', False),
                    ('Lipase', False),
                    ('Amylase', True),
                    ('Trypsin', False)
                ],
                'explanation': 'Amylase is the enzyme that breaks down starch into simpler sugars.',
                'difficulty': 'medium'
            }
        ]
        
        for topic in topics:
            for q_data in questions_data:
                question = Question.objects.create(
                    topic=topic,
                    question_text=q_data['text'],
                    explanation=q_data['explanation'],
                    difficulty=q_data['difficulty']
                )
                
                for i, (option_text, is_correct) in enumerate(q_data['options']):
                    Option.objects.create(
                        question=question,
                        option_text=option_text,
                        is_correct=is_correct,
                        order=i + 1
                    )
        
        self.stdout.write('Created sample questions')
    
    def create_sample_resources(self):
        topics = Topic.objects.all()[:5]
        
        for topic in topics:
            # Create a sample note
            Note.objects.get_or_create(
                topic=topic,
                title=f"Study Notes: {topic.name}",
                defaults={
                    'content': f'<h3>Introduction to {topic.name}</h3><p>This is a comprehensive guide to understanding {topic.name}. These notes cover the essential concepts and key points you need to know for your exams.</p>',
                    'created_by': User.objects.first() or User.objects.create_user('admin', 'admin@example.com', 'admin123')
                }
            )
            
            # Create sample flashcards
            flashcards_data = [
                ('What is the definition?', f'The definition of {topic.name} is...'),
                ('Key concept', f'Important concept in {topic.name}'),
                ('Clinical significance', f'Clinical importance of {topic.name}')
            ]
            
            for front, back in flashcards_data:
                Flashcard.objects.get_or_create(
                    topic=topic,
                    front_text=front,
                    defaults={
                        'back_text': back,
                        'created_by': User.objects.first()
                    }
                )
            
            # Create sample video
            VideoResource.objects.get_or_create(
                topic=topic,
                title=f"Video Lecture: {topic.name}",
                defaults={
                    'description': f'Comprehensive video lecture covering {topic.name}',
                    'video_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                    'duration_minutes': 45,
                    'created_by': User.objects.first()
                }
            )
        
        self.stdout.write('Created sample resources')
    
    def create_admin_user(self):
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@medprep.com',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            
            UserProfile.objects.create(
                user=admin_user,
                year_of_study='1st',
                college_name='MedPrep Administration',
                is_premium=True
            )
            
            self.stdout.write('Created admin user (admin/admin123)')
        else:
            self.stdout.write('Admin user already exists')
