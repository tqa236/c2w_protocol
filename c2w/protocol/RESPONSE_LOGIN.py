# -*- coding: utf-8 -*-
from twisted.internet.protocol import DatagramProtocol
import struct
import time 

def RESPONSE_LOGIN(userName,user_ID,name_list,last_event_ID):
    
    l = str(len(userName))
    code = '1s' + str(len(userName)) + 's'
    data = struct.pack(code,l.encode('utf-8'),userName.encode('utf-8'))
    print(data)
    return data
