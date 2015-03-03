#!/usr/bin/python
import Date;

class ResponseHeader:
    def __init__(self, httpVer, status):
        self.message = {}
        self.strMessage = ''
        
        if status == 200:
            self.strMessage.append(httpVer + ' 200 OK')
        elif status == 304:
            self.strMessage.append(httpVer + ' 204 NOT MODIFIED')
        elif status == 400:
            self.strMessage.append(httpVer + ' 400 BAD REQUEST')
        elif status == 401:
            self.strMessage.append(httpVer + ' 401 UNAUTHORIZED')
        elif status == 403:
            self.strMessage.append(httpVer + ' 403 FORBIDDEN')
        elif status == 404:
            self.strMessage.append(httpVer + ' 404 NOT FOUND')
        elif status == 500:
            self.strMessage.append(httpVer + ' 500 INTERNAL SERVER ERROR')
        elif status == 503:
            self.strMessage.append(httpver + ' 503 SERVICE UNAVAILABLE')
            
        self.strMessage.append('\r\n')