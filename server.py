import socket
import threading
import json

user_data_path = "./userdata.json".encode("utf8")
user_data_fallback_path = "./userdata_example.json".encode("utf8")
access_option = "a"
write_option = "w"

clients = []
clients_lock = threading.Lock()


# --------------------------------------------------------------------------
# Functions


def access_userdata(option, user_data):
    if option == access_option:
        try:
            with open(user_data_path) as f:
                return json.load(f)
        except:
            with open(user_data_fallback_path) as f:
                return json.load(f)

    if option == write_option:
        data_to_write = json.dumps(user_data, indent=4)
        with open(user_data_path, "w") as f:
            f.write(data_to_write)


def add_message_to_userdata(sender, message):
    user_data = access_userdata(access_option, None)
    user_data["messages"].append({"sender": sender, "message": message})
    access_userdata(write_option, user_data)

    print(f"User data: {user_data}")


def broadcast(message):
    with clients_lock:
        disconnected = []

        for client in clients:
            try:
                client.sendall(message.encode("utf-8"))
            except:
                disconnected.append(client)

        for client in disconnected:
            clients.remove(client)


def handle_client(client_socket, client_address):
    print(f"Connection from {client_address} has been established!")

    with clients_lock:
        clients.append(client_socket)

    try:
        while True:
            data = client_socket.recv(1024)

            if not data:
                break

            message = data.decode("utf-8")
            print(f"Received data {message} from {client_address}")

            add_message_to_userdata(client_address, message)

            response = json.dumps({"sender": str(client_address), "message": message})

            broadcast(response)

    finally:
        with clients_lock:
            if client_socket in clients:
                clients.remove(client_socket)


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
