# frontend/app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Autenticación
    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('settings/', views.settings_view, name='settings'),

    # API Endpoints (proxy a FastAPI)
    path('api/count-people/', views.count_people, name='count_people'),
    path('api/update-threshold/', views.update_threshold, name='update_threshold'),
    path('api/get-thresholds/', views.get_thresholds, name='get_thresholds'),

    # Health check
    path('health/', views.health, name='health'),
]
