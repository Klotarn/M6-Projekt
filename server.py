import socket
import json

user_data_path = "./userdata.json".encode("utf8")
user_data_fallback_path = "./userdata_example.json".encode("utf8")
access_option = "a"
write_option = "w"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", 5000))
server.listen(5)

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

print("Server is listening on port 5000...")

while True:
    client_socket, client_address = server.accept()
    print(f"Connection from {client_address} has been established!")

    with client_socket:
        while True:
            data = client_socket.recv(1024)
            user_data = access_userdata(access_option, None)

            if not data:
                break

            message = data.decode("utf-8")
            print(f"Received data {message} from {client_address}")
            
            user_data.update({
                "sender": client_address,
                "message": message
            })
            access_userdata(write_option, user_data)

            response = "Server is responding!"
            client_socket.sendall(response.encode("utf-8"))