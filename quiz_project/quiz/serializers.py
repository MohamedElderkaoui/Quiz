from rest_framework import serializers
from .models import Question, Answer, Score, QuizCategory

class QuizCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizCategory
        fields = '__all__'

class AnswerSerializer(serializers.ModelSerializer):
    # Optionally, if you want to use a custom field for the question reference:
    question_id = serializers.PrimaryKeyRelatedField(
        queryset=Question.objects.all(), write_only=True, source='question'
    )

    class Meta:
        model = Answer
        fields = ['id', 'text', 'is_correct', 'question_id']

class QuestionSerializer(serializers.ModelSerializer):
    # Nest answers if needed:
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = '__all__'

class ScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Score
        fields = '__all__'
