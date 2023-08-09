import socket
import sys

def main():
    if len(sys.argv) != 2:
        print("Usage: python client.py <server_ip>")
        return

    server_ip = sys.argv[1]
    server_port = 12345      # Replace with the server's port number

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect((server_ip, server_port))
        print(f"Connected to {server_ip}:{server_port}")

        while True:
            user_input = input("Enter a message to send to the server (type 'exit' to quit): ")
            if user_input.lower() == 'exit':
                break

            client_socket.send(user_input.encode('utf-8'))

            response = client_socket.recv(1024)
            print("Server response:", response.decode('utf-8'))

    except Exception as e:
        print("Error:", e)
    finally:
        client_socket.close()

if __name__ == '__main__':
    main()
