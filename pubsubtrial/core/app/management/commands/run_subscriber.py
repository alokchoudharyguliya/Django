# app/management/commands/run_subscriber.py
import redis
from django.conf import settings
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Run Redis subscriber"

    def handle(self, *args, **kwargs):
        r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True)
        pubsub = r.pubsub()
        pubsub.subscribe("notifications")

        self.stdout.write("Listening on 'notifications' channel...")

        for message in pubsub.listen():
            if message["type"] == "message":
                self.stdout.write(f"📩 New message: {message['data']}")
