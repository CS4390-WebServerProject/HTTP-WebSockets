#!/usr/bin/python
from __future__ import unicode_literals
from PingPong.HTTPDate import HTTPDate
from PingPong.Header import RequestHeader, ResponseHeader
from PingPong.ETag import ETag
from PingPong.PingConf import PingConf
from stat import *
import sys, os, threading, gzip, time, socket, select, io, hashlib, binascii

def gzipCompress(str):
    out = io.BytesIO()
    with gzip.GzipFile(fileobj=out, mode='wb') as f:
        f.write(str.encode('utf-8'))

    return out.getvalue()

# Thread
def handler(clientSock, addr, config, etag):
    # Flag to indicate that the connection is opened
    connectionOpen = True

    # We will default to HTTP/1.1 unless otherwise by client
    httpVer = 'HTTP/1.1'
    message = ''

    # Timeout of when to close the connection when there appears to be no data left
    # We set it to 15s
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

            # Make sure host exists within PingPong configuration
            if config.hasHost(request.message['Host'][0]):
                host = request.message['Host'][0]
                filepath = config.getConfig(host, 'rootdir') + request.reqLocation
                hasModified = True
                cachingEnabled = config.getConfig(host, 'caching') == 'on'

                # Check if browser allows cache
                if 'Cache-Control' in request.message:
                    if request.message['Cache-Control'][0] == 'no-cache':
                        cachingEnabled = False

                try:
                    # Get requested file with regard to root directory for host
                    f = open(filepath)
                    body = f.read()
                except IOError:
                    print("There was an error...")
                    notFound = True
                    filepath = '404.html'
                    f = open(filepath)
                    body = f.read()

                f.close()

                # Check if caching is enabled on server
                if cachingEnabled and 'If-None-Match' in request.message:
                    hasModified = etag.hasModified(filepath, request.message['If-None-Match'][0])

                # Determine HTTP Response
                if notFound:
                    response = ResponseHeader(httpVer, 404, 'Not Found')
                elif cachingEnabled and not hasModified:
                    response = ResponseHeader(httpVer, 304, 'Not Modified')
                else:
                    response = ResponseHeader(httpVer, 200, 'OK')

                response.addMessage('Date', HTTPDate())
                response.addMessage('Server', 'PingPong Server')
                response.addMessage('Content-Type', request.message['Content-Type'] + '; charset=UTF-8')

                # Generate new ETag if requested resource is newer than caching
                if cachingEnabled and hasModified:
                    response.addMessage('ETag', etag.generateETag(filepath))

                if hasModified:
                    # Check if client supports gzip encoding
                    if request.canAcceptEncoding('gzip') and config.getConfig(host, 'gzip') == 'on':
                        body = gzipCompress(body)
                        response.addMessage('Content-Encoding', 'gzip')
                    else:
                        body = body.encode('utf-8')
                else:
                    body = ""

                response.addMessage('Content-Length', str(len(body)))

                if 'keep-alive' in request.message['Connection']:
                    response.addMessage('Connection', 'keep-alive')

                print(u"RESPONSE:\n" + response.generateMessage())

                # HEAD
                if headReq or not hasModified:
                    clientSock.sendall(response.generateMessage().encode('utf-8'))
                else: # GET
                    totalResponse = response.generateMessage().encode('utf-8') + body
                    clientSock.sendall(totalResponse)

                # Client requests to close the connection
                if 'Connection' in request.message:
                    if 'close' in request.message['Connection']:
                        print("Connection is closing.")
                        connectionOpen = False

            else: # Host does not match
                # Host does not exist within PingPong configuration
                # Send 400 Bad Request
                body = """<!doctype>
                        <html>
                        <head><title>Ping Pong | Bad Request</title></head>
                        <body><h1>Requested hostname is invalid.</h1></body>
                        </html>"""
                response = ResponseHeader(httpVer, 400, 'Request')
                response.addMessage('Server', 'PingPong')
                response.addMessage('Date', HTTPDate())
                response.addMessage('Content-Length', len(body))
                response.addMessage('Content-Type', request.message['Content-Type'] + '; charset=UTF-8')
                totalResponse = response.generateMessage() + body
                clientSock.sendall(totalResponse.encode('utf-8'))
                connectionOpen = False
        else:
            print("No more requests. Closing.")
            connectionOpen = False


    clientSock.close();


def init(port):
    try:
        config = PingConf("pingpong.ini")
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverSocket.bind(('', port))
        serverSocket.listen(2);
        threads = []
        startServer = True
        etag = ETag()

        while startServer:
            # We are looking for any interrupts
            try:
                print('Ready to serve...')
                clientSock, addr = serverSocket.accept()
                t = threading.Thread(target=handler, args=(clientSock, addr, config, etag,))
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
