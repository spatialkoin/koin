import socket
import threading
import miniupnpc

def handle_client(client_socket):
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break
            decoded_data = data.decode('utf-8')
            print("Received:", decoded_data)

            response = "Message received: " + decoded_data
            client_socket.send(response.encode('utf-8'))
        except Exception as e:
            print("Error:", e)
            break
    client_socket.close()

def main():
    host = ''       # Listen on all available network interfaces
    port = 12345    # Choose a port number

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)  # Allow up to 5 client connections in the queue

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
