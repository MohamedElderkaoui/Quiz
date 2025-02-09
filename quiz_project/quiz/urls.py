from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
# admin import
from django.contrib import admin

urlpatterns = [
    path('api/', views.api_home, name='api_home'),
    path('api/questions/', views.get_questions, name='get_questions'),
    path('api/score/', views.submit_score, name='submit_score'),
    path('api/ranking/', views.ranking, name='ranking'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Use the built-in JWT view
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Refresh JWT tokens
    path('api/questions/', views.questions_list, name='questions_list'),
]
 