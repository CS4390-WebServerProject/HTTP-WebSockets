import hashlib, sys, base64
##############################################################################################
# Author: Tim Gowan
# Date : Tue, 3 Mar 2015 15:00:43 CST 
# Description: 
#   a program that prints the correct WebSocket Protocol reply based on a Sec-WebSocket-Key command line argument.
# 
#Pseudocode (From Wikipedia): 
#   The client sends a Sec-WebSocket-Key which is a random value that has been base64 encoded.
#   To form a response, the GUID 258EAFA5-E914-47DA-95CA-C5AB0DC85B11 is appended to this base64 encoded key. 
#   The base64 encoded key will not be decoded first.
#   The resulting string is then hashed with SHA-1, then base64 encoded.
#   Finally, the resulting reply occurs in the header Sec-WebSocket-Accept.
#
###############################################################################################

#Globally Unique Identifier for Websocket Handshake Reply
GUID = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11' 

#Creating sha1 Hash object
m=hashlib.sha1()

#Use CommandLineArgument for initial string to hash
def handShakeSHA(webSocketKey):
    return base64.b64encode(hashlib.sha1(webSocketKey+GUID).digest())

print(handShakeSHA(unicode("dGhlIHNhbXBsZSBub25jZQ==")))