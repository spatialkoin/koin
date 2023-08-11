import socket
import threading
import miniupnpc
import os
import hashlib
import signal

# Global variable to track the server socket
server_socket = None
upnp = None

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
                response = "Data saved to file with hash as name: " + file_name

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
    upnp.selectigd()

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

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Accepted connection from {client_address[0]}:{client_address[1]}")

        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

if __name__ == '__main__':
    main()
