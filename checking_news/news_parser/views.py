from django.shortcuts import render
from django.views import View
from .tasks import parse


class ParseNewsView(View):

    def get(self, request):
        task = parse.delay()
        return render(request, 'parse_news.html')
