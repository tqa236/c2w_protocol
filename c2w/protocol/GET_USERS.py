import struct 

def GET_USERS(seq_number,user_id,first_user_id,nbr_users,room_id):

# Function to struct the PUT_NEW_MESSAGE packet
# MESSAGE_TYPE (1 byte 'B') = 14 (0x0E)
# SEQ_NUMBER (2 byte 'H')
# USER_ID (1 byte 'B')
# MESSAGE1_LENGTH (2 byte 'H') = 3 + MESSAGE2_LENGTH (1 for ROOM_ID and 2 for MESSAGE2_LENGTH)
# ROOM_ID (1 byte 'B')
# MESSAGE2_LENGTH (2 byte 'H') = size of MESSAGE
# MESSAGE (MESSAGE2_LENGTH bytes 's')
    
    message_type = 0x0A;
    message1_length = 3;


    code = '!BHBH' + 'BBB';

    data = struct.pack(code,message_type,seq_number,user_id,message1_length,first_user_id,nbr_users,room_id);

    return data;

A = GET_USERS(1,2,3,4,5);
print(A);
