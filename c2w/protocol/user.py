

class User():
    def __init__(self,user_id,username,room_id):
        self.user_id = user_id ;
        self.username = username;
        self.room_id = room_id;

client1 = User(0,'Rodrigo',0);
print(client1.username);
client2 = User(1,'Guinther',0);
print(client2.username);

lista = [client1,client2];
lista.append(client1);
print(lista[2].username);



