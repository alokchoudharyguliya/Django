# api/views.py
from rest_framework import generics
from .models import Item
from .serializers import ItemSerializer
from .metrics import item_created_counter

class ItemCreateView(generics.CreateAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        item_created_counter.inc()   # Increment custom metric
        return instance