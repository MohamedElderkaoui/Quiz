from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from .views import (
    api_home, get_random_questions, submit_score, get_ranking, get_all_questions,
    add_question, edit_question, delete_question, add_answer, edit_answer, delete_answer,
    QuizCategoryViewSet, QuestionViewSet, AnswerViewSet, ScoreViewSet, PublicView
)

# ✅ DRF Router Setup for ViewSets
router = DefaultRouter()
router.register(r'categories', QuizCategoryViewSet, basename="quizcategory")
router.register(r'questions', QuestionViewSet, basename="question")
router.register(r'answers', AnswerViewSet, basename="answer")
router.register(r'scores', ScoreViewSet, basename="score")

# ✅ URL Patterns
urlpatterns = [
    # 🌍 API Home
    path('', api_home, name="api-home"),

    # 🎯 Quiz Endpoints
    path('questions/random/', get_random_questions, name="get-random-questions"),
    path('questions/all/', get_all_questions, name="get-all-questions"),
    path('questions/add/', add_question, name="add-question"),
    path('questions/edit/<int:question_id>/', edit_question, name="edit-question"),
    path('questions/delete/<int:question_id>/', delete_question, name="delete-question"),

    # 🎯 Answer Endpoints
    path('answers/add/<int:question_id>/', add_answer, name="add-answer"),
    path('answers/edit/<int:answer_id>/', edit_answer, name="edit-answer"),
    path('answers/delete/<int:answer_id>/', delete_answer, name="delete-answer"),

    # 🏆 Scores & Rankings
    path('scores/submit/', submit_score, name="submit-score"),
    path('scores/ranking/', get_ranking, name="get-ranking"),

    # 🔐 Authentication (JWT)
    path('auth/token/', TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name="token_refresh"),

    # 📜 API Schema & Swagger Docs
    path('schema/', SpectacularAPIView.as_view(), name="schema"),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name="swagger-ui"),

    # 🔄 DRF ViewSets (Router)
    path('', include(router.urls)),

    # 🌍 Public API
    path('public/', PublicView.as_view(), name="public-view"),
]
