import openai
import os
from dotenv import load_dotenv
from .models import Question, Answer

# Cargar variables de entorno
load_dotenv()
import os
import openai
 
openai.api_key = os.environ["a"]
def generate_questions_from_openai(prompt, num_questions=5):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        questions = response["choices"][0]["message"]["content"].split("\n")
        return questions[:num_questions]
    
    except openai.error.OpenAIError as e:
        print(f"Error de OpenAI: {e}")
        return []

def save_questions_to_db(questions, category="General Knowledge", difficulty="easy"):
    for question_text in questions:
        # Crear la pregunta en la base de datos
        question = Question.objects.create(
            text=question_text,
            quiz_category=category,
            difficulty=difficulty
        )
        
        # Crear una respuesta de muestra (puedes modificar esto para generar respuestas reales)
        Answer.objects.create(
            question=question,
            text="Sample Answer",  # Puedes mejorar esto generando respuestas con OpenAI
            is_correct=True  # Lógica básica, puedes mejorarla
        )
        
        print(f"Saved question: {question_text}")

def main():
    # Definir el prompt para generar preguntas
    prompt = "Generate 5 multiple-choice questions on general knowledge with answers."

    # Generar preguntas desde OpenAI
    questions = generate_questions_from_openai(prompt, num_questions=5)

    if questions:
        # Guardar las preguntas en la base de datos
        save_questions_to_db(questions, category="General Knowledge", difficulty="easy")
    else:
        print("No questions generated.")

if __name__ == "__main__":
    main()
