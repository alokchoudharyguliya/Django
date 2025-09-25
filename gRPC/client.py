import grpc
import users_pb2
import users_pb2_grpc

def run():
    # Connect to server
    channel = grpc.insecure_channel('localhost:50051')
    stub = users_pb2_grpc.UserServiceStub(channel)

    # --- 1. Unary RPC ---
    print("\n=== Unary RPC: GetUser ===")
    response = stub.GetUser(users_pb2.UserRequest(id=1))
    print(f"User: {response.user.id}, {response.user.name}, Active={response.user.is_active}")

    # --- 2. Server Streaming RPC ---
    print("\n=== Server Streaming RPC: ListUsers ===")
    for user in stub.ListUsers(users_pb2.google_dot_protobuf_dot_empty__pb2.Empty()):
        print(f"User: {user.id}, {user.name}, Active={user.is_active}")

    # --- 3. Client Streaming RPC ---
    print("\n=== Client Streaming RPC: UploadUsers ===")
    def generate_users():
        for i in range(3):
            yield users_pb2.User(id=i, name=f"UploadedUser{i}", is_active=True)
    summary = stub.UploadUsers(generate_users())
    print(f"Uploaded {summary.count} users")

    # --- 4. Bidirectional Streaming RPC ---
    print("\n=== Bidirectional Streaming RPC: Chat ===")
    def chat_messages():
        messages = ["Hi", "How are you?", "Goodbye!"]
        for text in messages:
            yield users_pb2.ChatMessage(sender="Client", text=text)

    for reply in stub.Chat(chat_messages()):
        print(f"Server replied: {reply.text}")

if __name__ == "__main__":
    run()
