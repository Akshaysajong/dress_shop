from django.urls import path
from .views import HomeAPIView

urlpatterns = [
    # ==================== HOME API ====================
    path('home/', HomeAPIView.as_view(), name='api_home'),
    
]