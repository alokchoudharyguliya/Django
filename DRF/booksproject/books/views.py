from rest_framework import viewsets
from .models import Book
from .serializers import BookSerializer
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework_xml.renderers import XMLRenderer
from rest_framework_yaml.renderers import YAMLRenderer
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer
                        , XMLRenderer, YAMLRenderer]