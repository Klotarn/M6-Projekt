import socket
import os
from dotenv import load_dotenv
import threading
import json
import getpass
import hashlib
from queue import Queue

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
auth_results = Queue()

print(f"Connecting to server at {SERVER_IP}:5000")

# TODO - welcome function from jespers lagra

# TODO - login function - use hashing from johans lagra, needs server side implementation

# TODO - logout function, needs server side implementation

# TODO - register function from johans lagra, needs server side implementation

# TODO - login_failed from jespers lagra

# TODO - quit from jespers lagra

def receive_packets(client): # TODO - maybe use global variable to decide if messages should be received or not, to avoid receiving messages when logged out. This should be set in the login and logout functions.
    while True:
        try:
            response = client.recv(1024)

            if not response:
                break

            packet = json.loads(response.decode("utf-8"))
            action = packet.get("action")
            data = packet.get("data")

            if action == "auth_status":
                auth_results.put(data)

            if action == "message":
                print(f"[{data['sender']}] {data['message']}")

        except:
            break


def login():
    username = input("Username: ")
    password = password_hash(getpass.getpass())

    packet = {
        "action": "login",
        "data": {
            "username": username, # example usernames are user1 and user2
            "password": password # example passwords are password and 123456
        }
    }

    packet = json.dumps(packet)  # Convert the packet to a JSON string before sending

    client.sendall(packet.encode("utf-8"))


def authenticate():
    while True:
        login()
        result = auth_results.get()
        status = result.get("status")
        message = result.get("message")

        if status == "success":
            print(f"Login successful!")
            return

        print(f"Login failed: {message}")


def password_hash(password):
    return hashlib.sha256(password.encode(encoding = 'UTF-8', errors = 'strict')).hexdigest()


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    client.connect((SERVER_IP, 5000))


    threading.Thread(target=receive_packets, args=(client,), daemon=True).start()

    authenticate()

    # TODO - here is where main menu should be implemented with login, logout, register and quit options. Keep in a while loop, but check if patch_stdout might be something like instances which would be bad to start many of
    # TODO - Only execute following code if user is logged in
    with patch_stdout(): # Makes user input stick to bottom and allows messages to be printed above it
        while True:
            placeholder = HTML('<gray><italic>Write your message here...</italic></gray>')

            message = session.prompt("> ", placeholder=placeholder)

            if not message.strip(): # Avoid sending empty messages
                continue

            print(f"You: {message}")

            if message.lower() == "quit":
                break # TODO - this sends the user back to the main menu, but should also send a logout message to the server. This should be handled with a logout function.

            packet = {
                "action": "message",
                "data": message
            }

            packet = json.dumps(packet)  # Convert the packet to a JSON string before sending

            client.sendall(packet.encode("utf-8"))
