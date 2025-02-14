from django.core.management.base import BaseCommand
import random
from faker import Faker
from quiz.models import QuizCategory, Question, Answer

fake = Faker()

def create_fake_data():
    # Create 50 quiz categories if they don't exist
    for _ in range(50):
        category_name = fake.word().capitalize()
        if not QuizCategory.objects.filter(name=category_name).exists():
            category = QuizCategory.objects.create(name=category_name)

            # Create 50 questions per category (total of 2500 questions)
            difficulties = ['easy', 'medium', 'hard']
            for _ in range(50):
                question_text = fake.sentence()
                question = Question.objects.create(
                    text=question_text,
                    quiz_category=category,
                    difficulty=random.choice(difficulties)
                )

                # Create 1 correct answer and 3 incorrect answers
                correct_answer = Answer.objects.create(
                    question=question,
                    text=fake.sentence(),
                    is_correct=True
                )

                for _ in range(3):
                    Answer.objects.create(
                        question=question,
                        text=fake.sentence(),
                        is_correct=False
                    )

    print("Fake data created successfully!")

class Command(BaseCommand):
    help = 'Populates the database with fake data'

    def handle(self, *args, **kwargs):
        # Call the function that populates the data
        create_fake_data()
        self.stdout.write(self.style.SUCCESS('Successfully populated the database with fake data'))
