# -*- coding: utf-8 -*-
from twisted.internet.protocol import DatagramProtocol
import struct
import time 

def RESPONSE_LOGOUT(seq_number,user_id):
    
    message_type = 3;
    message_length = 1
    status_code = 0
    
    code = '!BHBH' + 'B'
    data = struct.pack(code,message_type,seq_number,user_id,message_length,status_code);
    return data
