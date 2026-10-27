import socket
import os
from dotenv import load_dotenv
import threading
import json
import hashlib
from queue import Queue

from prompt_toolkit import PromptSession, print_formatted_text
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

SERVER_IP = os.getenv("SERVER_IP")  # Default to localhost if not set

logged_in = threading.Event()
current_username = None
auth_results = Queue()

prompt_style = Style.from_dict({
    "prompt": "ansicyan bold", # Customize the prompt style
    "": "ansiyellow", # Customize the input text style
})
auth_style = Style.from_dict({
    "prompt": "white bold", # Customize the prompt style
    "": "white", # Customize the input text style
})

session = PromptSession(erase_when_done=True, style=prompt_style) # Add erase_when_done=True to make the prompt disappear after input

print(f"Connecting to server at {SERVER_IP}:5000")

# TODO - welcome function from jespers lagra

# TODO - register function from johans lagra, needs server side implementation

def receive_packets(client): # TODO - maybe use global variable to decide if messages should be received or not, to avoid receiving messages when logged out. This should be set in the login and logout functions.
    while True:
        try:
            response = client.recv(1024)

            if not response:
                break

            packet = json.loads(response.decode("utf-8"))
            action = packet.get("action")
            data = packet.get("data")

            if action in {"auth_login_status", "auth_logout_status"}:
                auth_results.put(data)

            if action == "message" and logged_in.is_set():
                print(f"{data['sender_username']}: {data['message']}")

        except:
            break


def login():
    username = session.prompt("Username: ", is_password=False, placeholder=HTML('<gray><italic>Enter your username...</italic></gray>'), style=auth_style)
    print_formatted_text(HTML('<bold>Username:</bold> {}').format(username))
    password = password_hash(session.prompt("Password: ", is_password=True, placeholder=HTML('<gray><italic>Enter your password...</italic></gray>'), style=auth_style))

    packet = {
        "action": "login",
        "data": {
            "username": username, # example usernames are user1 and user2
            "password": password # example passwords are password and 123456
        }
    }

    send(packet)


def authenticate():
    while True:
        login()
        result = auth_results.get()
        status = result.get("status")
        message = result.get("message")

        if status == "login_response_success":
            global current_username
            current_username = result.get("username")
            logged_in.set()
            print(f"Login successful!")
            auth_results.task_done()
            return

        logged_in.clear()
        print(f"Login failed: {message}")
        
        auth_results.task_done()


def password_hash(password):
    return hashlib.sha256(password.encode(encoding = 'UTF-8', errors = 'strict')).hexdigest()

def logout():
    global current_username

    packet = {
        "action": "logout",
        "data": {}
    }

    send(packet)

    result = auth_results.get()
    if result.get("status") == "logout_response_success":
        logged_in.clear()
        current_username = None
        print("You are now logged out.")
    else:
        print(f"Logout failed: {result.get('message', 'Unknown error.')}")
    auth_results.task_done()

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

            message = session.prompt("> ", is_password=False, placeholder=placeholder, style=prompt_style)

            if not message.strip(): # Avoid sending empty messages
                continue

            command_action = check_message_for_commands(message)

            if command_action == "quit":
                break

            if command_action == "message":
                    

                print(f"You: {message}")

                packet = {
                    "action": command_action,
                    "data": {
                        "message": message,
                        "username": current_username,
                    }
                }

                send(packet)
