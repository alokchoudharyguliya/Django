from django.contrib import admin
from django.urls import path
from src.views import *
urlpatterns = [
    path('', home),
    path('recipes/<int:id>/', view_recipe, name="view_recipe"),
]