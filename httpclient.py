#!/usr/bin/env python
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust, Omar Almokdad
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
import urllib

# show correct way to use the program
def help():
    print "httpclient.py [GET/POST] [URL]\n"

# Class for the return of the response
class HTTPResponse(object):

    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

# Class to act as client
class HTTPClient(object):

    # connect to the specified host at the specified port (default to 80)
    def connect(self, host, port=80):
        # use sockets!
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))

        return s

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            print part
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer)

    # get the code of the reply (second word of the reply)
    def get_code(self, data):
        return int(data.split(" ")[1])

    # get the headers and body of the reply
    def get_headers_and_body(self, data):
        dataList = data.split("\n")
        body = ""
        headers = ""
        dataList.pop(0)
        # save the headers line by line
        while(dataList[0] != '\r'):
            headers = headers + dataList.pop(0) + "\n"
        dataList.pop(0)
        # save the body line by line
        while(dataList):
            body = body + dataList.pop(0) + "\n"
        return headers, body

    # send a GET request, and process the reply
    def GET(self, url, args=None):
        command = url.split("/")
        # if "http://" is part of the request
        if command[0] == "http:":
            command.pop(0)
            command.pop(0)

        # get the host and the port
        hostAndPort = command.pop(0)
        hostPortList = hostAndPort.split(":")
        host = hostPortList[0]
        if len(hostPortList) == 2:
            port = int(hostPortList[1])
        else:
            port = 80

        # connect to host
        s = self.connect(host, port)

        # construct the message to send
        content = "/".join(command)
        message = "GET /" + content + " HTTP/1.1\r\nHost: " + host + "\r\n\r\n"

        # send and process return
        s.send(message)
        data = self.recvall(s)
        code = self.get_code(data)
        headers, body = self.get_headers_and_body(data)
        print data
        return HTTPResponse(code, body)

    # send a post request, and process the reply
    def POST(self, url, args=None):
        command = url.split("/")
        # if "http://" is part of the request
        if command[0] == "http:":
            command.pop(0)
            command.pop(0)

        # get the host and the port
        hostAndPort = command.pop(0)
        hostPortList = hostAndPort.split(":")
        host = hostPortList[0]
        if len(hostPortList) == 2:
            port = int(hostPortList[1])
        else:
            port = 80

        # connect to host
        s = self.connect(host, port)

        # construct the message to send
        content = "/".join(command)
        message = "POST /" + content + " HTTP/1.1\r\nHost: " + host + "\r\n"

        message = message + "Content-type: application/x-www-form-urlencoded\r\n"
        if args:
            query = urllib.urlencode(args)
            message = message + "Content-length: " + \
                str(len(query)) + "\r\n\r\n"
            message = message + query
        else:
            message = message + "Content-length: 0\r\n\r\n"

        # send and process return
        s.send(message)
        data = self.recvall(s)
        code = self.get_code(data)
        headers, body = self.get_headers_and_body(data)
        return HTTPResponse(code, body)

    # sort GET from POST
    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST(url, args)
        else:
            return self.GET(url, args)

# main program logic
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        client.command(sys.argv[2], sys.argv[1])
    else:
        client.command(sys.argv[1])
