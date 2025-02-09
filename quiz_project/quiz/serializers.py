from rest_framework import serializers
from .models import Question, Answer, Score

class AnswerSerializer(serializers.ModelSerializer):
    """Serializa respuestas"""
    class Meta:
        model = Answer
        fields = '__all__'

class QuestionSerializer(serializers.ModelSerializer):
    """Serializa preguntas con sus respuestas"""
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = '__all__'

class ScoreSerializer(serializers.ModelSerializer):
    """Serializa las puntuaciones"""
    class Meta:
        model = Score
        fields = '__all__'
