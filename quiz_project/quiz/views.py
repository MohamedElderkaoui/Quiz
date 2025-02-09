import random
import json
import redis
import openai
from django.conf import settings
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.http import JsonResponse
from .models import Question, Score
from .serializers import QuestionSerializer, ScoreSerializer
from django_datatables_view.base_datatable_view import BaseDatatableView

# OpenAI API Client Setup
openai.api_base = "https://api.openai.com/v1"
openai.api_key = settings.OPENAI_API_KEY

# Redis Cache Setup
cache_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

def fetch_questions_from_openai():
    """Fetch questions from OpenAI and cache them with Redis."""
    cached_questions = cache_client.get("questions")
    if cached_questions:
        return json.loads(cached_questions)

    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "user",
                    "content": "Generate 5 general knowledge questions, each with 3 answer choices and one correct answer. Return as JSON."
                }
            ]
        )
        questions = json.loads(response.choices[0].message.content)
        cache_client.set("questions", json.dumps(questions), ex=3600)  # Cache for 1 hour
        return questions
    except Exception as e:
        print(f"Error fetching questions from OpenAI: {e}")
        return []  # Handle this more gracefully by providing fallback questions

@api_view(['GET'])
def get_random_questions(request):
    """Returns 10 random questions (cached in Redis)."""
    cached_questions = cache_client.get("random_questions")
    
    if cached_questions:
        return Response(json.loads(cached_questions))

    questions = list(Question.objects.all())
    if len(questions) < 10:
        return Response({"error": "Not enough questions in the database"}, status=400)

    random.shuffle(questions)
    serialized_questions = QuestionSerializer(questions[:10], many=True).data
    cache_client.set("random_questions", json.dumps(serialized_questions), ex=3600)

    return Response(serialized_questions)

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def submit_score(request):
    """Stores a player's score."""
    serializer = ScoreSerializer(data=request.data)
    
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Score saved successfully"}, status=201)
    
    return Response(serializer.errors, status=400)

@api_view(['GET'])
def get_ranking(request):
    """Returns the top 10 scores."""
    scores = Score.objects.order_by('-points')[:10]
    serializer = ScoreSerializer(scores, many=True)
    return Response(serializer.data)

def api_home(request):
    """API home endpoint."""
    return JsonResponse({"message": "Welcome to the API"}, status=200)

def get_questions(request):
    """Fetch 10 random questions."""
    questions = list(Question.objects.all())
    
    if len(questions) < 10:
        return JsonResponse({"error": "Not enough questions in the database"}, status=400)

    random.shuffle(questions)
    serialized_questions = QuestionSerializer(questions[:10], many=True).data
    return JsonResponse(serialized_questions, safe=False)

def ranking(request):
    """Returns the top 10 scores."""
    top_scores = Score.objects.order_by('-points')[:10]
    serialized_scores = ScoreSerializer(top_scores, many=True).data
    return JsonResponse(serialized_scores, safe=False)

class QuestionListJson(BaseDatatableView):
    model = Question
    columns = ['text', 'quiz_category', 'difficulty']  # Columns to display
    order_columns = ['text', 'quiz_category', 'difficulty']  # Order columns
    max_display_length = 500  # Maximum number of records to display

    def get_queryset(self):
        return Question.objects.all()





# questions_list

def questions_list(request):
    return QuestionListJson.as_view()(request)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

class PublicView(APIView):
    """
    A public API view that does not require authentication.
    """
    permission_classes = [AllowAny]  # Allows anyone to access this endpoint

    def get(self, request):
        return Response({"message": "This is a public endpoint!"})
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

class PublicView(APIView):
    """
    A public API view that does not require authentication.
    """
    permission_classes = [AllowAny]  # Allows anyone to access this endpoint

    def get(self, request):
        return Response({"message": "This is a public endpoint!"})
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
import random
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Question, Answer, Score
from .serializers import QuestionSerializer, AnswerSerializer, ScoreSerializer

# Fetch 10 random questions with answers (using cache for performance)
@api_view(['GET'])
def get_random_questions(request):
    """Returns 10 random questions with their answers."""
    questions = list(Question.objects.all())
    if len(questions) < 10:
        return Response({"error": "Not enough questions in the database"}, status=400)

    random.shuffle(questions)  # Shuffle the questions list
    questions_with_answers = []
    for question in questions[:10]:
        answers = Answer.objects.filter(question=question)
        serialized_answers = AnswerSerializer(answers, many=True).data
        question_data = QuestionSerializer(question).data
        question_data['answers'] = serialized_answers
        questions_with_answers.append(question_data)

    return Response(questions_with_answers)


