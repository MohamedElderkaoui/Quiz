from django.urls import re_path
from .consumers import QuizTimerConsumer

websocket_urlpatterns = [
    re_path(r'ws/quiz/timer/$', QuizTimerConsumer.as_asgi()),
]
