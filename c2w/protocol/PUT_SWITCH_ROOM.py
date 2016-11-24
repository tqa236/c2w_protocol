import struct 

def PUT_SWITCH_ROOM(seq_number,user_id,room_id):

# Function to struct the PUT_NEW_MESSAGE packet
# MESSAGE_TYPE (1 byte 'B') = 14 (0x0E)
# SEQ_NUMBER (2 byte 'H')
# USER_ID (1 byte 'B')
# MESSAGE1_LENGTH (2 byte 'H') = 3 + MESSAGE2_LENGTH (1 for ROOM_ID and 2 for MESSAGE2_LENGTH)
# ROOM_ID (1 byte 'B')
# MESSAGE2_LENGTH (2 byte 'H') = size of MESSAGE
# MESSAGE (MESSAGE2_LENGTH bytes 's')
    
    message_type = 0x0C;
    message1_length = 1;


    code = '!BHBH' + 'B';

    data = struct.pack(code,message_type,seq_number,user_id,message1_length,room_id);

    return data;

A = PUT_SWITCH_ROOM(1,2,3);
print(A);
