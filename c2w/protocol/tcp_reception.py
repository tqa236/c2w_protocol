# -*- coding: utf-8 -*-
import struct 

def framing(frame) :
    """
    This function returns if the given frame is ready to be unpacked.
    :param frame: a byte containing all data currently received and not yet unpacked
    """

    messageLength = 65537 #Note that the max length of the frame is 65536, so this value ensure that the len(frame) >= messageLength test is False
    if frame == b'' :
        messageLength = 65537    
    else :
        if len(frame) >= 6: #The header of any frame is 6 bytes long, so this test check if the header can be decoded.
            header = frame[:6]
            messageInfo = struct.unpack('!BHBH', header)
            messageLength = messageInfo[3] + 6 #And then get the messageLength field
    
    return (len(frame) >= messageLength, messageLength)
