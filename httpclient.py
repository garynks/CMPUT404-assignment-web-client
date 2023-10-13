#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
import ssl
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_port(self, url):
        parsed_url = urllib.parse.urlparse(url)
        hostname = parsed_url.hostname
        port = parsed_url.port

        if not port:
            scheme = parsed_url.scheme
            if scheme == "http":
                port = 80
            elif scheme == "https":
                port = 443

        return hostname, port
    
    def get_path(self, url):
        parsed_url = urllib.parse.urlparse(url)
        path = parsed_url.path

        if not path:
            path = '/'

        return path

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # if HTTPs, create a socket for SSL/TLS communication
        if port == 443:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            context.load_default_certs() # required for certificate verification
            self.socket = context.wrap_socket(self.socket, server_hostname=host)

        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        code = int(data.split(' ')[1])
        return code

    def get_headers(self, data):
        headers = {}
        response_lines = data.split('\r\n')
        for line in response_lines:
            key_value = line.split(":", 1)

            # If it's a key-value pair, then it's a header
            if (len(key_value) == 2):
                headers[key_value[0]] = key_value[1].strip()
        
        return headers


    def get_body(self, data):
        body = re.search(r"\r\n\r\n(.*)", data, re.DOTALL)
        
        if body:
            body = body.group(1) # return everything after \r\n\r\n
            return body
        
        return None
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        # switched utf-8 to latin-1 because some websites
        # return a termination byte that doesn't decode properly in utf-8
        # e.g www.google.com
        return buffer.decode('latin-1')

    def GET(self, url, args=None):
        host, port = self.get_host_port(url)
        path = self.get_path(url)
        self.connect(host, port)

        request = self.build_request("GET", host, path)

        self.sendall(request)
        response = self.recvall(self.socket)
        self.socket.close()

        print(response)

        response_code = self.get_code(response)
        response_body = self.get_body(response)

        # If a 3xx response code is returned, redirect to the new location
        if 300 <= response_code < 400:
            response_headers = self.get_headers(response)
            location = response_headers["Location"]
            self.GET(location)
        
        return HTTPResponse(response_code, response_body)

    def POST(self, url, args=None):
        host, port = self.get_host_port(url)
        path = self.get_path(url)
        self.connect(host, port)

        request = self.build_request("POST", host, path, args)
        self.sendall(request)
        response = self.recvall(self.socket)
        self.socket.close()

        print(response)

        response_code = self.get_code(response)
        response_body = self.get_body(response)
        return HTTPResponse(response_code, response_body)
    
    def build_request(self, request_method, host, path, args=None):
        request_headers = \
                f"{request_method} {path} HTTP/1.1\r\n" + \
                f"Host: {host}\r\n" + \
                "Connection: close\r\n"
        request_body = ""

        if request_method == "POST":
            if args:
                request_body = '&'.join([f'{key}={value}' for key, value in args.items()])
                
                # Additional headers
                request_headers += "Content-type: application/x-www-form-urlencoded\r\n"
            
            # Always include a Content Length with the POST 
            # This is needed if we are POSTing headers without a request body
            request_headers += f"Content-length: {len(request_body.encode('utf-8'))}\r\n"
             
        return request_headers + "\r\n" + request_body

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
