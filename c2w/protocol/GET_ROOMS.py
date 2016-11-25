import struct 

def GET_ROOMS(seq_number,user_id,first_room_id,nbr_rooms):

# Function to struct the PUT_NEW_MESSAGE packet
# MESSAGE_TYPE (1 byte 'B') = 14 (0x0E)
# SEQ_NUMBER (2 byte 'H')
# USER_ID (1 byte 'B')
# MESSAGE1_LENGTH (2 byte 'H') = 3 + MESSAGE2_LENGTH (1 for ROOM_ID and 2 for MESSAGE2_LENGTH)
# ROOM_ID (1 byte 'B')
# MESSAGE2_LENGTH (2 byte 'H') = size of MESSAGE
# MESSAGE (MESSAGE2_LENGTH bytes 's')
    
    message_type = 0x08;
    message_length = 0x02;


    code = '!BHBH' + 'BB';

    data = struct.pack(code,message_type,seq_number,user_id,message_length,first_room_id,nbr_rooms);

    return data;

A = GET_ROOMS(5,16,3,4);
print(A);
