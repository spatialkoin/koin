import socket

def main():
    server_ip = '127.0.0.1'  # Replace with the server's IP address
    server_port = 12345      # Replace with the server's port number

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect((server_ip, server_port))
        print(f"Connected to {server_ip}:{server_port}")

        message = "Hello, server!"
        client_socket.send(message.encode('utf-8'))

        response = client_socket.recv(1024)
        print("Server response:", response.decode('utf-8'))

    except Exception as e:
        print("Error:", e)
    finally:
        client_socket.close()

if __name__ == '__main__':
    main()
