from django.db import models
class Question(models.Model):
    text = models.CharField(max_length=255)
    quiz_category = models.CharField(max_length=100)  # Add this if it's missing
    difficulty = models.CharField(max_length=50, default='easy')

    def __str__(self):
        return self.text
class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text} ({'Correcta' if self.is_correct else 'Incorrecta'})"

class Score(models.Model):
    player_name = models.CharField(max_length=100)
    points = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.player_name} - {self.points}"
