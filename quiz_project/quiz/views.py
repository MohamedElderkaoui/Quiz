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