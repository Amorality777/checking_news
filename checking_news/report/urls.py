from django.urls import path

from report.views import ShowBrokenLinks

urlpatterns = [path('', ShowBrokenLinks.as_view())]