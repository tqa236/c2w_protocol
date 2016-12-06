# -*- coding: utf-8 -*-
from twisted.internet.protocol import DatagramProtocol
from c2w.main.lossy_transport import LossyTransport
from twisted.internet import reactor

import logging
from . import unpacking
from . import packing
import c2w.main.constants
from c2w.main.constants import ROOM_IDS

logging.basicConfig()
moduleLogger = logging.getLogger('c2w.protocol.udp_chat_server_protocol')


class c2wUdpChatServerProtocol(DatagramProtocol):

    # Il faut commencer le videoStreaming aprés avoir changé de salle.
    

    def __init__(self, serverProxy, lossPr):
        """
        :param serverProxy: The serverProxy, which the protocol must use
            to interact with the user and movie store (i.e., the list of users
            and movies) in the server.
        :param lossPr: The packet loss probability for outgoing packets.  Do
            not modify this value!

        Class implementing the UDP version of the client protocol.

        .. note::
            You must write the implementation of this class.

        Each instance must have at least the following attribute:

        .. attribute:: serverProxy

            The serverProxy, which the protocol must use
            to interact with the user and movie store in the server.

        .. attribute:: lossPr

            The packet loss probability for outgoing packets.  Do
            not modify this value!  (It is used by startProtocol.)

        .. note::
            You must add attributes and methods to this class in order
            to have a working and complete implementation of the c2w
            protocol.
        """
        #: The serverProxy, which the protocol must use
        #: to interact with the server (to access the movie list and to 
        #: access and modify the user list).
        
        self.serverProxy = serverProxy
        self.lossPr = lossPr
        
        self.events_list = {}
        self.last_event_ID = 0
        self.seq_number_users = {}
        # [0]   last_event   
        # [1]   packet 
        # [2]   IP 
        # [3]   PORT 
        self.delay_to_disconnect = 60
        
        self.rooms_actives = []
        
    
###########
       
    def startProtocol(self):
        """
        DO NOT MODIFY THE FIRST TWO LINES OF THIS METHOD!!

        If in doubt, do not add anything to this method.  Just ignore it.
        It is used to randomly drop outgoing packets if the -l
        command line option is used.
        """
        self.transport = LossyTransport(self.transport, self.lossPr)
        DatagramProtocol.transport = self.transport
    
###########
        
    def addEvent(self, event_type, user_id, content):
        # Je dois créer une dictionary avec tous les events
        # Je dois créer une variable current_event
        # La clés sera le event_number et le contenu sera le paquet, déjà dans la forme binaire pour ajouter dans la réponse RESPONSE_EVENTS
        # Les clés sont numérotés de 0 (/0x00/0x00/0x00) à 16777215 (/0xff/0xff/0xff)
        # Si on arrive au fin de la dictionary on doit commencer par zero de nouveau
        # On va écrire sur les anciennes contenue de les clés
        # Paquets du type: NEW_MESSAGE, NEW_USER, SWITCH_ROOM et LOGOUT
        # faire une fonction pour ajouter le événement dans la bonne position, dans la bonne forme de packet, incrementer current_event
        # faire une fonction pour recueillir les événements de first_event to last_event de la liste

        # event_type = 0x01 # MESSAGE # content = message(String)
        # event_type = 0x02 # NEW_USER # content = username(String)
        # event_type = 0x03 # SWITCH_ROOM # content = old_room_id
        # event_type = 0x04 # LOGOUT # content = None
                
        room_id = self.serverProxy.getUserById(user_id).userChatRoom    # On récupere le room_id du usager
        if room_id == c2w.main.constants.ROOM_IDS.MAIN_ROOM :        # Si nous sommes dans la MAIN ROOM
            room_id = 0
        else :
            room_id = self.serverProxy.getMovieByTitle(room_id).movieId   # On change c2w.main.constants.ROOM_IDS.MAIN_ROOM par 0 (entière)
        
        if self.last_event_ID == 16777215 :                             # Si on arrive à la fin, on retourne au débout
            event_id = 0
        else :                                                          # Sinon on incremente
            event_id =  self.last_event_ID + 1
        
        coded_event = packing.CODE_EVENT(event_type, event_id, room_id, user_id, content)   # code le event
        self.events_list[event_id] = coded_event                                  # on enregistre le event sur le bon champ
        
        self.last_event_ID = event_id                                             # On incremente self.last_event_ID
        
    
