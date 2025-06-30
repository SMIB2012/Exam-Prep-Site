"""
Management command to import questions from various sources
"""
from django.core.management.base import BaseCommand
from django.core.files import File
import json
import csv
from core.models import Subject, Topic, Question, QuestionOption


class Command(BaseCommand):
    help = 'Import questions from JSON or CSV files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='Path to the file containing questions',
            required=True
        )
        parser.add_argument(
            '--format',
            type=str,
            choices=['json', 'csv'],
            help='File format (json or csv)',
            default='json'
        )
        parser.add_argument(
            '--subject',
            type=str,
            help='Subject code or name',
            required=True
        )

    def handle(self, *args, **options):
        file_path = options['file']
        file_format = options['format']
        subject_identifier = options['subject']
        
        try:
            # Get or create subject
            try:
                subject = Subject.objects.get(code=subject_identifier)
            except Subject.DoesNotExist:
                try:
                    subject = Subject.objects.get(name=subject_identifier)
                except Subject.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(f'Subject "{subject_identifier}" not found')
                    )
                    return
            
            if file_format == 'json':
                self.import_from_json(file_path, subject)
            elif file_format == 'csv':
                self.import_from_csv(file_path, subject)
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error importing questions: {str(e)}')
            )

    def import_from_json(self, file_path, subject):
        """Import questions from JSON file"""
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            
        questions_created = 0
        
        for item in data:
            # Get or create topic
            topic_name = item.get('topic', 'General')
            topic, created = Topic.objects.get_or_create(
                subject=subject,
                name=topic_name,
                defaults={'description': f'{topic_name} questions'}
            )
            
            # Create question
            question = Question.objects.create(
                topic=topic,
                question_text=item['question'],
                difficulty=item.get('difficulty', 'MEDIUM'),
                explanation=item.get('explanation', '')
            )
            
            # Create options
            options = item['options']
            correct_option_index = item.get('correct_answer', 0)
            
            for i, option_text in enumerate(options):
                QuestionOption.objects.create(
                    question=question,
                    option_text=option_text,
                    is_correct=(i == correct_option_index)
                )
            
            questions_created += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully imported {questions_created} questions')
        )

    def import_from_csv(self, file_path, subject):
        """Import questions from CSV file"""
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            questions_created = 0
            
            for row in reader:
                # Get or create topic
                topic_name = row.get('topic', 'General')
                topic, created = Topic.objects.get_or_create(
                    subject=subject,
                    name=topic_name,
                    defaults={'description': f'{topic_name} questions'}
                )
                
                # Create question
                question = Question.objects.create(
                    topic=topic,
                    question_text=row['question'],
                    difficulty=row.get('difficulty', 'MEDIUM'),
                    explanation=row.get('explanation', '')
                )
                
                # Create options (assuming columns: option_a, option_b, option_c, option_d)
                options = [
                    row.get('option_a', ''),
                    row.get('option_b', ''),
                    row.get('option_c', ''),
                    row.get('option_d', '')
                ]
                
                correct_answer = row.get('correct_answer', 'A').upper()
                correct_index = ord(correct_answer) - ord('A')
                
                for i, option_text in enumerate(options):
                    if option_text:  # Only create non-empty options
                        QuestionOption.objects.create(
                            question=question,
                            option_text=option_text,
                            is_correct=(i == correct_index)
                        )
                
                questions_created += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully imported {questions_created} questions from CSV')
        )
