import os
import sys
import datetime
import re
from socket import socket


# Class to manage response
class Res:
    conn: socket
    regex_html = re.compile(r"html")
    regex_image = re.compile(r"gif|jpe?g|bmp|png")
    regex_css = re.compile(r"css")
    regex_js = re.compile(r"js")
    regex_json = re.compile(r"json")
    regex_xml = re.compile(r"xml")
    http_ver = "HTTP/1.0"
    headers = f"{http_ver} 200 OK\nServer: LRSS/1.0.0\n"

    def __init__(self, conn: socket, ver = "HTTP/1.0", keep_alive = False):
        self.conn = conn
        self.http_ver = ver
        self.keep_alive = keep_alive
        print(f"New connection from {conn.getpeername()}, version: {self.http_ver}, keep alive: {self.keep_alive}")

    def send(self, file):
        if os.path.exists(file):
            self.headers += f"Date: {datetime.datetime.now()}\n"
            is_html = re.findall(self.regex_html, file)
            if is_html:
                self.headers += f"Content-type: text/html\n"
            else:
                if re.findall(self.regex_image, file):
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

            self.headers += f"Content-length: {os.path.getsize(file)}\nConnection: {'keep-alive' if self.keep_alive else 'close'}\n\n"
            self.conn.sendall(bytes(self.headers, "utf-8"))
            self.conn.sendall(bytes(open(file, "rb").read()))
        else:
            self.not_found()
        return

    def not_found(self):
        body = "<html><body>404 Not Found</body></html>"
        headers = f"{self.http_ver} 404 Not Found\nDate: {datetime.datetime.now()}\nServer: LRSS/1.0.0\nContent-type: text/html\nContent-length: {sys.getsizeof(body)}\nConnection: close\n\n"
        self.conn.sendall(bytes(headers + body, "utf-8"))
        return

    def test(self):
        body = "<html><body>Hello World</body></html>"
        headers = f"{self.http_ver} 200 OK\nDate: {datetime.datetime.now()}\nServer: LRSS/1.0.0\nContent-type: text/html\nContent-length: {sys.getsizeof(body)}\nConnection: close\n\n"
        self.conn.sendall(bytes(headers + body, "utf-8"))
        return