###########
              
    def getEvent(self,last_event_id,room_id,nbr_events): ######################################################## Il faut commenter
        # Je dois créer une list/dictionary avec tous les events
        # Je dois créer une variable current_event
        # La clés sera le event_number et le contenu sera le paquet, déjà dans la forme binaire pour ajouter dans la réponse RESPONSE_EVENTS
        # Les clés sont numérotés de 0 (/0x00/0x00/0x00) à 16777215 (/0xff/0xff/0xff)
        # Si on arrive au fin de la list/dictionary on doit commencer par zero de nouveau
        # On va écrire sur les anciennes contenue de les clés
        # Paquets du type: NEW_MESSAGE, NEW_USER, SWITCH_ROOM et LOGOUT
        # faire une fonction pour ajouter le événement dans la bonne position, dans la bonne forme de packet, incrementer current_event
        # faire une fonction pour recueillir les événements de first_event to last_event de la liste
       
        #Je n'utilise pas encore room_id, mais, je crois que je vais changer
        
        n_event = last_event_id + 1
        get_events_list = b''   
        real_events_number = 0
        i = 0
        end = False
        while i < nbr_events and not end :
            i += 1
            if n_event == self.last_event_ID :
                get_events_list += self.events_list[n_event]
                real_events_number = real_events_number + 1
                end = True
            elif n_event == 16777215 :
                get_events_list += self.events_list[n_event]
                n_event = 0
                real_events_number = real_events_number + 1
            else :
                get_events_list += self.events_list[n_event]
                n_event = n_event + 1
                real_events_number = real_events_number + 1    
        return [get_events_list, real_events_number]
    
###########
        
    def lostResponse(self,user_id,seq_number, ip_number, port_number):

        if user_id in self.seq_number_users :         
            key_seq = seq_number == self.seq_number_users[user_id][0]
            key_ip = ip_number == self.seq_number_users[user_id][2]
            key_port = port_number == self.seq_number_users[user_id][3]
            
            if key_seq and key_ip and key_port :
                packet = self.seq_number_users[user_id][1]
                resend = True
            else :
                packet = 0
                resend = False
        else :
                packet = 0
                resend = False            

        return [resend, packet]
    
###########
         
    def loginRules(self, username):
        # Cette function limite les caractères, la taille et la forme d'username
        # return TRUE si le username est bon
        # return FALSE si le username n'est pas bon
        return 1
    
###########
         
    def getRooms(self, first_room_id, nbr_rooms):   ######################################################## Il faut commenter
    
        movie_list = self.serverProxy.getMovieList()
        users_list = self.serverProxy.getUserList()
        

        movie_id_selected = []
        for movie in movie_list :
            if movie.movieId >= first_room_id :
                movie_id_selected.append(movie.movieId)

                
        movie_id_sorted_list = sorted(movie_id_selected, key=int)
        
        if nbr_rooms > len(movie_id_sorted_list) :
            movie_id_sorted_list = movie_id_sorted_list[0:nbr_rooms]
        else :
            movie_id_sorted_list = movie_id_sorted_list[0:len(movie_id_sorted_list)]    
        
        movie_list_to_response_rooms = []
        n_users_room = [] # il faut faire un vecteur de zeros
        
        for i in range(len(movie_id_sorted_list)) :
            movie_list_to_response_rooms.append(self.serverProxy.getMovieById(movie_id_sorted_list[i]))
            n_users_room.append(0)
            for users in users_list :
                if users.userChatRoom == movie_id_sorted_list[i] :
                    n_users_room[i] = n_users_room[i] + 1                 
                    
        return [movie_list_to_response_rooms, n_users_room]
        
