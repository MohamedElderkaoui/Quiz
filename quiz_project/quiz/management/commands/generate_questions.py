# quiz/management/commands/generate_questions.py

from django.core.management.base import BaseCommand
import os
import openai
from quiz.models import Question, Answer
from quiz.app_add_generate_questions_with_api_openai import generate_questions_from_openai, save_questions_to_db

class Command(BaseCommand):
    help = "Generates questions from OpenAI and saves them to the database"

    def handle(self, *args, **kwargs):
        # Asegurarse de que la API Key está configurada correctamente
        openai.api_key = os.getenv('OPENAI_API_KEY')
        if not openai.api_key:
            self.stdout.write(self.style.ERROR("Error: OPENAI_API_KEY no está configurada."))
            return

        # Definir el prompt para generar preguntas
        prompt = "Generate 5 multiple-choice questions on general knowledge with answers."

        # Generar preguntas usando OpenAI
        questions = generate_questions_from_openai(prompt, num_questions=5)

        if questions:
            # Guardar preguntas en la base de datos
            save_questions_to_db(questions, category="General Knowledge", difficulty="easy")
            self.stdout.write(self.style.SUCCESS(f"Se generaron y guardaron {len(questions)} preguntas."))
        else:
            self.stdout.write(self.style.ERROR("No se generaron preguntas."))
