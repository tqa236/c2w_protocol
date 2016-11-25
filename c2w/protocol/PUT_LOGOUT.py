# -*- coding: utf-8 -*-
from twisted.internet.protocol import DatagramProtocol
import struct
import time 

def PUT_LOGOUT(seq_number,user_ID):

    message_type = 2;
    
    message_length = 0
   
    code = '!BHBH' 
    data = struct.pack(code,message_type,seq_number,user_id,message_length);
    return data
