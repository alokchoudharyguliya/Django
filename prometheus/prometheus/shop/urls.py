# shop/urls.py
from django.urls import path
from .views import purchase

urlpatterns = [
    path('purchase/', purchase, name='purchase'),
]