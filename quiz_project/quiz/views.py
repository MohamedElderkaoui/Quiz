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
from rest_framework import viewsets, status
from .models import Question, Answer, Score, QuizCategory
from .serializers import QuestionSerializer, AnswerSerializer, ScoreSerializer, QuizCategorySerializer


# ✅ OpenAI API Setup
openai.api_base = "https://api.openai.com/v1"
openai.api_key = settings.OPENAI_API_KEY


# 🔍 Helper to Fetch Questions from OpenAI with Caching
def fetch_questions_from_openai():
    """Fetches general knowledge questions from OpenAI and caches them for 1 hour."""
    cached_questions = cache.get("questions")
    if cached_questions:
        return cached_questions
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": "Generate 5 general knowledge questions with 3 options and one correct answer. JSON format."}],
            temperature=0.7
        )
        questions = json.loads(response["choices"][0]["message"]["content"])
        cache.set("questions", questions, timeout=3600)
        return questions

    except Exception as e:
        print(f"Error fetching questions from OpenAI: {e}")
        return []


# 🌐 API Home
@api_view(['GET'])
@permission_classes([AllowAny])
def api_home(request):
    return JsonResponse({"message": "Welcome to the Quiz API!"})


# 🎯 Get 10 Random Questions
@api_view(['GET'])
@permission_classes([AllowAny])
def get_random_questions(request):
    """Returns 10 random questions with caching."""
    cached_questions = cache.get("random_questions")
    if cached_questions:
        return Response(json.loads(cached_questions))

    questions = list(Question.objects.all())
    if len(questions) < 10:
        return Response({"error": "Not enough questions available."}, status=400)

    random.shuffle(questions)
    selected_questions = QuestionSerializer(questions[:10], many=True).data
    cache.set("random_questions", json.dumps(selected_questions), timeout=3600)
    return Response(selected_questions)


# 🎯 Get All Questions
@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_questions(request):
    """Retrieve all questions."""
    questions = Question.objects.all()
    serializer = QuestionSerializer(questions, many=True)
    return Response(serializer.data)


# 🏆 Get Top 10 Rankings
@api_view(['GET'])
@permission_classes([AllowAny])
def get_ranking(request):
    """Retrieve the top 10 scores."""
    scores = Score.objects.order_by('-points')[:10]
    serializer = ScoreSerializer(scores, many=True)
    return Response(serializer.data)


# 🔒 Submit Player's Score (Protected)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def submit_score(request):
    """Submit a player's score."""
    serializer = ScoreSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Score submitted successfully!"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 🛠️ Add a New Question (Protected)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def add_question(request):
    """Add a new question."""
    serializer = QuestionSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        cache.delete("random_questions")  # Invalidate cache
        return Response({"message": "Question added successfully!"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 🛠️ Edit an Existing Question (Protected)
@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def edit_question(request, question_id):
    """Edit an existing question."""
    question = get_object_or_404(Question, id=question_id)
    serializer = QuestionSerializer(question, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        cache.delete("random_questions")  # Invalidate cache
        return Response({"message": "Question updated successfully!"}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 🗑️ Delete a Question (Protected)
@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_question(request, question_id):
    """Delete a question."""
    question = get_object_or_404(Question, id=question_id)
    question.delete()
    cache.delete("random_questions")  # Invalidate cache
    return Response({"message": "Question deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)


# 🛠️ Add an Answer to a Question (Protected)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def add_answer(request, question_id):
    """Add an answer to a question."""
    question = get_object_or_404(Question, id=question_id)
    data = request.data.copy()
    data['question'] = question.id
    serializer = AnswerSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Answer added successfully!"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 🛠️ Edit an Answer (Protected)
@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def edit_answer(request, answer_id):
    """Edit an existing answer."""
    answer = get_object_or_404(Answer, id=answer_id)
    serializer = AnswerSerializer(answer, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Answer updated successfully!"}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 🗑️ Delete an Answer (Protected)
@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_answer(request, answer_id):
    """Delete an answer."""
    answer = get_object_or_404(Answer, id=answer_id)
    answer.delete()
    return Response({"message": "Answer deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)


# 🌍 Public API View
class PublicView(viewsets.ViewSet):
    """A public view for testing API access."""
    permission_classes = [AllowAny]

    def list(self, request):
        return Response({"message": "This is a public endpoint!"})


# 🚀 ViewSets for DRF Router
class QuizCategoryViewSet(viewsets.ModelViewSet):
    queryset = QuizCategory.objects.all()
    serializer_class = QuizCategorySerializer


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class AnswerViewSet(viewsets.ModelViewSet):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer


class ScoreViewSet(viewsets.ModelViewSet):
    queryset = Score.objects.all()
    serializer_class = ScoreSerializer
