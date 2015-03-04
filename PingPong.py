#!/usr/bin/python

from PingHeaders.HTTPDate import HTTPDate
from PingHeaders.Header import RequestHeader, ResponseHeader
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
        connectionSocket, addr = serverSocket.accept()
        
        # Flag to indicate that the connection is opened
        connectionOpen = True
        
        while connectionOpen:
            httpVer = 'HTTP/1.1'
            try:
                message = connectionSocket.recv(1024)
                
                # Organize request messages
                request = RequestHeader(message)
                print(message)
                httpVer = request.httpVer
                
                # Get requested file
                f = open(request.reqLocation)
                body = f.read()
                f.close()
                
                response = ResponseHeader(request.httpVer, 200, 'OK')
                response.addMessage('Date', HTTPDate())
                response.addMessage('Server', 'PingPongServer')
                response.addMessage('Content-Length', str(len(body)))
                print('RESPONSE:\n' + response.generateMessage())
                connectionSocket.sendall(response.generateMessage())
                connectionSocket.sendall(body + '\r\n')
                
                if request.message['Connection'] == 'close':
                    connectionOpen = false
                
            except IOError:
                print("There was an error...")
                
                f = open('404.html')
                body = f.read()
                f.close()
                
                # Write 404 Message
                response = ResponseHeader(httpVer, 404, 'Not Found')
                response.addMessage('Date', HTTPDate())
                response.addMessage('Server', 'PingPongServer')
                response.addMessage('Content-Length', str(len(body)))
                print("RESPONSE:\n" + response.generateMessage())
                
                connectionSocket.sendall(response.generateMessage())
                connectionSocket.sendall(body)
            
        connectionSocket.close()
    
    # Close server 
    serverSocket.close()
            

if __name__ == '__main__':
    if len(sys.argv) > 1:
        init(int(sys.argv[1]))
    else:
        init(80)