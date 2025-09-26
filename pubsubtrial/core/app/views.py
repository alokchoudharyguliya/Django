import redis
from django.conf import settings
from django.http import JsonResponse

def publish_message(request):
    r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True)
    message = request.GET.get("msg", "Hello Subscribers!")
    
    # Publish to "notifications" channel
    r.publish("notifications", message)
    return JsonResponse({"status": "Message published", "message": message})