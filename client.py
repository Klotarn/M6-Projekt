import socket
import os
from dotenv import load_dotenv
import threading
import json

load_dotenv()

SERVER_IP = os.getenv("SERVER_IP")  # Default to localhost if not set

print(f"Connecting to server at {SERVER_IP}:5000")


def receive_messages(client):
    while True:
        try:
            response = client.recv(1024)

            if not response:
                break

            data = json.loads(response.decode("utf-8"))

            print(f"\n[{data['sender']}] {data['message']}")

        except:
            break


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    client.connect((SERVER_IP, 5000))

    threading.Thread(target=receive_messages, args=(client,), daemon=True).start()

    while True:
        message = input("Write message: ")

        if message.lower() == "quit":
            break

        client.sendall(message.encode("utf-8"))
