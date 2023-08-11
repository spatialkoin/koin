import socket
import threading
import miniupnpc
import os
import hashlib
import signal
import time
import requests

# Global variable to track the server socket
server_socket = None
upnp = None

register = "../register/"
files = "../files/"

def handle_client(client_socket):
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break
            decoded_data = data.decode('utf-8')
            print("Received:", decoded_data)

            command, *rest = decoded_data.split(maxsplit=1)
            client_ip = client_socket.getpeername()[0]
            ip_filename = os.path.join(register, f"{client_ip}.ip")
            with open(ip_filename, 'w') as ip_file:
                ip_file.write(client_ip)

            if command == "GET":
                file_name = files + rest[0]
                if os.path.exists(file_name):
                    with open(file_name, 'r') as file:
                        file_content = file.read()
                        response = "File content:\n" + file_content
                else:
                    response = "File not found"
            elif command == "LIST":
                file_list = "\n".join(os.listdir(files))
                response = "File list:\n" + file_list
            else:

                file_hash = hashlib.sha256(decoded_data.encode('utf-8')).hexdigest()
                file_name = file_hash + ".txt"
                path_file_name = files + file_name
                with open(path_file_name, 'w') as file:
                    file.write(decoded_data)
                response = f"Data saved to file with hash as name: {file_name}, IP address registered."

            client_socket.send(response.encode('utf-8'))
        except Exception as e:
            print("Error:", e)
            break
    client_socket.close()


def cleanup_and_exit(signum, frame):
    global server_socket, upnp

    print("Received termination signal. Cleaning up and exiting...")

    if upnp:
        upnp.deleteportmapping(port, 'TCP')
        upnp.mappedaddress = ''  # Release the mapped IP address

    if server_socket:
        server_socket.close()

    # You can add additional cleanup code here if needed

    print("Cleanup complete. Exiting.")
    exit(0)

def register_thread():
    while True:
        try:
            time.sleep(60)  # Wait for 60 seconds before checking again
            for ip_filename in os.listdir(register):
                with open(os.path.join(register, ip_filename), 'r') as ip_file:
                    target_ip = ip_file.read().strip()
                    print("Connecting to registered IP:", target_ip)
                    try:
                        # You can implement your logic here to make outgoing connections to target_ip
                        # For example, you can use sockets to connect to the target_ip.
                        # You can reuse some parts of your handle_client function here.
                        server_ip = target_ip
                        server_port = 12345      # Replace with the server's port number

                        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                        try:
                            client_socket.connect((server_ip, server_port))
                            print(f"Connected to {server_ip}:{server_port}")
                            user_input = "LIST"
                            client_socket.send(user_input.encode('utf-8'))
                            response = client_socket.recv(1024)
                            print("Server response:", response.decode('utf-8'))

                        except Exception as e:
                            print("Error:", e)
                        finally:
                            client_socket.close()

                        pass
                    except Exception as e:
                        print("Error connecting to", target_ip, ":", e)
        except Exception as e:
            print("Error in register thread:", e)

def main():
    global server_socket

    host = ''
    port = 12345

    # Set up signal handling for termination
    signal.signal(signal.SIGINT, cleanup_and_exit)
    signal.signal(signal.SIGTERM, cleanup_and_exit)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)

    print(f"Server listening on {host}:{port}")

    upnp = miniupnpc.UPnP()
    upnp.discoverdelay = 200
    upnp.discover()

    try:
        if upnp.selectigd():
            external_ip = upnp.externalipaddress()
            print("External IP Address:", external_ip)

            result = upnp.addportmapping(
                port, 'TCP', upnp.lanaddr, port,
                'Python UPnP Example', '')

            if result:
                print("Port mapping created successfully.")
            else:
                print("Failed to create port mapping.")
                return
        else:
            raise Exception("No UPnP device found")
    except Exception as e:
        # Use an external service to determine public IP address
        response = requests.get('https://httpbin.org/ip')
        if response.status_code == 200:
            external_ip = response.json()['origin']
            print("Public IP Address:", external_ip)
        else:
            print("Failed to retrieve public IP address.")
            return

    # Start the register thread
    register_thread_handler = threading.Thread(target=register_thread)
    register_thread_handler.start()

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Accepted connection from {client_address[0]}:{client_address[1]}")

        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

if __name__ == '__main__':
    main()
