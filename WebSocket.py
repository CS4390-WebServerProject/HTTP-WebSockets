import struct
import sys
import socket
import threading
import select
from PingPong.Header import RequestHeader, ResponseHeader
from base64 import b64encode
from hashlib import sha1
from StringIO import StringIO

class PingPongWebSocket:

    def __init__(self, hostname, uri, port=None):
        if port is None:
            port = 80

        self.hostname = hostname
        self.uri = uri
        self.port = port
        self.threads = []
        self.startServer = True
        self.clients = []
        self.messages = []
        self.indexOffset = 0
        self.lock = threading.Lock()

        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.bind(('', port))


    def start(self):
        # Create socket
        self.serverSocket.listen(4)

        while self.startServer:
            try:
                print("Ready to serve websocket.")
                clientSock, addr = self.serverSocket.accept()

                # List is thread-safe
                self.clients.append(clientSock)

                t = threading.Thread(target=self.handler, args=(clientSock, len(self.clients),))
                self.threads.append(t)
                t.start()
            except KeyboardInterrupt:
                self.startServer = False

        # Close any existing client connections
        for t in self.threads:
            t.join()

        self.serverSocket.close()

    def parseFrame(self, frame):
        buff = StringIO(frame)

        shortStruct = struct.Struct('H')
        longStruct = struct.Struct('Q')
        intStruct = struct.Struct('I')
        charStruct = struct.Struct('c')

        # First byte (fin and opcode)
        finOp = ord(buff.read(1))
        finBit = (finOp & 128) >> 7
        opCode = finOp & 0x0f


        if opCode == 0x8:
            buff.close()
            return None
        else:
            # Second byte (mask and payload)
            maskPayload = ord(buff.read(1))
            maskBit = (maskPayload & 254) >> 7
            payload = maskPayload & 127

            if maskBit != 1:
                raise ValueError('Mask bit is not set when it should be from clients.')

            extendedPayload = 0

            if payload == 126:
                extendedPayload = shortStruct.unpack(buff.read(2))
            elif payload == 127:
                extendedPayload = longStruct.unpack(buff.read(8))

            payload = extendedPayload + payload

            maskingKey = buff.read(4)

            # Get encoded text
            encodedText = buff.read(payload)
            decodedTextIO = StringIO()

            for i in range(0, payload):
                decodedTextIO.write(chr(ord(encodedText[i]) ^ ord(maskingKey[i % 4])))

            decodedText = decodedTextIO.getvalue()

            buff.close()
            decodedTextIO.close()

            return decodedText

    def makeFrame(self, text, fin=None):
        buff = StringIO()

        if fin == None:
            fin = True
            finBit = 1 << 7
        else:
            fin = False
            finBit = 0

        opcode = 0x1 if fin else 0x0

        # 8 bit
        s = struct.Struct('>c')

        # 16 bit
        eP = struct.Struct('>2s')

        # 64 bit
        eE = struct.Struct('>8s')

        buff.write(s.pack(chr(finBit + opcode)))

        if len(text) <= 125 and len(text) >= 0:
            buff.write(s.pack(chr(len(text))))
        # text can fit within a 16 bit unsigned int
        elif len(text) > 125 and len(text) <= 0xff:
            buff.write(s.pack(chr(126)))
            buff.write(eP.pack(len(text)))
        elif len(text) > 125 and len(text) <= 0xffffffff:
            buff.write(s.pack(chr(127)))
            buff.write(eE.pack(len(text)))

        buff.write(text)

        resStr = buff.getvalue()

        buff.close()

        return resStr

    def handler(self, clientSock, index):
        running = True
        gotHandshake = False
        message = ''
        timeout = 5
        indexOffset = self.indexOffset
        clientSock.setblocking(0)

        ready = select.select([clientSock], [], [], timeout)

        while running and self.startServer:
            try:
                ready = select.select([clientSock], [], [], timeout)
                strStruct = struct.Struct('1024s')

                try:
                    message = clientSock.recv(1024).decode('unicode_escape')
                    print("Message: " + message)
                except socket.error:
                    message = ''

                if ready[0] and message != '':
                    # Initial step: handshake
                    if not gotHandshake:
                        request = RequestHeader(message)

                        print("Request URL:" + request.reqLocation)
                        print("Request Hostname: " + request.message['Host'])

                        if request.reqLocation == self.uri:
                            hostname = self.hostname + ':' + str(self.port)

                            if request.message['Host'] == hostname:
                                if request.message['Upgrade'] == 'websocket' and request.message['Connection'] == 'Upgrade':
                                    webSocketKey = request.message['Sec-WebSocket-Key']
                                    webSocketVer = request.message['Sec-WebSocket-Version']

                                    print("Web Socket Key: " + webSocketKey)
                                    print("Web Socket Ver: " + webSocketVer)

                                    # Build magic
                                    magic = webSocketKey + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
                                    accept = b64encode(sha1(magic.encode('utf-8')).digest())

                                    response = ResponseHeader(request.httpVer, 101, "Switching Protocols")
                                    response.addMessage("Upgrade", "websocket")
                                    response.addMessage("Connection", "Upgrade")
                                    response.addMessage("Sec-WebSocket-Accept", accept.decode('utf-8'))

                                    clientSock.sendall(response.generateMessage().encode('utf-8'))

                                    gotHandshake = True
                            else:
                                running = False
                        else:
                            running = False
                    else:
                        print("Got message!")
                        text = self.parseFrame(message)
                        
                        if text != None:
                            for sock in self.clients:
                                sock.sendall(self.makeFrame(text))
                        else:
                            running = False

            except KeyboardInterrupt:
                running = False

        clientSock.close();

        self.lock.acquire()
        try:
            # Remove socket from client list
            self.clients.pop(index - self.indexOffset - 1)
            self.indexOffset = self.indexOffset - 1
        finally:
            self.lock.release()


if __name__ == '__main__':
    websocket = PingPongWebSocket(sys.argv[1], sys.argv[2], int(sys.argv[3]))
    websocket.start()
