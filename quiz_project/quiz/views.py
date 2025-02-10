import random
import json
import openai
from django.conf import settings
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from rest_framework import viewsets
from .models import Question, Answer, Score, QuizCategory
from .serializers import QuestionSerializer, AnswerSerializer, ScoreSerializer, QuizCategorySerializer


# ✅ OpenAI API Setup
openai.api_base = "https://api.openai.com/v1"
openai.api_key = settings.OPENAI_API_KEY


# ✅ Fetch Questions from OpenAI with Caching
def fetch_questions_from_openai():
    """Fetches general knowledge questions from OpenAI and caches them for 1 hour."""
    return cache.get_or_set(
        "questions",
        lambda: fetch_from_openai_helper(),
        timeout=3600
    )


def fetch_from_openai_helper():
    """Helper function to fetch questions from OpenAI."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": "Generate 5 general knowledge questions with 3 answer choices and one correct answer. Return JSON."}]
        )
        return json.loads(response["choices"][0]["message"]["content"])
    except Exception as e:
        print(f"Error fetching questions: {e}")
        return []


# ✅ API Home View
@api_view(['GET'])
def api_home(request):
    """API home endpoint."""
    return JsonResponse({"message": "Welcome to the API"}, status=200)


# ✅ Get 10 Random Questions
@api_view(['GET'])
def get_random_questions(request):
    """Returns 10 random questions (cached for performance)."""
    cached_questions = cache.get("random_questions")

    if cached_questions:
        return Response(json.loads(cached_questions))

    questions = list(Question.objects.all())

    if len(questions) < 10:
        return Response({"error": "Not enough questions in the database"}, status=400)

    random.shuffle(questions)
    serialized_questions = QuestionSerializer(questions[:10], many=True).data
    cache.set("random_questions", json.dumps(serialized_questions), timeout=3600)

    return Response(serialized_questions)


# ✅ Submit Player's Score (Protected)
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


# ✅ Get Top 10 Rankings
@api_view(['GET'])
def get_ranking(request):
    """Returns the top 10 scores."""
    scores = Score.objects.order_by('-points')[:10]
    serializer = ScoreSerializer(scores, many=True)
    return Response(serializer.data)


# ✅ Get All Questions
@api_view(['GET'])
def get_all_questions(request):
    """Returns all questions."""
    questions = Question.objects.all()
    serializer = QuestionSerializer(questions, many=True)
    return Response(serializer.data)


# ✅ Add a New Question (Protected)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def add_question(request):
    """Adds a new question."""
    serializer = QuestionSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Question added successfully"}, status=201)
    return Response(serializer.errors, status=400)


# ✅ Edit an Existing Question (Protected)
@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def edit_question(request, question_id):
    """Edits an existing question."""
    question = get_object_or_404(Question, id=question_id)
    serializer = QuestionSerializer(question, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Question updated successfully"}, status=200)
    return Response(serializer.errors, status=400)


# ✅ Delete a Question (Protected)
@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_question(request, question_id):
    """Deletes a question."""
    question = get_object_or_404(Question, id=question_id)
    question.delete()
    return Response({"message": "Question deleted successfully"}, status=204)


# ✅ Add an Answer to a Question (Protected)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def add_answer(request, question_id):
    """Adds an answer for a question."""
    question = get_object_or_404(Question, id=question_id)
    data = request.data.copy()
    data["question"] = question.id  # Assign question ID

    serializer = AnswerSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Answer added successfully"}, status=201)
    return Response(serializer.errors, status=400)


# ✅ Edit an Answer (Protected)
@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def edit_answer(request, answer_id):
    """Edits an existing answer."""
    answer = get_object_or_404(Answer, id=answer_id)
    serializer = AnswerSerializer(answer, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Answer updated successfully"}, status=200)
    return Response(serializer.errors, status=400)


# ✅ Delete an Answer (Protected)
@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_answer(request, answer_id):
    """Deletes an answer."""
    answer = get_object_or_404(Answer, id=answer_id)
    answer.delete()
    return Response({"message": "Answer deleted successfully"}, status=204)


# ✅ ViewSets for DRF Router
class QuizCategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for Quiz Categories."""
    queryset = QuizCategory.objects.all()
    serializer_class = QuizCategorySerializer


class QuestionViewSet(viewsets.ModelViewSet):
    """ViewSet for Questions."""
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class AnswerViewSet(viewsets.ModelViewSet):
    """ViewSet for Answers."""
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer


class ScoreViewSet(viewsets.ModelViewSet):
    """ViewSet for Scores."""
    queryset = Score.objects.all()
    serializer_class = ScoreSerializer


# ✅ Public API View (No Authentication)
class PublicView(APIView):
    """A public API view that does not require authentication."""
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"message": "This is a public endpoint!"})

class ScoreViewSet(viewsets.ModelViewSet):
    queryset = Score.objects.all()
    serializer_class = ScoreSerializer
