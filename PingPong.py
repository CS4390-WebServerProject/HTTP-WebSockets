#!/usr/bin/python
from __future__ import unicode_literals
from PingPong.HTTPDate import HTTPDate
from PingPong.Header import RequestHeader, ResponseHeader
from PingPong.PingConf import PingConf
import sys, os, threading, io, gzip, time, socket, select


def gzipCompress(str):
    out = io.io()
    with gzip.GzipFile(fileobj=out, mode='w') as f:
        f.write(str)

    return out.getvalue()

# Thread
def handler(clientSock, addr, config):
    # Flag to indicate that the connection is opened
    connectionOpen = True

    # We will default to HTTP/1.1 unless otherwise by client
    httpVer = 'HTTP/1.1'
    message = ''

    # Timeout of when to close the connection when there appears to be no data left
    # We set it to 30s
    timeout = 15

    hasMessage = False

    clientSock.setblocking(0)

    ready = select.select([clientSock], [], [], timeout)

    # Persistent Connection
    while connectionOpen:
        headReq = False
        notFound = False

        ready = select.select([clientSock], [], [], timeout)

        # HTTP Request message should be no more than 1MB
        try:
            message = clientSock.recv(1024).decode('unicode_escape')
            hasMessage = True
        except socket.error:
            hasMessage = False

        # Organize request messages
        if ready[0] and message != '':
            print(u"REQUEST:\n" + message)
            request = RequestHeader(message)
            httpVer = request.httpVer

            # Don't send the body
            if request.reqType == 'HEAD':
                headReq = True
            
            try:
                # Get requested file
                f = open(request.reqLocation)
                body = f.read()
            except IOError:
                print("There was an error...")
                notFound = True
                f = open('404.html')
                body = f.read()

            f.close()
        
            print('Sending response...')
            if notFound:
                # Write 404 Message
                response = ResponseHeader(httpVer, 404, 'Not Found')
                response.addMessage('Date', HTTPDate())
                response.addMessage('Server', 'PingPongServer')
                response.addMessage('Content-Length', str(len(body)))
            else:
                response = ResponseHeader(httpVer, 200, 'OK')
                response.addMessage('Date', HTTPDate())
                response.addMessage('Server', 'PingPongServer')

                if request.message['Connection'] == 'keep-alive':
                    response.addMessage('Connection', 'keep-alive')

                # Check if client supports gzip encoding
                if request.canAcceptEncoding('gzip') and config.conf['gzip'] == 'on':
                    body = gzipCompress(body)
                    response.addMessage('Content-Encoding', 'gzip')

                response.addMessage('Content-Length', len(body))
                response.addMessage('Content-Type', request.message['Content-Type'] + '; charset=UTF-8')

            print(u"RESPONSE:\n" + response.generateMessage())

            if headReq:
                clientSock.sendall(response.generateMessage())
            else:
                totalResponse = response.generateMessage() + body
                clientSock.sendall(totalResponse.encode('utf-8'))
                
            if 'Connection' in request.message:
                if request.message['Connection'] == 'close':
                    print("Connection is closing.")
                    connectionOpen = False

        else:
            print("No more requests. Closing.")
            connectionOpen = False


    clientSock.close();


def init(port):
    try:
        config = PingConf("pingpong.conf")
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverSocket.bind(('', port))
        serverSocket.listen(2);
        threads = []
        startServer = True
        
        while startServer:
            # We are looking for any interrupts
            try:
                print('Ready to serve...')
                clientSock, addr = serverSocket.accept()
                t = threading.Thread(target=handler, args=(clientSock, addr, config))
                threads.append(t)
                t.start()
                
            except KeyboardInterrupt:
                # Ending the server
                print('Server is now closing...')
                startServer = False
                # Close any existing client connections
                for t in threads:
                    t.join()
        
        # Close server 
        serverSocket.close()
    except SyntaxError as err:
        print(err)
    except socket.error as err:
        print(err)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        init(int(sys.argv[1]))
    else:
        init(80)
