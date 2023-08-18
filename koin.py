import socket
import threading
import miniupnpc
import os
import hashlib
import signal
import time
import requests
import pickle
import re

# Global variable to track the server socket
server_socket = None
upnp = None
MAX_FILE_SIZE = 1024 * 1024
register = "../register/"
files = "../files/"
document_index = '../document_index.pkl'

end_of_message_indicator = b'\r'

class DocumentIndex:
    def __init__(self, index_file_path, model_directory):
        self.index_file_path = index_file_path
        self.model_directory = model_directory
        self.index = {}

        if os.path.exists(self.index_file_path):
            with open(self.index_file_path, 'rb') as index_file:
                self.index = pickle.load(index_file)

    def add_document(self, model_name, file_name, model, file_content):
        self.index[file_name] = {'model_name': model_name, 'model_file': self._save_model(model), 'content': file_content}
        self._save_index()

    def _save_index(self):
        with open(self.index_file_path, 'wb') as index_file:
            pickle.dump(self.index, index_file)

    def _save_model(self, model):
        model_file_name = os.path.join(self.model_directory, f"{len(self.index)}_model.pkl")
        with open(model_file_name, 'wb') as model_file:
            pickle.dump(model, model_file)
        return model_file_name

    def search_by_model(self, model_name):
        matching_files = [file_name for file_name, data in self.index.items() if data['model_name'] == model_name]
        return matching_files

    def search_by_string(self, search_string):
        matching_files = [file_name for file_name, data in self.index.items() if self._string_in_file(search_string, data['content'])]
        return matching_files

    def _string_in_file(self, search_string, model_content):
        escaped_search_string = re.escape(search_string)
        pattern = re.compile(escaped_search_string, re.IGNORECASE)
        match = re.search(pattern, model_content)
        return match is not None


def index_for_search():
    while True:
        # Sample index data structure
        sample_index_data = {
            # Add more files if needed
        }

        # Save the sample index data to a file
        with open(document_index, 'wb') as index_file:
            pickle.dump(sample_index_data, index_file)

        print("Sample index data saved to 'document_index.pkl'.")

        # Example model (replace this with your actual model instance)
        example_model = {'model_data': 'example model data'}

        index = DocumentIndex(document_index, '../models')


        with open(document_index, 'rb') as index_file:
            index_data = pickle.load(index_file)
        print(index_data)


        text_files_directory = '../files'  # Replace this with the actual directory path
        model_name = 'example_model'  # Replace this with a meaningful model name

        for filename in os.listdir(text_files_directory):
            if filename.endswith('.txt'):
                file_path = os.path.join(text_files_directory, filename)
                with open(file_path, 'r') as file:
                    file_content = file.read()

                index.add_document(model_name, filename, example_model, file_content)

        time.sleep(3)

def handle_client(client_socket):
    while True:
        try:
            data = client_socket.recv(MAX_FILE_SIZE)
            if not data:
                break
            decoded_data = data.decode('utf-8')
            print("Received:", decoded_data)

            command, *rest = decoded_data.split(maxsplit=1)
            client_ip = client_socket.getpeername()[0]
            ip_filename = os.path.join(register, f"{client_ip}.ip")
            with open(ip_filename, 'w') as ip_file:
                ip_file.write(client_ip)


            print(f"Received command: '{command}'")
            if command == "GET":
                file_name = files + rest[0]
                if os.path.exists(file_name):
                    with open(file_name, 'r') as file:
                        file_content = file.read()
                        response = "File content:\n" + file_content
                else:
                    response = "File not found"
            elif command == "LIST_IP":
                print("Executing LIST IP branch")
                file_list = "\n".join(os.listdir(register))
                response = "IP list:\n" + file_list
            elif command == "LIST":
                print("Executing LIST branch")
                file_list = "\n".join(os.listdir(files))
                response = "File list:\n" + file_list
            elif command == "SEARCH":
                # Initialize the DocumentIndex with the existing index data
                model_directory = '../models'  # Replace with the actual directory path for models
                index = DocumentIndex(document_index, model_directory)
                search_string = rest[0]  # Replace this with the string you want to search for

                matching_filenames = []
                for filename, data in index.index.items():
                    if isinstance(data, dict):
                        model_name = data.get('model_name', '')
                        if model_name == 'example_model':
                            content = data.get('content', '')
                            if re.search(search_string, content, re.IGNORECASE):
                                matching_filenames.append(f"file: {filename}")
                                print(f"Matching content found in file: {filename}")

                if matching_filenames:
                    response = "\n".join(matching_filenames)
                else:
                    response = "No matching content found."

            else:
                file_hash = hashlib.sha256(decoded_data.encode('utf-8')).hexdigest()
                file_name = file_hash + ".txt"
                path_file_name = files + file_name
                with open(path_file_name, 'w') as file:
                    file.write(decoded_data)
                response = f"Data saved to file with hash as name: {file_name}, IP address registered.\n"

            print("TEST 0")
            response_size_mb = len(response.encode('utf-8')) / (1024 * 1024)  # Convert bytes to megabytes
            print("Response size:", response_size_mb, "MB")  # Print the size in megabytes
            client_socket.send(response.encode('utf-8'))
            print("TEST 1")
            client_socket.send(end_of_message_indicator)
            print("TEST 2")
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

