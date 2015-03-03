#!/usr/bin/python

class RequestHeader:
    def __init__(self, message, delimeter='\r\n'):
        messageArr = message.split(delimeter)
        
        # Get Request type
        req = messageArr[0].split(' ')
        self.reqType = req[0]
        self.reqLocation = 'index.html' if req[1] == '/' else req[1][1:]
        self.httpVer = req[2]
        
        print("ReqType: ", self.reqType)
        print("ReqLoc: ", self.reqLocation)
        print("httpVer: ", self.httpVer)
        
        # Store into dictionary
        self.message = {}
        
        for mess in messageArr[1:]:
            if mess is not '':
                mess = mess.split(": ")
                # Fill the message dictionary
                self.message[mess[0]] = mess[1];
                

class ResponseHeader:
    def __init__(self, message, delimeter='\r\n'):
        messageArr = message.split(delimeter)
        
        # Get Request type
        resp = messageArr[0].split(' ')
        self.httpVer = resp[0]
        self.statusCode = resp[1]
        self.reason = resp[2]
        
        # Store into dictionary
        self.message = {}
        
        for mess in messageArr[1:]:
            if mess is not '':
                mess = mess.split(": ")
                # Fill the message dictionary
                self.message[mess[0]] = mess[1];