#!/usr/bin/python

from PingHeaders.HTTPDate import HTTPDate
from PingHeaders.Header import RequestHeader, ResponseHeader
from socket import *
import sys, os, thread

def handler(clientSock, addr):
    # Flag to indicate that the connection is opened
    connectionOpen = True
    httpVer = 'HTTP/1.1'

    # Persistent Connection
    while connectionOpen:
        try:
            print('Waiting for request...')
            message = clientSock.recv(1024)
            
            # Organize request messages
            if message != '':
                print("REQUEST:\n" + message)
                request = RequestHeader(message)
                httpVer = request.httpVer
                
                # Get requested file
                f = open(request.reqLocation)
                body = f.read()
                f.close()
                
                print('Sending response...')
                
                response = ResponseHeader(httpVer, 200, 'OK')
                response.addMessage('Date', HTTPDate())
                response.addMessage('Server', 'PingPongServer')
                response.addMessage('Content-Length', len(body))
                response.addMessage('Content-Type', request.message['Content-Type'])
                print('RESPONSE:\n' + response.generateMessage())
                clientSock.sendall(response.generateMessage() + body)
                
                if request.message['Connection'] == 'close':
                    print("Connection is closed")
                    connectionOpen = False
            else:
                connectionOpen = False

            
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
            
            clientSock.sendall(response.generateMessage() + body)

    clientSock.close();


def init(port):
    serverSocket = socket(AF_INET, SOCK_STREAM)
    
    serverSocket.bind(('', port))
    
    serverSocket.listen(2);
    
    while True:
        
        # We are looking for any interrupts
        try:
            print('Ready to serve...')
            clientSock, addr = serverSocket.accept()
            thread.start_new_thread(handler, (clientSock, addr))
            
        except KeyboardInterrupt:
            # Ending the server
            print('Server is now closing...')
            break
    
    # Close server 
    serverSocket.close()
            

if __name__ == '__main__':
    if len(sys.argv) > 1:
        init(int(sys.argv[1]))
    else:
        init(80)
