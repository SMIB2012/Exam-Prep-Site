from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import UserProfile
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Create test users for the admin panel'

    def handle(self, *args, **options):
        test_users = [
            {
                'username': 'jane_doe',
                'first_name': 'Jane',
                'last_name': 'Doe',
                'email': 'jane.doe@medprep.com',
                'is_active': True,
                'profile': {
                    'year_of_study': '2nd_year',
                    'province': 'Punjab',
                    'college_type': 'Public',
                    'college_name': 'King Edward Medical University',
                    'phone_number': '+92-300-1111111',
                    'is_premium': True,
                    'premium_expires_at': timezone.now() + timedelta(days=30)
                }
            },
            {
                'username': 'ali_hassan',
                'first_name': 'Ali',
                'last_name': 'Hassan',
                'email': 'ali.hassan@medprep.com',
                'is_active': True,
                'profile': {
                    'year_of_study': '3rd_year',
                    'province': 'Sindh',
                    'college_type': 'Private',
                    'college_name': 'Aga Khan University',
                    'phone_number': '+92-321-2222222',
                    'is_premium': False,
                }
            },
            {
                'username': 'sara_ahmed',
                'first_name': 'Sara',
                'last_name': 'Ahmed',
                'email': 'sara.ahmed@medprep.com',
                'is_active': False,
                'profile': {
                    'year_of_study': '1st_year',
                    'province': 'KPK',
                    'college_type': 'Public',
                    'college_name': 'Khyber Medical University',
                    'phone_number': '+92-333-3333333',
                    'is_premium': False,
                }
            },
        ]

        self.stdout.write("Creating test users...")
        
        for user_data in test_users:
            # Check if user already exists
            if User.objects.filter(username=user_data['username']).exists():
                self.stdout.write(f"User {user_data['username']} already exists, skipping...")
                continue
                
            # Create user
            user = User.objects.create_user(
                username=user_data['username'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                email=user_data['email'],
                password='testpass123',
                is_active=user_data['is_active']
            )
            
            # Create or get profile
            profile_data = user_data['profile']
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'year_of_study': profile_data['year_of_study'],
                    'province': profile_data['province'],
                    'college_type': profile_data['college_type'],
                    'college_name': profile_data['college_name'],
                    'phone_number': profile_data['phone_number'],
                    'is_premium': profile_data['is_premium'],
                    'premium_expires_at': profile_data.get('premium_expires_at'),
                    'total_quiz_score': 0,
                    'total_quizzes_taken': 0,
                }
            )
            
            self.stdout.write(
                self.style.SUCCESS(f"Created user: {user.username} ({user.get_full_name()})")
            )
        
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        premium_users = User.objects.filter(userprofile__is_premium=True).count()
        
        self.stdout.write(f"\nSummary:")
        self.stdout.write(f"Total users: {total_users}")
        self.stdout.write(f"Active users: {active_users}")
        self.stdout.write(f"Premium users: {premium_users}")
