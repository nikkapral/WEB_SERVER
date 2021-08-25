from socket import socket
from threading import Thread, Lock
from datetime import datetime


class Client(Thread):
    def __init__(self, addr, conn):
        Thread.__init__(self, name=str(addr[0]) + " " + str(addr[1]))
        self.host = addr[0]
        self.port = addr[1]
        self.conn = conn

    def run(self):
        request = self.conn.recv(DATA_SIZE).decode()
        if request != '':
            print(request)

            headers = request.split('\n')
            webpage = headers[0].split()[1]
            if webpage == '/':
                webpage = '/index.html'
            elif '.' not in webpage:
                webpage += '.html'

            if webpage.split('.')[-1] in FILES:
                try:
                    try:
                        with open(DEFAULT_FOLDER + webpage, 'r') as f:
                            content = f.read()
                        response = """HTTP/1.1 200 OK
                                Server: WebServer
                                Content-type: text/html
                                Content-length: 5000
                                Connection: close\n\n""" + content
                    except UnicodeDecodeError:
                        with open(DEFAULT_FOLDER + webpage, 'rb') as f:
                            content = f.read()
                        response = """HTTP/1.1 200 OK
                                Server: WebServer
                                Content-type: image/png
                                Content-length: 5000
                                Connection: close\n\n"""
                    with lock:
                        with open('log/log.txt', 'a+') as log:
                            log.write(str(datetime.now().strftime("%d/%m/%Y %H:%M:%S")) + ' || ' + self.host
                                      + ' || ' + webpage + ' || None\n')
                except FileNotFoundError:
                    response = 'HTTP/1.0 404 NOT FOUND\n\nPage Not Found!'
                    with lock:
                        with open('log/log.txt', 'a+') as log:
                            log.write(str(datetime.now().strftime("%d/%m/%Y %H:%M:%S")) + ' || ' +
                                      self.host + ' || ' + webpage + ' || 404\n')
            else:
                if webpage.split('.')[-1] != "ico":
                    response = 'HTTP/1.0 403 FORBIDDEN\n\nForbidden Error!'
                    with lock:
                        with open('log/log.txt', 'a+') as log:
                            log.write(str(datetime.now().strftime("%d/%m/%Y %H:%M:%S")) + ' || ' +
                                      self.host + ' || ' + webpage + ' || 403\n')
            if "Content-type: image/jpg" in response:
                self.conn.sendall(response.encode()+content)
            else:
                self.conn.sendall(response.encode())
        self.conn.close()

SERVER_HOST = 'localhost'
SERVER_PORT = 8080
DATA_SIZE = 8192
DEFAULT_FOLDER = 'pages'
FILES = ['html', 'js', 'png', 'jpg', 'jpeg']

sock = socket()
sock.bind((SERVER_HOST, SERVER_PORT))
sock.listen(3)
lock = Lock()

clients = []
while True:
    try:
        conn, addr = sock.accept()
        clients.append(Client(addr, conn))
        clients[-1].start()

        for cl in clients:
            if not cl.is_alive():
                clients.remove(cl)
    except:
        break

sock.close()