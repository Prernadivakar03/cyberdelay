from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('submit/', views.submit_incident, name='submit'),
    path('result/<int:pk>/', views.incident_result, name='incident_result'),
    path('history/', views.incident_history, name='history'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('delete/<int:pk>/', views.delete_incident, name='delete_incident'),
]
