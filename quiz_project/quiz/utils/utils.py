import random
from faker import Faker
from quiz.models import QuizCategory, Question, Answer

fake = Faker()

def create_fake_data():
    # Create 50 quiz categories
    categories = []
    for _ in range(50):
        category = QuizCategory.objects.create(name=fake.word().capitalize())
        categories.append(category)

    # Create 50 questions per category (total of 2500 questions)
    difficulties = ['easy', 'medium', 'hard']
    for category in categories:
        for _ in range(50):
            question = Question.objects.create(
                text=fake.sentence(),
                quiz_category=category,
                difficulty=random.choice(difficulties)
            )
            
            # Create 4 answers per question (one correct and three incorrect)
            correct_answer = Answer.objects.create(question=question, text=fake.sentence(), is_correct=True)
            for _ in range(3):
                Answer.objects.create(question=question, text=fake.sentence(), is_correct=False)

    print("Fake data created successfully!")
