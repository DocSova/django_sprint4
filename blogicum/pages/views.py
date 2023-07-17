"""Функции, отвечающие за вывод приложения pages."""
from http import HTTPStatus

from django.views import View
from django.shortcuts import render


class AboutView(View):
    def get(self, request):
        return render(request, 'pages/about.html')


class RulesView(View):
    def get(self, request):
        return render(request, 'pages/rules.html')


def page_not_found(request, exception):
    return render(request, 'pages/404.html', status=HTTPStatus.NOT_FOUND)


def csrf_failure(request, reason=''):
    return render(request, 'pages/403csrf.html', status=HTTPStatus.FORBIDDEN)


def server_error(request):
    return render(request,
                  'pages/500.html',
                  status=HTTPStatus.INTERNAL_SERVER_ERROR)
