from django.shortcuts import render
from django.views import View

from news_parser.models import BrokenLink


class ShowBrokenLinks(View):

    def get(self, request):
        links = BrokenLink.objects.filter(fixed=False)
        return render(request, 'show_broken_links.html', {'links': links})
