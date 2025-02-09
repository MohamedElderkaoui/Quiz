from rest_framework import viewsets
from .models import Question, Answer, Score
from .serializers import QuestionSerializer, AnswerSerializer, ScoreSerializer

class QuestionViewSet(viewsets.ModelViewSet):
    """API endpoint for managing questions"""
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

class AnswerViewSet(viewsets.ModelViewSet):
    """API endpoint for managing answers"""
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer

class ScoreViewSet(viewsets.ModelViewSet):
    """API endpoint for managing scores"""
    queryset = Score.objects.all().order_by('-date')  # Sort by latest scores
    serializer_class = ScoreSerializer
