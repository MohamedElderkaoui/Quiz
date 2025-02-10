from django.core.management.base import BaseCommand
import openai
from quiz.models import Question, Answer, QuizCategory
from quiz.app_add_generate_questions_with_api_openai import generate_questions_from_openai, save_questions_to_db
import os

class Command(BaseCommand):
    help = "Generates multiple-choice questions from OpenAI and saves them to the database."

    def add_arguments(self, parser):
        parser.add_argument("--category", type=str, default="General Knowledge", help="Category of the questions.")
        parser.add_argument("--difficulty", type=str, choices=["easy", "medium", "hard"], default="easy", help="Difficulty level.")
        parser.add_argument("--num_questions", type=int, default=5, help="Number of questions to generate.")

    def handle(self, *args, **options):
        category = options["category"]
        difficulty = options["difficulty"]
        num_questions = options["num_questions"]

        openai.api_key = os.getenv('OPENAI_API_KEY')
        if not openai.api_key:
            self.stdout.write(self.style.ERROR("Error: OPENAI_API_KEY no está configurada."))
            return

        prompt = f"""
        Generate {num_questions} multiple-choice questions on {category}.
        Each question should have 4 possible answers, with one correct answer.
        Format the response as a JSON array with the following structure:
        [
          {{
            "question": "Example question?",
            "answers": [
              {{"text": "Option 1", "is_correct": true}},
              {{"text": "Option 2", "is_correct": false}},
              {{"text": "Option 3", "is_correct": false}},
              {{"text": "Option 4", "is_correct": false}}
            ],
            "difficulty": "{difficulty}",
            "category": "{category}"
          }}
        ]
        """

        questions = generate_questions_from_openai(prompt, num_questions)

        if questions:
            save_questions_to_db(questions)
            self.stdout.write(self.style.SUCCESS(f"Se generaron y guardaron {len(questions)} preguntas en la categoría '{category}' con dificultad '{difficulty}'"))
        else:
            self.stdout.write(self.style.ERROR("No se generaron preguntas."))
