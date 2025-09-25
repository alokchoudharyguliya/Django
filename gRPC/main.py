import grpc
from concurrent import futures
import time

import users_pb2
import users_pb2_grpc

class UserServiceServicer(users_pb2_grpc.UserServiceServicer):
    # Unary RPC
    def GetUser(self, request, context):
        return users_pb2.UserResponse(
            user=users_pb2.User(id=request.id, name="Alice", is_active=True)
        )

    # Server streaming
    def ListUsers(self, request, context):
        for i in range(1, 4):
            yield users_pb2.User(id=i, name=f"User {i}", is_active=bool(i%2))

    # Client streaming
    def UploadUsers(self, request_iterator, context):
        count = 0
        for user in request_iterator:
            print(f"Received user: {user.name}")
            count += 1
        return users_pb2.UploadSummary(count=count)

    # Bidirectional streaming
    def Chat(self, request_iterator, context):
        for msg in request_iterator:
            print(f"{msg.sender}: {msg.text}")
            yield users_pb2.ChatMessage(sender="Server", text=f"Echo: {msg.text}")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    users_pb2_grpc.add_UserServiceServicer_to_server(UserServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("🚀 Server running on port 50051...")
    try:
        while True:
            time.sleep(86400)  # keep alive 1 day
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == "__main__":
    serve()
