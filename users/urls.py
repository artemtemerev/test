from django.contrib import admin
from django.urls import path, include
from .views import CalendarView

urlpatterns = [
    path('<int:pk>/calendar-view/', CalendarView.as_view(), name='calendar_view'),
]