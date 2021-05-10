from django.urls import path

from news_parser.views import ParseNewsView

urlpatterns = [
    path('new_task/', ParseNewsView.as_view(), name='new_task')
]