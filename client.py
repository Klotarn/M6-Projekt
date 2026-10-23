import socket
import os
from dotenv import load_dotenv
import threading
import json

from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML

load_dotenv()

style = Style.from_dict({
    "prompt": "ansicyan bold", # Customize the prompt style
    "": "ansiyellow", # Customize the input text style
})
session = PromptSession(erase_when_done=True, style=style) # Add erase_when_done=True to make the prompt disappear after input

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

    with patch_stdout(): # Makes user input stick to bottom and allows messages to be printed above it
        while True:
            placeholder = HTML('<gray><italic>Write your message here...</italic></gray>')

            message = session.prompt("> ", placeholder=placeholder)

            if not message.strip(): # Avoid sending empty messages
                continue

            print(f"You: {message}")

            if message.lower() == "quit":
                break

            client.sendall(message.encode("utf-8"))