###########
         
    def getUsers(self, first_user_id, nbr_users, room_id):
        # l'entrées : le ID du première usager que le client a demandé,
        # le nombre de de usagers et le room où on va chercher
        
        # le résultat : une liste de la classe c2wUser avec le nombre d'usagers demandé dans la bonne salle
        
        users_list = self.serverProxy.getUserList()                                  # On trouve tous les usagers
        
        user_id_selected = []
        for user in users_list :                                                     # On prend les usagers dans la bonne movie room
            if (user.userChatRoom == room_id and user.userId >= first_user_id) or ROOM_IDS.MAIN_ROOM :
                user_id_selected.append(user.userId)                                    # On prend le id de tous les usagers sélectionnés
                
        user_id_sorted_list = sorted(user_id_selected, key=int)                      # On ordenne le ID des usagers
        
        if nbr_users > len(user_id_sorted_list) :
            user_id_sorted_list = user_id_sorted_list[0:nbr_users]                   # On ne prend que le nombre demandé
        else :
            user_id_sorted_list = user_id_sorted_list[0:len(user_id_sorted_list)]    # On prend le maximum possible
        
        user_list_to_response_users = []                                             # liste vide pour garder le résultat
        
        for i in range(len(user_id_sorted_list)) :
            user_list_to_response_users.append(self.serverProxy.getUserById(user_id_sorted_list[i])) # On prend les objets de la classe c2wUser
                    
        return user_list_to_response_users
        
###########

    def streamingControl(self):
    
        full_movie_list = self.serverProxy.getMovieList()
        full_user_list = self.serverProxy.getUserList()
        
        for movie in full_movie_list :
            someone_is_watching = False                                                 # Dans le debout de la recherche, personne regarde la video    
            if movie.movieTitle != ROOM_IDS.MAIN_ROOM :                                 # Si la movie room n'est pas la na MAIN_ROOM (sans straming)
                
                for user in full_user_list :
                    if user.userChatRoom == movie.movieTitle :                          # Il y a quelqu'un dans la room
                        someone_is_watching = True                                      # Il y a quelqu'un en regardant la video
                        self.serverProxy.startStreamingMovie(movie.movieTitle)          # On commence le streaming                        
                        if not movie.movieTitle in self.rooms_actives :                 # Le film n'étais pas encore en straming
                            self.serverProxy.startStreamingMovie(movie.movieTitle)      # On commence le streaming
 
                            self.rooms_actives.append(movie.movieTitle)                 # On ajute le film à le liste des films en streaming
                        break                                                           # On sort du boucle, parce que un client est souffisant

                                                           
                if not someone_is_watching :                                            # Personne regarde cette video
                    if movie.movieTitle in self.rooms_actives :                         # Il y avait avant quelqu'un qui regardait cette video
                        self.serverProxy.stopStreamingMovie(movie.movieTitle)           # On arrête le streaming  
                        self.rooms_actives.remove(movie.movieTitle)                     # On supprime le video de la liste de video en cours  
###########

    def checkConnectiontUser(self, user_id, seq_number):
    
        if not self.serverProxy.getUserById(user_id) is None :        
            if seq_number == self.seq_number_users[user_id][0] :
                self.addEvent(0x04, user_id, None)                                               # On ajoute le logout à les événements           
                self.serverProxy.removeUser(self.serverProxy.getUserById(user_id).userName)      # On supprime le user (On doit faire ça après addEvent)
                print('Disconnected an inactive user : ' + str(user_id))
            else :
                reactor.callLater(self.delay_to_disconnect, self.checkConnectiontUser, user_id, self.seq_number_users[user_id][0])
             
