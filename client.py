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

HELP_MESSAGE = """
The following commands are available:
/help, Displays this help message
/quit, Exits the application
"""
# /whisper, Sends a private message to a selected user. type /whisper [user] [message]

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

    send(packet)


def authenticate():
    # auth_results.queue.clear()
    while True:
        login()
        result = auth_results.get()
        status = result.get("status")
        message = result.get("message")

        if status == "login_response_success":
            print(f"Login successful!")
            return

        print(f"Login failed: {message}")


def password_hash(password):
    return hashlib.sha256(password.encode(encoding = 'UTF-8', errors = 'strict')).hexdigest()

def logout():
    packet = {
        "action": "logout",
        "data": {}
    }

    send(packet)
    
    authenticate()

def quit():
    packet = {
        "action": "quit",
        "data": {}
    }

    send(packet)

    print("Disconnected from server.")

def check_message_for_commands(message):
    if message[0] == "/":
        if message == "/quit":
            quit()
            return "quit"

        if message == "/logout":
            logout()
            return "logout"

        if message == "/register":
            print("Registration functionality is not implemented yet.")
            return None

        # if message[0-7] == "/whisper":
        #     print("Du har valt att viska, din lilla busunge")
        #     whisper(message)

        if message == "/help":
            print(HELP_MESSAGE)
            return None
        else:
            print("Unknown command. Type /help for a list of commands")
            return None
    else:
        return "message"


# def whisper(message):
#     message_list = message.split(" ")

#     packet = {
#         "action": "whisper",
#         "data": {
#             "target": message_list[1],
#             "message": message_list[2]
#         }
#     }

#     send(packet)

def send(packet):
    packet = json.dumps(packet)  # Convert the packet to a JSON string before sending
    client.sendall(packet.encode("utf-8"))
    return


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

            command_action = check_message_for_commands(message)

            if command_action == "quit":
                break

            if command_action == "message":
                    

                print(f"You: {message}")

                packet = {
                    "action": command_action,
                    "data": message
                }

                send(packet)
