import socket
import sys
import time


MAX_FILE_SIZE = 1024 * 1024

end_of_message_indicator = b"\r\r\r\r\r"

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
            print(user_input)
            client_socket.send(user_input.encode('utf-8'))
            response = b''  # Initialize an empty bytes object to hold the complete response

            while True:
                chunk = client_socket.recv(MAX_FILE_SIZE)
                if not chunk or chunk == end_of_message_indicator:
                    break
                response += chunk
                #print("Server response:", response.decode('utf-8'))

            print("Server response:", response.decode('utf-8'))
            time.sleep(0.5)

    except Exception as e:
        print("Error:", e)
    finally:
        client_socket.close()

if __name__ == '__main__':
    main()
