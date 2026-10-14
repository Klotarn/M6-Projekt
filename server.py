import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", 5000))
server.listen(5)

print("Server is listening on port 5000...")

while True:
    client_socket, client_address = server.accept()
    print(f"Connection from {client_address} has been established!")

    # Receive data from the client
    data = client_socket.recv(1024).decode("utf-8")
    print(f"Received data {data} from {client_address}")

    # Send a response back to the client
    response = "Server is responding!"
    client_socket.sendall(response.encode("utf-8"))

    # Close the connection
    client_socket.close()
