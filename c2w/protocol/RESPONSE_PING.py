# -*- coding: utf-8 -*-
from twisted.internet.protocol import DatagramProtocol
import struct
import time 

def RESPONSE_PING(last_event_id1,last_event_id2,room_id):
    message_type = 5
    message_length = 3
    code = '!BHBH' + 'BH'
    data = struct.pack(code,message_type,seq_number,user_id,message_length,last_event_id1,last_event_id2)
    return data
