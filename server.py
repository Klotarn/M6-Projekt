import socket
import threading
import json
from ast import literal_eval as make_tuple

user_data_path = "./messages.json".encode("utf8")
user_data_fallback_path = "./messages_example.json".encode("utf8")
access_option = "a"
write_option = "w"

clients = []
clients_lock = threading.Lock()


# --------------------------------------------------------------------------
# Functions


def access_messages(option, messages):
    if option == access_option:
        try:
            with open(user_data_path) as f:
                return json.load(f)
        except:
            with open(user_data_fallback_path) as f:
                return json.load(f)

    if option == write_option:
        data_to_write = json.dumps(messages, indent=4)
        with open(user_data_path, "w") as f:
            f.write(data_to_write)


# Store messages in the JSON "database"
def add_message_to_messages(sender, message):
    messages = access_messages(access_option, None)
    messages["messages"].append({"sender": sender, "message": message})
    access_messages(write_option, messages)


def send_packet_to_client(client_socket, packet):
    client_socket.sendall(json.dumps(packet).encode("utf-8"))


# Sends message to all connected clients except the sender.
def broadcast(client_address, message):
    print(f"Broadcasting message from {client_address}: {message}")

    add_message_to_messages(client_address, message)

    PACKET = json.dumps({"sender": str(client_address), "message": message})

    with clients_lock:
        disconnected = []

        for client in clients:
            try:
                message_dict = json.loads(PACKET)
                sender = make_tuple(message_dict["sender"])
                if client["address"] == sender:
                    continue  # Skip sending the message back to the sender

                packet = {
                    "action": "message",
                    "data": message_dict
                }

                send_packet_to_client(client["socket"], packet)
            except:
                disconnected.append(client)

        for client in disconnected:
            clients.remove(client)


# TODO - auth function to handle login and logout, and user creation. This function should be called in the handle_client function when a client connects.

# TODO - create_user function

# TODO - login function

# TODO - logout handling. this should be triggered either when message is "quit" or when a certain logout command is sent from the client.


def handle_client(client_socket, client_address):
    print(f"Connection from {client_address} has been established!")

    with clients_lock:
        clients.append({"address": client_address, "socket": client_socket})

    try:
        while True:
            data = client_socket.recv(1024)

            if not data:
                break

            # TODO - here is where the data from the client is received and processed. This is where login, logout and user creation should be handled.
            packet = json.loads(data.decode("utf-8"))
            action = packet["action"]
            target = packet.get("target")  # Use .get() to avoid KeyError if "target" is not present

            if action == "message":
                broadcast(client_address, packet["data"])

    finally:
        with clients_lock:
            for client in clients:
                if client["socket"] == client_socket:
                    clients.remove(client)
                    break


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