###########
       
    def datagramReceived(self, datagram, host_port):
        """
        :param string datagram: the payload of the UDP packet.
        :param host_port: a touple containing the source IP address and port.
        
        Twisted calls this method when the server has received a UDP
        packet.  You cannot change the signature of this method.
        """
        
        fieldsList = unpacking.decode(datagram)
        
        message_type = fieldsList[0][0]
        seq_number = fieldsList[0][1]
        user_id = fieldsList[0][2]
        server_id = 0
        
        # resend est un boolean, si resend = False on a jamais envoyé ce paquet, si resend = True on doit renvoyer le paquet
        resend, packet = self.lostResponse(user_id, seq_number, host_port[0], host_port[1])                
        
        if resend :
            self.transport.write(packet, host_port)
        else :
            ########### LOGIN REQUEST / RESPONSE_LOGIN
            if message_type == 0x00 :                                                                      # On a reçu le message de login
                new_username = fieldsList[1][0]
                status = 5                
                if self.loginRules(new_username) == 1:                                                     # Il faut passer par les régles du serveur 
                    if  self.serverProxy.userExists(new_username) :                                        # Il y a déjà quelqu'un avec le même username
                        packet = packing.RESPONSE_LOGIN(0, 0, new_username , self.last_event_ID, 0x04)     # faire le paquet    
                        status = 4                                           
                    elif len(self.serverProxy.getUserList()) > 255 :                                       # Le système est plein d'usagers
                        packet = packing.RESPONSE_LOGIN(0, 0, new_username , self.last_event_ID, 0x02)     # faire le paquet 
                        status = 2
                    elif not self.serverProxy.userExists(new_username) :                                   # Il n'y a personne avec le même username
                        user_id_login = self.serverProxy.addUser(new_username, ROOM_IDS.MAIN_ROOM) # On ajoute le user à base de données et prendre le id
                        
                        self.addEvent(0x02, user_id_login, new_username)                                   # On ajoute le login à les événements
                        packet = packing.RESPONSE_LOGIN(0, user_id_login, new_username , self.last_event_ID,0x00) # faire le paquet
                        
                        self.seq_number_users[user_id_login] = [0,packet, host_port[0], host_port[1]]      # On va créer une position pour le user seq_number
                        
                        status = 0
                    else :                                                                                  # On ne sait pas ce que se passe
                        packet = packing.RESPONSE_LOGIN(0, 0, new_username , self.last_event_ID, 0x01)      # faire le paquet 
                        status = 1                                 
                else :
                    status = 3                                                                                       # Le username ne passe pas pour les lois du serveur
                    packet = packing.RESPONSE_LOGIN(0, 0, new_username , self.last_event_ID, 0x03)          # faire le paquet
                
                self.transport.write(packet, host_port)                                                     # On envoie le paquet
                if status == 0 :
                    reactor.callLater(self.delay_to_disconnect, self.checkConnectiontUser, user_id_login, self.seq_number_users[user_id_login][0])
                        
            ###########        
            
            if user_id in self.seq_number_users :                                                       # On vérifie si le clé existe dans le dictionary                 
                if seq_number == self.seq_number_users[user_id][0] + 1 :                                # Authentification par la bonne clé seq_number~user_id
            
                ########### LOGOUT REQUEST / RESPONSE_LOGOUT
                    if message_type == 0x02 :                                                           # On a reçu le message de logout
                        if self.serverProxy.getUserById(user_id) :                                      # On vérifie si il y a le user sur la base de données                        
                            self.addEvent(0x04, user_id, None)                                          # On ajoute le logout à les événements
                            self.seq_number_users[user_id][0] = self.seq_number_users[user_id][0] + 1   # On incrémente le seq_number du user                       
                            self.serverProxy.removeUser(self.serverProxy.getUserById(user_id).userName) # On supprime le user (On doit faire ça après addEvent)
                            packet = packing.RESPONSE_LOGOUT(seq_number,server_id,0x00)                 # On fait le paquet 
                            self.seq_number_users[user_id][1] = packet                                  # On enregistre le paquet
                            self.transport.write(packet, host_port)
                            
                        else :                                                                          # Si on a déjà supprimés le user de la base de données
                            packet = packing.RESPONSE_LOGOUT(seq_number,server_id,0x00)
                            self.transport.write(packet, host_port)
                            
                        if self.serverProxy.getUserById(user_id) :    # Si même après avoir supprimé le user, il existe dans la base de données
                            packet = packing.RESPONSE_LOGOUT(seq_number,server_id,0x01)                   # On fait le paquet 
                            self.transport.write(packet, host_port)                                     # On envoie le paquet      
                
                ########### PING REQUEST / RESPONSE_PING
                    if message_type == 0x04 :                                                       # On a reçu le message de get_ping
                        packet = packing.RESPONSE_PING(seq_number, server_id, self.last_event_ID)   # On fait le paquet avec last_event_ID courrant
                        self.seq_number_users[user_id][0] = self.seq_number_users[user_id][0] + 1   # On incrémente le seq_number du user
                        self.seq_number_users[user_id][1] = packet                                  # On enregistre le paquet
                        self.transport.write(packet, host_port)      
                
                ########### EVENTS REQUEST / RESPONSE_EVENTS
                    if message_type == 0x06 :                                                       # On a reçu le message de get_events
                        last_event_id = fieldsList[1][0]                                            # Le premier event que le usager demande
                        nbr_events = fieldsList[1][1]                                               # Le nombre de events que le usager demande
                        room_id = fieldsList[1][2]                                                  # La room où le usager demande les events
                        
                        getEvents = self.getEvent(last_event_id,room_id,nbr_events)
                        packet_content = getEvents[0]                                               # le packet binaire avec tous les events déjà codé (sans le nbr_events)
                                           
                        real_events_number = getEvents[1]                                            # Le nombre de events qu'on envoie (pas necessairement le celui demandé)
                        message_length = len(packet_content)                                        # la taille de la message (sans nbr_events, on ajoute ça dans RESPONSE_EVENTS_HEAD)
                        packet_head = packing.RESPONSE_EVENTS_HEAD(seq_number, server_id, real_events_number,message_length) # le packet binaire avec le message head
                        packet = packet_head + packet_content       # On additionne les deux packet binaires                               
                        
                        self.seq_number_users[user_id][0] = self.seq_number_users[user_id][0] + 1   # On incrémente le seq_number du user
                        self.seq_number_users[user_id][1] = packet                                  # On enregistre le paquet
                        
                        self.transport.write(packet, host_port)
                        
                ########### ROOMS REQUEST / RESPONSE_ROOMS
                    if message_type == 0x08 :                                                               # On a reçu le message de get_rooms
                        first_room_id = fieldsList[1][0]                                                    # La première movie room que on va envoyer
                        nbr_rooms = fieldsList[1][1]                                                        # Le nombre de movie room que on va envoyer
                        
                        movie_list = self.getRooms(first_room_id, nbr_rooms)[0]                                  # Une liste avec les classes c2wMovie qu'on va envoyer
                        n_users_room_list = self.getRooms(first_room_id, nbr_rooms)[1]                           # Une liste avec le nombre de usagers dans chaque movie room
                        
                        packet = packing.RESPONSE_ROOMS(seq_number, server_id, movie_list, n_users_room_list) # On fait le paquet
                        
                        self.seq_number_users[user_id][0] = self.seq_number_users[user_id][0] + 1           # On incrémente le seq_number du user
                        self.seq_number_users[user_id][1] = packet                                          # On enregistre le paquet
                        self.transport.write(packet, host_port)                                             # On envoie le paquet  
                
                ########### USERS REQUEST / RESPONSE_USERS
                    if message_type == 0x0A :                                                      # On a reçu le message de get_users
                        first_user_id = fieldsList[1][0]                                           # Le première user que on va envoyer
                        nbr_users = fieldsList[1][1]                                               # Le nombre de users que on va envoyer
                        
                        user_list = self.getUsers(first_user_id, nbr_users, self.serverProxy.getUserById(user_id).userChatRoom)                             
                        # Une liste avec les classes c2wUser qu'on va envoyer
                        
                        packet = packing.RESPONSE_USERS(seq_number, server_id, user_list,self.serverProxy)            # On fait le paquet
                        
                        self.seq_number_users[user_id][0] = self.seq_number_users[user_id][0] + 1  # On incrémente le seq_number du user
                        self.seq_number_users[user_id][1] = packet                                 # On enregistre le paquet
                        self.transport.write(packet, host_port)                                    # On envoie le paquet            
                    
                ########### SWITCH ROOM REQUEST / RESPONSE_SWITCH_ROOM
                    if message_type == 0x0C :                                                       # On a reçu le message de get_users
                        username = self.serverProxy.getUserById(user_id).userName                   # Le nom d'usager
                        old_room = self.serverProxy.getUserById(user_id).userChatRoom               # L'ancienne room
                        new_room = fieldsList[1][0]                                                 # la nouvelle room
                        
                        if new_room == 0  :                                                         # Si nous sommes dans la MAIN ROOM
                            new_room = c2w.main.constants.ROOM_IDS.MAIN_ROOM
                        else :
                            new_room = self.serverProxy.getMovieById(new_room).movieTitle
                            
                        if old_room == c2w.main.constants.ROOM_IDS.MAIN_ROOM :
                            old_room = 0
                        else :
                            old_room = self.serverProxy.getMovieByTitle(old_room).movieId
                        
                        if new_room != c2w.main.constants.ROOM_IDS.MAIN_ROOM and self.serverProxy.getMovieByTitle(new_room) is None :
                            # Il existe pas le movie room (manque le bon code)                        
                            packet = packing.RESPONSE_SWITCH_ROOM(seq_number, server_id, 0x01)        # On fait le paquet 
                        
                        else :                                                                     # S'il existe la room dans le système 
                            self.serverProxy.updateUserChatroom(username, new_room)                 # On met à jour la room
                        
                            if new_room == self.serverProxy.getUserById(user_id).userChatRoom :     # On a bien mis à jour la room
                                self.addEvent(0x03, user_id, old_room)                              # On ajoute à les events     
                                packet = packing.RESPONSE_SWITCH_ROOM(seq_number, server_id, 0x00)    # On fait le paquet
                            else :
                                packet = packing.RESPONSE_SWITCH_ROOM(seq_number, server_id, 0x01)    # On fait le paquet
                                
                        self.seq_number_users[user_id][0] = self.seq_number_users[user_id][0] + 1   # On incrémente le seq_number du user
                        self.seq_number_users[user_id][1] = packet                                  # On enregistre le paquet  
                        self.transport.write(packet, host_port)                                     # On envoie le paquet                            
                
                    
                ########### MESSAGE REQUEST / RESPONSE_NEW_MESSAGE
                    if message_type == 0x0E :                                                         # On a reçu le message de put_new_message
                        room_message = fieldsList[1][0]                                               # Le movie id lequel le user envoie le message
                        new_message = fieldsList[1][1]                                                # Le message (String) envoyé par le user
                        
                        if room_message == 0  :                                                           # Si nous sommes dans la MAIN ROOM
                            room_message = c2w.main.constants.ROOM_IDS.MAIN_ROOM
                        else :
                            room_message = self.serverProxy.getMovieById(room_message).movieTitle
                            
                        if room_message is None :                                                       # Il n'y a pas le movie room dans le système
                            packet = packing.RESPONSE_NEW_MESSAGE(seq_number, server_id, 0x02)          # On fait le paquet                        
                                                        
                        elif self.serverProxy.getUserById(user_id).userChatRoom != room_message :     # La movie room n'est pas la movie room courant d'usager
                            packet = packing.RESPONSE_NEW_MESSAGE(seq_number, server_id, 0x03)          # On fait le paquet
                        
                        elif self.serverProxy.getUserById(user_id).userChatRoom == room_message :    #Le bon cas
                            self.addEvent(0x01, user_id, new_message)                                 # On ajoute à les events
                            packet = packing.RESPONSE_NEW_MESSAGE(seq_number, server_id, 0x00)          # On fait le paquet
                            
                        else:                                                                         # On ne sait pas ce que se passe
                            packet = packing.RESPONSE_NEW_MESSAGE(seq_number, server_id, 0x01)          # On fait le paquet
                        
                        self.seq_number_users[user_id][0] = self.seq_number_users[user_id][0] + 1     # On incrémente le seq_number du user
                        self.seq_number_users[user_id][1] = packet                                    # On enregistre le paquet  
                        self.transport.write(packet, host_port)                                       # On envoie le paquet
                            
                
            self.streamingControl()            
                
                ###########                       
                                                  

                                        
                        
                        
                        
                        
                        
