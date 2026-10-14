import socket
import os
from dotenv import load_dotenv

load_dotenv()

SERVER_IP = os.getenv("SERVER_IP")  # Default to localhost if not set

print(f"Connecting to server at {SERVER_IP}:5000")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER_IP, 5000)) # Change "localhost" to the IP address of the server
print(client.getsockname())