# Submit player's score (protected by JWT authentication)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def submit_score(request):
    """Store a player's score."""
    serializer = ScoreSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Score saved successfully"}, status=201)
    return Response(serializer.errors, status=400)


# Fetch top 10 rankings based on points
@api_view(['GET'])
def get_ranking(request):
    """Returns the top 10 scores."""
    scores = Score.objects.order_by('-points')[:10]
    serializer = ScoreSerializer(scores, many=True)
    return Response(serializer.data)


# Get a list of all questions
@api_view(['GET'])
def get_all_questions(request):
    """Returns all questions."""
    questions = Question.objects.all()
    serializer = QuestionSerializer(questions, many=True)
    return Response(serializer.data)


# Add a new question (only accessible to admins or authorized users)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def add_question(request):
    """Add a new question."""
    serializer = QuestionSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Question added successfully"}, status=201)
    return Response(serializer.errors, status=400)


# Edit an existing question (only accessible to admins or authorized users)
@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def edit_question(request, question_id):
    """Edit an existing question."""
    question = get_object_or_404(Question, id=question_id)
    serializer = QuestionSerializer(question, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Question updated successfully"}, status=200)
    return Response(serializer.errors, status=400)


# Delete a question (only accessible to admins or authorized users)
@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_question(request, question_id):
    """Delete a question."""
    question = get_object_or_404(Question, id=question_id)
    question.delete()
    return Response({"message": "Question deleted successfully"}, status=204)


# Add an answer to a question
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def add_answer(request, question_id):
    """Add an answer for a question."""
    question = get_object_or_404(Question, id=question_id)
    serializer = AnswerSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(question=question)
        return Response({"message": "Answer added successfully"}, status=201)
    return Response(serializer.errors, status=400)


# Edit an existing answer
@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def edit_answer(request, answer_id):
    """Edit an existing answer."""
    answer = get_object_or_404(Answer, id=answer_id)
    serializer = AnswerSerializer(answer, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Answer updated successfully"}, status=200)
    return Response(serializer.errors, status=400)


# Delete an answer
@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_answer(request, answer_id):
    """Delete an answer."""
    answer = get_object_or_404(Answer, id=answer_id)
    answer.delete()
    return Response({"message": "Answer deleted successfully"}, status=204)
import json
import random
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import Question, Score
from .serializers import QuestionSerializer, ScoreSerializer

@require_GET
def api_home(request):
    """
    A simple API home view that returns a welcome message in JSON format.
    """
    return JsonResponse({"message": "Welcome to the API"}, status=200)


@require_GET
def get_questions(request):
    """
    Return 10 random questions as JSON.
    
    This view fetches all questions from the database, shuffles them,
    and returns the first 10 questions using the QuestionSerializer.
    """
    questions = list(Question.objects.all())
    
    if len(questions) < 10:
        return JsonResponse({"error": "Not enough questions in the database"}, status=400)
    
    random.shuffle(questions)
    # Serialize the first 10 questions. Using `safe=False` because we are returning a list.
    serialized_questions = QuestionSerializer(questions[:10], many=True).data
    return JsonResponse(serialized_questions, safe=False)


@require_GET
def ranking(request):
    """
    Return the top 10 scores as JSON.
    
    Scores are ordered in descending order by points.
    """
    top_scores = Score.objects.order_by('-points')[:10]
    serialized_scores = ScoreSerializer(top_scores, many=True).data
    return JsonResponse(serialized_scores, safe=False)


@csrf_exempt  # Only for demonstration; consider using proper CSRF protection in production.
@require_POST
def submit_score(request):
    """
    Receive a score submission via a POST request (as JSON) and save it.
    
    Expects the request body to contain valid JSON data for a Score.
    """
    try:
        # Parse the incoming JSON data
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    
    serializer = ScoreSerializer(data=data)
    
    if serializer.is_valid():
        serializer.save()
        return JsonResponse({"message": "Score saved successfully"}, status=201)
    
    return JsonResponse(serializer.errors, status=400)
