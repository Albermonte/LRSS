# utils/res.py

import os
import sys
import datetime
import re
from socket import socket


# Class to manage response
class Res:
    conn: socket
    # All regex to check file type
    regex_html = re.compile(r"html")
    regex_image = re.compile(r"gif|jpe?g|bmp|png")
    regex_css = re.compile(r"css")
    regex_js = re.compile(r"js")
    regex_json = re.compile(r"json")
    regex_xml = re.compile(r"xml")
    http_ver = "HTTP/1.0"
    headers = f"{http_ver} 200 OK\nServer: LRSS/1.0.0\n"

    def __init__(self, conn: socket, ver="HTTP/1.0", keep_alive=False):
        self.conn = conn
        self.http_ver = ver
        self.keep_alive = keep_alive
        print(
            f"New connection from {conn.getpeername()}, version: {self.http_ver}, keep alive: {self.keep_alive}")

    def send(self, file, head_only=False):
        # Check if file exists
        if os.path.exists(file):
            self.headers += f"Date: {datetime.datetime.now()}\n"
            # Check file type
            if re.findall(self.regex_html, file):
                self.headers += f"Content-type: text/html\n"
            elif re.findall(self.regex_image, file):
                type = re.findall(self.regex_image, file)[0]
                self.headers += f"Content-type: image/{type}\n"
            elif re.findall(self.regex_css, file):
                self.headers += f"Content-type: text/css\n"
            elif re.findall(self.regex_js, file):
                self.headers += f"Content-type: text/javascript\n"
            elif re.findall(self.regex_json, file):
                self.headers += f"Content-type: application/json\n"
            elif re.findall(self.regex_xml, file):
                self.headers += f"Content-type: application/xml\n"
            else:
                self.headers += f"Content-type: application/octet-stream\n"

            # Set lenght header
            # Set connection header, important for keep-alive
            self.headers += f"Content-length: {os.path.getsize(file)}\nConnection: {'keep-alive' if self.keep_alive else 'close'}\n\n"
            self.conn.sendall(bytes(self.headers, "utf-8"))
            # If request method is HEAD, don't send body
            if not head_only:
                self.conn.sendall(bytes(open(file, "rb").read()))
        else:
            return self.not_found()
        return 0

    def not_found(self):
        # Send 404 error
        body = "<html><body>404 Not Found</body></html>"
        headers = f"{self.http_ver} 404 Not Found\nDate: {datetime.datetime.now()}\nServer: LRSS/1.0.0\nContent-type: text/html\nContent-length: {sys.getsizeof(body)}\nConnection: close\n\n"
        self.conn.sendall(bytes(headers + body, "utf-8"))
        return -1

    # Test method in case it's needed
    def test(self):
        body = "<html><body>Hello World</body></html>"
        headers = f"{self.http_ver} 200 OK\nDate: {datetime.datetime.now()}\nServer: LRSS/1.0.0\nContent-type: text/html\nContent-length: {sys.getsizeof(body)}\nConnection: close\n\n"
        self.conn.sendall(bytes(headers + body, "utf-8"))
        return 0
