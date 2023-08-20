import http.server
import socketserver
import miniupnpc

class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # You can modify this part to handle requests and responses as needed
        # For this example, we'll just forward the request downstream
        downstream_address = ('127.0.0.1', 8081)  # Local machine, nginx port 8080
        downstream_response = self.forward_request(downstream_address)

        self.send_response(downstream_response.status)
        for header, value in downstream_response.headers.items():
            self.send_header(header, value)
        self.end_headers()
        self.wfile.write(downstream_response.content)

    def forward_request(self, address):
        # You can use any library to send requests to the downstream server
        import requests
        response = requests.get(f"http://{address[0]}:{address[1]}{self.path}")
        return response

def main():
    # Initialize UPnP and add a port mapping
    upnp = miniupnpc.UPnP()
    upnp.discoverdelay = 200
    upnp.discover()
    upnp.selectigd()
    try:
        print(internal_port)
        upnp.addportmapping(external_port, 'TCP', upnp.lanaddr, internal_port,
                            'Proxy Server', '')
        print("Port mapping added successfully")
    except Exception as e:
        print(f"Error adding port mapping: {e}")
    # Set up the proxy server
    proxy_port = 8081  # Change this to the desired proxy port
    with socketserver.TCPServer(('', proxy_port), ProxyHandler) as server:
        print(f"Proxy server is running on port {proxy_port}")
        server.serve_forever()

if __name__ == "__main__":
    external_port = 80  # External port you want to forward
    internal_port = 8080   # Internal port of the downstream nginx server
    main()
