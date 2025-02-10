import openai
import os
from dotenv import load_dotenv
import csv  
import time


# Definir las categorías
categories = [
    "Science", "History", "Geography", "Art", "Sports", "Technology",
    "Mathematics", "Literature", "Movies", "Music", "Nature", "Politics",
    "Economics", "Philosophy", "Psychology", "Religion", "Astronomy",
    "Medicine", "Law", "Business", "Programming", "Engineering",
    "Health", "Physics", "Chemistry", "Biology", "Environmental Science",
    "Languages", "Sociology", "Anthropology", "Archaeology", "Statistics",
    "Data Science", "Astronautics", "Gaming", "Mythology", "Trivia",
    "Cooking", "Food & Drink", "Fashion", "Photography", "Pets",
    "Travel", "Hobbies", "DIY", "Education", "Fitness", "Life Skills",
    "Current Events", "World Cultures", "Architecture", "Famous People", "Pop Culture"
]

# Función para generar preguntas usando OpenAI
def generate_questions(category, num_questions=50):  # Reducción a 50 preguntas por lote
    questions = []
    for _ in range(num_questions):
        prompt = f"Genera una pregunta de opción múltiple sobre {category} con 4 respuestas posibles, indicando la respuesta correcta."
        
        # Llamada a la API de OpenAI con el modelo actualizado
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Modelo gpt-3.5-turbo
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,  # Ajusta según sea necesario
            n=1,
            temperature=0.7
        )
        
        question_data = response['choices'][0]['message']['content'].strip().split("\n")
        question_text = question_data[0]
        answers = question_data[1:]
        
        # Crear un diccionario con la pregunta y las respuestas
        question = {
            "category": category,
            "question": question_text,
            "answers": answers
        }
        questions.append(question)
    return questions

# Guardar las preguntas en un archivo CSV
def save_to_csv(questions, filename='questions_data.csv'):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Category', 'Question', 'Answer 1', 'Answer 2', 'Answer 3', 'Answer 4'])
        
        for question in questions:
            row = [
                question['category'],
                question['question'],
                question['answers'][0],
                question['answers'][1],
                question['answers'][2],
                question['answers'][3]
            ]
            writer.writerow(row)

# Generar las preguntas por categoría y hacer múltiples solicitudes
def generate_all_questions():
    all_questions = []
    for category in categories:
        print(f"Generando preguntas para la categoría: {category}")
        # Realizar la solicitud por lotes pequeños
        category_questions = generate_questions(category, 50)  # Solicita 50 preguntas por categoría
        all_questions.extend(category_questions)
        
        # Pausa entre solicitudes para no exceder los límites de la API
        time.sleep(2)  # Puedes ajustar este tiempo según sea necesario
    
    return all_questions

# Guardar todas las preguntas en un archivo CSV
all_questions = generate_all_questions()
save_to_csv(all_questions)

print("Las preguntas han sido generadas y guardadas en 'questions_data.csv'.")