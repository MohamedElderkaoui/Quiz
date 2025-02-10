import openai
import os
import json
from dotenv import load_dotenv
from quiz.models import Question, Answer, QuizCategory

# Cargar variables de entorno una sola vez
load_dotenv()

# Configurar clave de OpenAI
openai.api_key = os.environ.get("OPENAI_API_KEY")

def generate_questions_from_openai(prompt, num_questions=5):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Asegúrate de que este modelo exista
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=700,
            temperature=0.7
        )
        content = response["choices"][0]["message"]["content"]

        # Intentar parsear como JSON
        try:
            questions_data = json.loads(content)
            return questions_data[:num_questions]  # Retorna solo la cantidad necesaria
        except json.JSONDecodeError:
            print("❌ Error: No se pudo parsear la respuesta JSON de OpenAI.")
            return []

    except openai.error.OpenAIError as e:
        print(f"❌ Error de OpenAI: {e}")
        return []

def save_questions_to_db(questions_data):
    """
    Guarda preguntas y respuestas en la base de datos.
    :param questions_data: Lista de diccionarios con preguntas y respuestas.
    """
    for question_data in questions_data:
        category_name = question_data.get("category", "General Knowledge")
        difficulty = question_data.get("difficulty", "easy")
        question_text = question_data.get("question", "")

        # Buscar o crear la categoría
        category, _ = QuizCategory.objects.get_or_create(name=category_name)

        # Evitar duplicados
        if Question.objects.filter(text=question_text, quiz_category=category).exists():
            print(f"⚠️ La pregunta '{question_text}' ya existe en la base de datos.")
            continue

        # Crear la pregunta
        question = Question.objects.create(
            text=question_text,
            quiz_category=category,
            difficulty=difficulty
        )

        # Guardar respuestas asociadas
        for answer_data in question_data.get("answers", []):
            Answer.objects.create(
                question=question,
                text=answer_data["text"],
                is_correct=answer_data["is_correct"]
            )

        print(f"✅ Pregunta guardada: {question_text}")

def main():
    # Prompt mejorado para asegurar salida JSON correcta
    prompt = """
    Generate 5 multiple-choice questions on general knowledge.
    Each question should have exactly 4 possible answers, with one correct answer.
    Format the response as a JSON array like this:
    [
      {
        "question": "What is the capital of France?",
        "answers": [
          {"text": "Paris", "is_correct": true},
          {"text": "London", "is_correct": false},
          {"text": "Berlin", "is_correct": false},
          {"text": "Madrid", "is_correct": false}
        ],
        "difficulty": "easy",
        "category": "Geography"
      }
    ]
    Make sure the output is a valid JSON object with double quotes.
    """

    # Generar preguntas usando OpenAI
    questions_data = generate_questions_from_openai(prompt, num_questions=5)

    if questions_data:
        # Guardar preguntas en la base de datos
        save_questions_to_db(questions_data)
        print(f"✅ {len(questions_data)} preguntas generadas y guardadas en la base de datos.")
    else:
        print("❌ No se generaron preguntas.")

# Ejecutar el script si se llama directamente
if __name__ == "__main__":
    main()
