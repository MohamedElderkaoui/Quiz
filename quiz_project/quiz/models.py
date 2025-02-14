from django.db import models

class QuizCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Question(models.Model):
    # Define difficulty levels
    EASY = 'easy'
    MEDIUM = 'medium'
    HARD = 'hard'
    DIFFICULTY_CHOICES = [
        (EASY, 'Easy'),
        (MEDIUM, 'Medium'),
        (HARD, 'Hard'),
    ]
    quiz_category = models.ForeignKey(
        QuizCategory, 
        on_delete=models.CASCADE, 
        related_name='questions'
    )
    text = models.TextField()
    difficulty = models.CharField(
        max_length=10, 
        choices=DIFFICULTY_CHOICES, 
        default=EASY
    )

    def __str__(self):
        return self.text

class Answer(models.Model):
    question = models.ForeignKey(
        Question, 
        on_delete=models.CASCADE, 
        related_name='answers'
    )
    text = models.TextField()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        status = "Correct" if self.is_correct else "Incorrect"
        return f"{self.text} ({status})"

class Score(models.Model):
    player_name = models.CharField(max_length=100)
    points = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="scores", null=True, blank=True)

    def __str__(self):
        return f"{self.player_name} - {self.points}"
