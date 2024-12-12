import threading
import time
from datetime import datetime
from socket import *
import sys

import requests
cache = {}
cache_lock = threading.Lock()

def get_age(headers):
    for header in headers:
        if header.split()[0] == "Date":
            return header

def proxyServer(tcpCliSock):
    global cache, cache_lock
    request = (tcpCliSock.recv(1024).decode())
    if not request:
        return
    request_url = request.split("\r\n")[0].split()[1]
    if request.split("\r\n")[0].split()[0] != "GET":
        tcpCliSock.send("400".encode())
        return

    headers = requests.head(request_url)

    with cache_lock:
        if request_url in cache:
            request_age = get_age(headers)
            cache_age = cache.get(request_url)[1]
            if request_age != cache_age:
                request_obj = requests.get(request_url)
                cache.update({request_url: (request_obj, request_age)})
            else:
                request_obj = cache.get(request_url)[0]
        else:
            request_obj = requests.get(request_url)
            cache[request_url] = (request_obj, get_age(request_obj.headers))
    if request_obj.status_code >= 400:
        tcpCliSock.send(request_obj.status_code.to_bytes())
        return
    print('Connected to original destination')

    print('received reply from http server')
    response_headers = "\r\n".join(f"{key}: {value}" for key, value in request_obj.headers.items())
    tcpCliSock.sendall(f"HTTP/1.1 {request_obj.status_code} {request_obj.reason}\r\n".encode())
    tcpCliSock.sendall(f"{response_headers}\r\n\r\n".encode())
    tcpCliSock.sendall(request_obj.content)

    print('reply forwarded to client')
    # Close the client socket
    tcpCliSock.close()


def thread_handler(portNo):
    tcpSerSock = socket(AF_INET, SOCK_STREAM)
    tcpSerSock.bind(("0.0.0.0", portNo))
    tcpSerSock.listen(5)
    while True:
        print('Ready to serve')
        try:
            tcpCliSock, addr = tcpSerSock.accept()
            tid = threading.Thread(target=proxyServer, args=[tcpCliSock])
            tid.start()
        except KeyboardInterrupt:
            print("proxy exiting!")
            break
        print('Received a connection from: ', addr)

if __name__ == "__main__":
    # python proxyServer.py serverTCPPort
    if len(sys.argv) != 2:
        print("Usage: python3 proxyServer.py proxyTCPPort")
        sys.exit(1)
    else:
        thread_handler(int(sys.argv[1]))
        sys.exit(0)