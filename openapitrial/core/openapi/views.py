from rest_framework.views import APIView
from rest_framework.response import Response

class HelloView(APIView):
    """
    get:
    Return a simple greeting.
    """
    def get(self, request):
        return Response({"message": "Hello, OpenAPI with Django!"})
