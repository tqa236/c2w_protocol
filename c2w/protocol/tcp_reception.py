# -*- coding: utf-8 -*-
import struct 

def framing(frame) :

    messageLength = 65536
    if frame is None :
        messageLength = 65536    
    else :
        if len(frame) >= 6:
            header = frame[:6]
            messageInfo = struct.unpack('!BHBH', header)
            messageLength = messageInfo[3] + 6
    
    return (len(frame) >= messageLength, messageLength)
