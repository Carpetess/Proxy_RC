from socket import *
import sys

import requests
from urllib.parse import urlparse


def proxyServer(portNo):
    tcpSerSock = socket(AF_INET, SOCK_STREAM)
    tcpSerSock.bind(("0.0.0.0", portNo))
    tcpSerSock.listen(5)
    while True:
        print('Ready to serve')
        try:
            tcpCliSock, addr = tcpSerSock.accept()
        except KeyboardInterrupt:
            print("proxy exiting!")
            break
        print('Received a connection from:')#, addr)
        #Fill in start.
        request_rec = tcpCliSock.recv(1024).decode()
        request = request_rec.split("\r\n")
        method = request[0].split(" ")[0]
        url = request[0].split(" ")[1]
        headers, body = get_headers_body(request)

        print('Connecting to original destination')
        hostname = None
        for header in headers:
            if header.split(" ")[0] == "Host:":
                hostname = header.split(" ")[1]
        if hostname is not None:
            serverSocket = socket(AF_INET, SOCK_STREAM)
            serverSocket.connect((hostname, 80))
        else:
            reply = "4XX"
            break
        # Fill in start.
        # Create a socket and connect to port 80 of the host in the URL
        # If connect fails prepare reply with error message 4XX
        # Fill in end.
        print('Connected to original destination')
        serverSocket.send(request_rec.encode())
        response_rec = serverSocket.recv(4096)
        response = response_rec.decode().split("\r\n")
        print(response)
        status_numeric = response[0].split(" ")[1]
        status_textual = response[0].split(" ")[2]
        header_response, body_response = get_headers_body(response)
        # Fill in start.
        # Receive reply from server. Separate it in status (numeric
        # and textual, header lines and body (in the case of POST)
        # Fill in end.
        print('received reply from http server')
        tcpCliSock.send(response_rec)
        # Fill in start.
        # forward server’s reply to client
        # Fill in end.
        print('reply forwarded to client')
        # Close the client socket
        tcpCliSock.close()
        # Proxy server is terminated by control C.
    tcpSerSock.close()

def get_headers_body(request):
    headers = []
    body = []
    for item in request:
        if item != '' and item != request[0]:
            if item.split(" ")[0][-1] == ":":
                headers.append(item)
            else:
                body.append(item)

    return headers, body

if __name__ == "__main__":
    # python proxyServer.py serverTCPPort
    if len(sys.argv)!=2:
        print("Usage: python3 proxyServer.py proxyTCPPort")
        sys.exit(1)
    else:
        proxyServer(int(sys.argv[1]))
        sys.exit(0)