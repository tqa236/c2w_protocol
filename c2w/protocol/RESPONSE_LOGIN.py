# -*- coding: utf-8 -*-
from twisted.internet.protocol import DatagramProtocol
import struct
import time 

def RESPONSE_LOGIN(seq_number,user_id,username,user_list,last_event_ID1,last_event_ID2):
    
    message_type = 1
    message_length = 5
    status_code = 0
    
    if len(user_list) >= 255:
        status_code = 2
    else:
        for i in user_list:
            if username == i.username:
                status_code = 4
                break
        
    code = '!BHBH' + 'BBBH'
    data = struct.pack(code,message_type,seq_number,0,message_length,status_code,user_id,last_event_ID1,last_event_ID2)
    return data
