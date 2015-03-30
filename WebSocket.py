import struct
import sys
import socket
import threading
import select
import time
import binascii
from PingPong.Header import RequestHeader, ResponseHeader
from base64 import b64encode
from hashlib import sha1
try:
    from StringIO import StringIO, BytesIO
except ImportError:
    from io import StringIO, BytesIO

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
        buff = BytesIO(frame)

        # Char
        cCharStruct = struct.Struct('!c')

        # 16 bit
        shortStruct = struct.Struct('!H')

        # 64 bit
        longStruct = struct.Struct('!Q')

        # 32 bit
        intStruct = struct.Struct('!I')

        # 8 bit
        charStruct = struct.Struct('!B')

        # First byte (fin and opCode)
        finOp = ord(buff.read(1))

        finBit = (finOp & 128) >> 7
        opCode = finOp & 0x0f

        if opCode == 0x8:
            buff.close()
            return None
        elif opCode == 0xA:
            # Pong reply
            return [opCode, True]
        else:
            # Second byte (mask and payload)
            maskPayload = ord(buff.read(1))
            maskBit = (maskPayload & 254) >> 7
            payload = maskPayload & 127

            if maskBit != 1:
                raise ValueError('Mask bit is not set when it should be from clients.')

            extendedPayload = 0

            if payload == 126:
                extendedPayload = shortStruct.unpack(buff.read(2))[0]
            elif payload == 127:
                extendedPayload = longStruct.unpack(buff.read(8))[0]

            payload = extendedPayload + payload

            maskingKey = buff.read(4)

            # Get encoded text
            encodedText = buff.read(payload)
            decodedTextIO = BytesIO()

            for i in range(0, payload):
                if sys.version_info > (3, 0):
                    decodedTextIO.write(chr(encodedText[i] ^ maskingKey[i % 4]))
                else:
                    decodedTextIO.write(chr(ord(encodedText[i]) ^ ord(maskingKey[i % 4])))


            decodedText = decodedTextIO.getvalue()

            buff.close()
            decodedTextIO.close()

            return [opCode, decodedText]


    def hasOpcode(self, frame, opCode):
        if sys.version_info > (3, 0):
            finOp = frame[0]
        else:
            finOp = ord(frame[0])

        finBit = (finOp & 128) >> 7
        opCodeFrame = finOp & 0x0f

        return opCode == opCodeFrame

    def sendPing(self, clientSock):
        pingFrame = self.makeFrame("Are you there?", 0x9);
        clientSock.sendall(pingFrame);

    def makeFrame(self, text, opCode=None, finArg=None):
        buff = BytesIO()

        fin = True if (finArg == None or finArg == True) else False
        finBit = (1 << 7) if fin else 0

        if opCode == None:
            opCode = 0x1 if fin else 0x0

        # 8 bit
        s = struct.Struct('>B')

        # 16 bit
        eP = struct.Struct('>2s')

        # 64 bit
        eE = struct.Struct('>8s')

        buff.write(s.pack(finBit + opCode))

        if len(text) <= 125 and len(text) >= 0:
            buff.write(s.pack(len(text)))
            print(buff.getvalue())
        # text can fit within a 16 bit unsigned int
        elif len(text) > 125 and len(text) <= 0xff:
            buff.write(chr(126))
            buff.write(eP.pack(len(text)))
        elif len(text) > 125 and len(text) <= 0xffffffff:
            buff.write(chr(127))
            buff.write(eE.pack(chr(len(text))))

        #buff.write(text.encode('utf-8'))
        for ch in text:
            buff.write(ch.encode('utf-8'))

        resStr = buff.getvalue()

        buff.close()

        return resStr

    def handler(self, clientSock, index):
        running = True
        gotHandshake = False
        message = ''
        timeout = 5
        startPing = time.time() * 1000  # In milliseconds
        endPing = time.time() * 1000
        noPongCount = 0
        msPingDelay = 5000
        waitingForPong = False

        indexOffset = self.indexOffset
        clientSock.setblocking(0)

        ready = select.select([clientSock], [], [], timeout)

        while running and self.startServer:
            # Update IO
            ready = select.select([clientSock], [], [], timeout)
            # Update time
            endPing = time.time() * 1000

            # Ping client every [msPingDelay] ms after handshake
            if gotHandshake and endPing - startPing >= msPingDelay:
                if not waitingForPong:
                    self.sendPing(clientSock)
                    waitingForPong = True
                elif noPongCount < 3:
                    # No pong reply recieved
                    noPongCount += 1
                else:
                    # Client is not responding. Disconnected
                    running = False

            try:
                message = clientSock.recv(1024)
            except socket.error:
                message = ''

            if ready[0] and len(message) > 0:
                # Initial step: handshake
                if not gotHandshake:
                    request = RequestHeader(message.decode('utf-8'))

                    print("Request URL:" + request.reqLocation)
                    print("Request Hostname: " + request.message['Host'][0])

                    if request.reqLocation == self.uri:
                        hostname = self.hostname + ':' + str(self.port)

                        if request.message['Host'][0] == hostname:
                            print(request.message['Upgrade'])
                            print(request.message['Connection'])
                            if 'websocket' in request.message['Upgrade']  and 'Upgrade' in request.message['Connection']:
                                webSocketKey = request.message['Sec-WebSocket-Key'][0]
                                webSocketVer = request.message['Sec-WebSocket-Version'][0]

                                print("Web Socket Key: " + webSocketKey)
                                print("Web Socket Ver: " + webSocketVer)

                                # Build magic
                                magic = webSocketKey + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
                                accept = b64encode(sha1(magic.encode('utf-8')).digest())

                                response = ResponseHeader(request.httpVer, 101, "Switching Protocols")
                                response.addMessage("Upgrade", "websocket")
                                response.addMessage("Connection", "Upgrade")
                                response.addMessage("Sec-WebSocket-Accept", accept.decode('utf-8'))

                                print(response.generateMessage())
                                print(len(response.generateMessage()))

                                clientSock.sendall(response.generateMessage().encode('utf-8'))

                                gotHandshake = True
                        else:
                            running = False
                    else:
                        running = False
                else:
                    if self.hasOpcode(message, 0x1):
                        print("Got message!")
                        text = self.parseFrame(message)
                        if text != None:
                            for sock in self.clients:
                                if text[0] == 0x1:
                                    messageBack = self.makeFrame(text[1])
                                    if sock.sendall(messageBack) != None:
                                        print("Uh oh! Error sending!")
                        else:
                            running = False
                    elif self.hasOpcode(message, 0xA):
                        # Pong
                        waitingForPong = False
                        noPongCount = 0
                    elif self.hasOpcode(message, 0x8):
                        running = False


        clientSock.close();
        print("Closing...")
        """
        self.lock.acquire()
        try:
            # Remove socket from client list
            self.clients.pop(index - self.indexOffset - 1)
            self.indexOffset += 1
        finally:
            self.lock.release()"""


if __name__ == '__main__':
    websocket = PingPongWebSocket(sys.argv[1], sys.argv[2], int(sys.argv[3]))
    websocket.start()
