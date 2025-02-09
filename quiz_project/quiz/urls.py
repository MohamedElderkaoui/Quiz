from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib import admin
from rest_framework.schemas import get_schema_view
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    # API Home
    path('api/', views.api_home, name='api_home'),
    
    # Questions endpoints:
    # Use a unique path for each view to avoid conflicts.
    path('api/questions/all/', views.get_questions, name='get_questions'),
    path('api/questions/list/', views.questions_list, name='questions_list'),
    
    # Score endpoints
    path('api/score/', views.submit_score, name='submit_score'),
    path('api/ranking/', views.ranking, name='ranking'),
    
    # Public endpoint
    path('api/public/', views.PublicView.as_view(), name='public_view'),
    
    # JWT Authentication endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # OpenAPI Schema (DRF built-in schema view)
    path("openapi/", get_schema_view(title="Your Project", description="API for all things …"), name="openapi-schema"),
    
    # Uncomment the following if you need access to the Django admin
    # path('admin/', admin.site.urls),
]

# DRF Spectacular endpoints for schema and documentation
urlpatterns += [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
