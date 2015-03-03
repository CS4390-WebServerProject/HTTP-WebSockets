#!/usr/bin/python

from PingHeaders import Date
from PingHeaders.Header import RequestHeader, ResponseHeade
from socket import *
import sys, os

def recvAll(s):
    buffer = []
    while True:
        data = s.recv(1024)
        while data:
            buffer.append(data)
        print(''.join(buffer))
    
    return ''.join(buffer)
    

def init(port):
    serverSocket = socket(AF_INET, SOCK_STREAM)
    
    serverSocket.bind(('', port))
    
    serverSocket.listen(11);
    
    while True:
        print 'Ready to serve...'
        connectionSocket, addr = serverSocket.accept();
        
        while True:
            try:
                message = connectionSocket.recv(1024)
                reqHeader = RequestHeader(message)
                
                f = open(reqHeader.reqLocation)
                output = f.read();
                
                connectionSocket.sendall("HTTP/1.1 200 OK\r\n\r\n")
                connectionSocket.sendall(output)
                
            except IOError:
                print("There was an error...")
            

if __name__ == '__main__':
    init(int(sys.argv[1]))