def register_thread(external_ip):
    while True:
        try:
            time.sleep(6)  # Wait for 60 seconds before checking again
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
                            user_input = "LIST_IP"
                            client_socket.send(user_input.encode('utf-8'))
                            response = b''  # Initialize an empty bytes object to hold the complete response

                            while True:
                                chunk = client_socket.recv(MAX_FILE_SIZE)
                                if not chunk or chunk == end_of_message_indicator:
                                    break
                                response += chunk
                                print("Server response:", response.decode('utf-8'))

                            print("Server response:", response.decode('utf-8'))
                            response_text = response.decode('utf-8')
                            lines = response_text.split('\n')

                            txt_lines = [line.replace(".ip", "") for line in lines if ".ip" in line]
                            for txt_line in txt_lines:
                                print("SAVE IP " + str(external_ip) + " IP" + txt_line)
                                ip_filename = os.path.join(register, f"{txt_line}.ip")
                                if not os.path.exists(ip_filename) and str(external_ip) != txt_line:
                                    with open(ip_filename, 'w') as ip_file:
                                        ip_file.write(txt_line)

                            user_input = "LIST"
                            client_socket.send(user_input.encode('utf-8'))
                            response = b''  # Initialize an empty bytes object to hold the complete response

                            while True:
                                chunk = client_socket.recv(MAX_FILE_SIZE)
                                if not chunk or chunk == end_of_message_indicator:
                                    break
                                response += chunk
                                print("Server response:", response.decode('utf-8'))

                            print("Server response:", response.decode('utf-8'))
                            response_text = response.decode('utf-8')
                            lines = response_text.split('\n')

                            txt_lines = [line for line in lines if ".txt" in line]

                            for txt_line in txt_lines:
                                print("GET "+ txt_line)
                                commnd_file = "GET "+ txt_line
                                client_socket.send(commnd_file.encode('utf-8'))
                                response = b''  # Initialize an empty bytes object to hold the complete response

                                while True:
                                    chunk = client_socket.recv(MAX_FILE_SIZE)
                                    if not chunk or chunk == end_of_message_indicator:
                                        break
                                    response += chunk
                                    print("Server response:", response.decode('utf-8'))

                                response_text = response.decode('utf-8')

                                print(response_text)
                                prefix = "File content:"
                                if response_text.startswith(prefix):
                                    content_start_index = response_text.index("\n", len(prefix)) + 1
                                    file_content = response_text[content_start_index:]

                                    print("File content Removed:")
                                    print(file_content)

                                    file_hash = hashlib.sha256(file_content.encode()).hexdigest()
                                    print("File hash:")
                                    print(file_hash)
                                    file_name = file_hash + ".txt"
                                    path_file_name = files + file_name

                                    try:
                                        with open(path_file_name, 'x') as file:
                                            file.write(file_content)
                                        response = f"Data saved to file with hash as name: {file_name}, IP address registered.\n"
                                    except FileExistsError:
                                        response = f"File with name '{file_name}' already exists. Data not saved.\n"

                                    print(response)

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
    register_thread_handler = threading.Thread(target=register_thread, args=(external_ip,))
    register_thread_handler.start()


    index_for_search_thread_handler = threading.Thread(target=index_for_search)
    index_for_search_thread_handler.start()

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Accepted connection from {client_address[0]}:{client_address[1]}")

        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

if __name__ == '__main__':
    main()
