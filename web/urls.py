from django.urls import path, include
from web import views

urlpatterns = [
    path('dashboard/', views.AdminDashboardView.as_view(), name='admin-dashboard'),
    path('contestant/<str:action>/', views.ContestantCRUDView.as_view(), name='contestant-crud'),
    path('game/<str:action>/', views.GameCRUDView.as_view(), name='game-crud'),
    path('game-session/', views.GameSessionView.as_view(), name='game-session'),
    path('game-session-status/', views.GameSessionStatusView.as_view(), name='game-session-status'),
]
