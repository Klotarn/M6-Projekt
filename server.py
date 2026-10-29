import socket
import threading
import json
from ast import literal_eval as make_tuple

messages_path = "./messages.json".encode("utf8")
messages_fallback_path = "./messages_example.json".encode("utf8")
users_path = "./users.json".encode("utf8")
users_fallback_path = "./users_example.json".encode("utf8")
access_option = "a"
write_option = "w"

clients = []
clients_lock = threading.Lock()


# --------------------------------------------------------------------------
# Functions


def access_messages(option, messages):
    if option == access_option:
        try:
            with open(messages_path) as f:
                return json.load(f)
        except:
            with open(messages_fallback_path) as f:
                return json.load(f)

    if option == write_option:
        data_to_write = json.dumps(messages, indent=4)
        with open(messages_path, "w") as f:
            f.write(data_to_write)

def access_users(option, users): # TODO - refactor so that only one user is changed at a time
    if option == access_option:
        try:
            with open(users_path) as f:
                return json.load(f)
        except:
            with open(users_fallback_path) as f:
                return json.load(f)

    if option == write_option:
        data_to_write = json.dumps(users, indent=4)
        with open(users_path, "w") as f:
            f.write(data_to_write)


# Store messages in the JSON "database"
def add_message_to_messages(sender, message):
    messages = access_messages(access_option, None)
    messages["messages"].append({"sender": sender, "message": message})
    access_messages(write_option, messages)


def send_packet_to_client(client_socket, packet):
    client_socket.sendall(json.dumps(packet).encode("utf-8"))


# Sends message to all connected clients except the sender.
def broadcast(sender_socket, message):
    with clients_lock:
        sender = next(
            (client for client in clients if client["socket"] == sender_socket),
            None,
        )

    if sender is None or sender["username"] is None:
        return

    sender_username = sender["username"]
    print(f"Broadcasting message from {sender_username}: {message}")
    add_message_to_messages(sender_username, message)

    with clients_lock:
        disconnected = []

        for client in clients:
            try:
                if client["socket"] == sender_socket:
                    continue # Skip sending the message back to the sender

                packet = {
                    "action": "message",
                    "data": {
                        "sender_username": sender_username,
                        "message": message,
                    }
                }

                send_packet_to_client(client["socket"], packet)
            except:
                disconnected.append(client)

        for client in disconnected:
            clients.remove(client)


# TODO - auth function to handle login and logout, and user creation. This function should be called in the handle_client function when a client connects.

# TODO - create_user function

def create_user(client_socket, username, password):
    users=access_users(access_option, None)

    if username in users:
        print(f"Signup failed. user {username} already exists.")
        packet = {
                    "action": "auth_login_status",
                    "data": {"status": "login_response_failure", "message": f"Username {username} is not available. Please select another username."}
                }
        send_packet_to_client(client_socket, packet)

    else:
        users["users"].append({"username": username, "password": password})
        access_users(write_option, users)
        print(f"New user {username} sucessfully registered")

def login(client_socket, username, password):
    users = access_users(access_option, None)
    if not any(
        user["username"] == username and user["password"] == password
        for user in users["users"]
    ):
        print(f"Failed login attempt for user {username}.")
        packet = {
            "action": "auth_login_status",
            "data": {"status": "login_response_failure", "message": "Invalid username or password."}
        }
        send_packet_to_client(client_socket, packet)
    else:
        print(f"User {username} logged in successfully.")
        with clients_lock:
            for client in clients:
                if client["socket"] == client_socket:
                    client["username"] = username
                    break

        packet = {
            "action": "auth_login_status",
            "data": {
                "status": "login_response_success",
                "message": "Login successful.",
                "username": username,
            }
        }
        send_packet_to_client(client_socket, packet)

def logout(client_socket):
    print(f"Client {client_socket.getpeername()} logged out.")
    packet = {
        "action": "auth_logout_status",
        "data": {"status": "logout_response_success", "message": "Logout successful."}
    }
    send_packet_to_client(client_socket, packet)
    with clients_lock:
        for client in clients:
            if client["socket"] == client_socket:
                client["username"] = None
                break

def handle_client(client_socket, client_address):
    print(f"Connection from {client_address} has been established!")

    with clients_lock:
        clients.append({
            "address": client_address,
            "socket": client_socket,
            "username": None,
        })

    try:
        while True:
            # Here is where the data from the client is received. The server will wait for data from the client, and when it receives data, it will process it accordingly.
            data = client_socket.recv(1024)

            if not data:
                break

            # Here is where the data from the client is processed.
            packet = json.loads(data.decode("utf-8"))
            action = packet["action"]

            if action == "signup":
                username = packet["data"]["username"]
                password = packet["data"]["password"]
                create_user(client_socket, username, password)

            if action == "login":
                username = packet["data"]["username"]
                password = packet["data"]["password"]
                login(client_socket, username, password)

            if action == "logout":
                logout(client_socket)

            if action == "quit":
                print(f"Client {client_address} requested to disconnect.")
                break

            if action == "message":
                broadcast(client_socket, packet["data"]["message"])

    except (ConnectionResetError, ConnectionAbortedError):
        # A client that closes abruptly can reset the connection on Windows.
        pass
    finally:
        with clients_lock:
            for client in clients:
                if client["socket"] == client_socket:
                    clients.remove(client)
                    break
        client_socket.close()


# --------------------------------------------------------------------------
# Program execution start


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", 5000))
server.listen(5)

print("Server is listening on port 5000...")

while True:
    client_socket, client_address = server.accept()

    thread = threading.Thread(
        target=handle_client, args=(client_socket, client_address)
    )

    thread.daemon = True
    thread.start()
