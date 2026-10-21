import socket
import os
from dotenv import load_dotenv

load_dotenv()

SERVER_IP = os.getenv("SERVER_IP")  # Default to localhost if not set

print(f"Connecting to server at {SERVER_IP}:5000")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    client.connect((SERVER_IP, 5000))

    while True:
        message = input("Skicka ett meddelande: ")

        if message.lower() == "quit":
            break

        client.sendall(message.encode("utf-8"))
        response = client.recv(1024).decode("utf-8")
        print(response)