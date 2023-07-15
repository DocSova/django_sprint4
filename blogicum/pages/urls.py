"""Роутинг в приложении pages."""
from django.urls import path

from .views import RulesView, AboutView

app_name = 'pages'

urlpatterns = [
    path('about/', AboutView.as_view(), name='about'),
    path('rules/', RulesView.as_view(), name='rules'),
]
