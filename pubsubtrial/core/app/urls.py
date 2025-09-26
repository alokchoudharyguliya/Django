from django.urls import path
from app.views import *
urlpatterns=[
    path('publish_message/',publish_message),
]