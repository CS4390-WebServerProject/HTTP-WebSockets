#!/usr/bin/python
from PingPong.HTTPDate import HTTPDate
from PingPong.Header import RequestHeader, ResponseHeader
from PingPong.PingConf import PingConf
import sys, os, thread, StringIO, gzip, time, socket, select


def gzipCompress(str):
    out = StringIO.StringIO()
    with gzip.GzipFile(fileobj=out, mode='w') as f:
        f.write(str)

    return out.getvalue()

# Thread
def handler(clientSock, addr, config):
    # Flag to indicate that the connection is opened
    connectionOpen = True

    # We will default to HTTP/1.1 unless otherwise by client
    httpVer = 'HTTP/1.1'

    # Timeout of when to close the connection when there appears to be no data left
    # We set it to 30s
    timeout = 5

    clientSock.setblocking(0)

    ready = select.select([clientSock], [], [], timeout)

    # Persistent Connection
    while connectionOpen:
        headReq = False
        notFound = False
        hasMessage = False

        ready = select.select([clientSock], [], [], timeout)

        # HTTP Request message should be no more than 1MB
        try:
            message = clientSock.recv(1024)
            hasMessage = True
        except socket.error:
            hasMessage = False

        # Organize request messages
        if ready[0]:
            print("REQUEST:\n" + message)
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

                # Check if client supports gzip encoding
                if request.canAcceptEncoding('gzip') and config.conf['gzip'] == 'on':
                    body = gzipCompress(body)
                    response.addMessage('Content-Encoding', 'gzip')

                response.addMessage('Content-Length', len(body))
                response.addMessage('Content-Type', request.message['Content-Type'] + '; charset=UTF-8')

            print("RESPONSE:\n" + response.generateMessage())

            if headReq:
                clientSock.sendall(response.generateMessage())
            else:
                clientSock.sendall(response.generateMessage() + body)
                
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
        
        while True:
            # We are looking for any interrupts
            try:
                print('Ready to serve...')
                clientSock, addr = serverSocket.accept()
                thread.start_new_thread(handler, (clientSock, addr, config))
                
            except KeyboardInterrupt:
                # Ending the server
                print('Server is now closing...')
                break
        
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
