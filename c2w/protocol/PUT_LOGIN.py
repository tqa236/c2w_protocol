# -*- coding: utf-8 -*-
from twisted.internet.protocol import DatagramProtocol
import struct
import time 

def PUT_LOGIN(seq_number,username):

    message_type = 0;
    user_id = 0;
    message_length = 1 + len(username)
    UL = len(username)
    code = '!BHBH' + 'B' + str(message_length) + 's'
    data = struct.pack(code,message_type,seq_number,user_id,message_length,UL,username.encode('utf-8'));
    return data
