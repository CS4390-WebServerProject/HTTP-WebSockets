#!/usr/bin/python

class RequestHeader:
    def __init__(self, message, delimeter='\r\n'):
        messageArr = message.split(delimeter)
        
        # Get Request type
        req = messageArr[0].split(' ')
        self.reqType = req[0]
        self.reqLocation = 'index.html' if req[1] == '/' else req[1][1:]
        self.httpVer = req[2]
        
        extension = self.reqLocation.split('.')[1]
        contentType = ''
        
        if extension =='html':
            contentType = 'text/html'
        elif extension == 'xml':
            contentType = 'text/xml'
        elif extension == 'txt':
            contentType = 'text/plain'
        elif extension == 'css':
            contentType = 'text/css'
        elif extension == 'csv':
            contentType = 'text/csv'
        elif extension == 'javascript':
            contentType = 'text/javascript'
        elif extension == 'zip':
            contentType = 'application/zip'
        elif extension == 'gz':
            contentType = 'application/gzip'
        elif extension == 'ogg':
            contentType = 'application/ogg'
        elif extension == 'pdf':
            contentType = 'application/pdf'
        elif extension == 'mp4':
            contentType = 'audio/mp4'
        elif extension == 'mp3':
            contentType = 'audio/mpeg'
        elif extension == 'webm':
            contentType = 'audio/webm'
        else:
            contentType = 'multipart/mixed'
        
        # Store into dictionary
        self.message = {}
        
        self.message['Content-Type'] = contentType
        
        for mess in messageArr[1:]:
            if mess is not '':
                mess = mess.split(": ")
                # Fill the message dictionary
                self.message[mess[0]] = mess[1];
            
class ResponseHeader:
    def __init__(self, httpVer, statusCode, reason, delimeter='\r\n'):
        
        self.httpVer = httpVer
        self.statusCode = statusCode
        self.reason = reason
        
        self.message = {}
    
    def addMessage(self, header, message):
        self.message[header] = str(message)
    
    def generateMessage(self):
        joinedMessage = ''
        joinedMessage = self.httpVer + ' ' + str(self.statusCode) + ' ' + self.reason + '\r\n'
        for key, value in self.message.iteritems():
            joinedMessage += key + ': ' + value + '\r\n'
            
        return joinedMessage + '\r\n'