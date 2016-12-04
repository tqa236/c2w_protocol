# -*- coding: utf-8 -*-
from twisted.internet.protocol import DatagramProtocol
from c2w.main.lossy_transport import LossyTransport
import logging
from . import unpacking
from . import packing
import c2w.main.constants


logging.basicConfig()
moduleLogger = logging.getLogger('c2w.protocol.udp_chat_server_protocol')


class c2wUdpChatServerProtocol(DatagramProtocol):

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
        
        
        
        
        

    def startProtocol(self):
        """
        DO NOT MODIFY THE FIRST TWO LINES OF THIS METHOD!!

        If in doubt, do not add anything to this method.  Just ignore it.
        It is used to randomly drop outgoing packets if the -l
        command line option is used.
        """
        self.transport = LossyTransport(self.transport, self.lossPr)
        DatagramProtocol.transport = self.transport
        
    def addEvent(self, event_type, content):
        # Je dois créer une list/dictionary avec tous les events
        # Je dois créer une variable current_event
        #   La clés sera le event_number et le contenu sera le paquet, déjà dans la forme binaire pour ajouter dans la réponse RESPONSE_EVENTS
        #   Les clés sont numérotés de 0 (/0x00/0x00/0x00) à 16777215 (/0xff/0xff/0xff)
        #   Si on arrive au fin de la list/dictionary on doit commencer par zero de nouveau
        #   On va écrire sur les anciennes contenue de les clés
        #       Paquets du type: NEW_MESSAGE, NEW_USER, SWITCH_ROOM et LOGOUT
        #       faire une fonction pour ajouter le événement dans la bonne position, dans la bonne forme de packet, incrementer current_event
        #       faire une fonction pour recueillir les événements de first_event to last_event de la liste
        pass
        
    def getEvent(self,last_event_id,nbr_events):
        # Je dois créer une list/dictionary avec tous les events
        # Je dois créer une variable current_event
        #   La clés sera le event_number et le contenu sera le paquet, déjà dans la forme binaire pour ajouter dans la réponse RESPONSE_EVENTS
        #   Les clés sont numérotés de 0 (/0x00/0x00/0x00) à 16777215 (/0xff/0xff/0xff)
        #   Si on arrive au fin de la list/dictionary on doit commencer par zero de nouveau
        #   On va écrire sur les anciennes contenue de les clés
        #       Paquets du type: NEW_MESSAGE, NEW_USER, SWITCH_ROOM et LOGOUT
        #   faire une fonction pour ajouter le événement dans la bonne position, dans la bonne forme de packet, incrementer current_event
        #       faire une fonction pour recueillir les événements de first_event to last_event de la liste
        pass
        
    def resendResponse(self,user_id,seq_number_user):
        # Quand arrivé un paquet 
        # 
        # On doit créer une dictionary avec le seq_number de chaque usager
        #   Le clé sera le nùmero_id et le contenu sera une list de deux elements [seq number usager, dernière paquet envoyé]
        #       #####LIRE Je ne suis pas sur se "seq number usager" est le seq_number que le serveur attends recevoir d'usager ou si est ça +/- 1
        #       Si on recevoir un paquet, on va vérifier dans la list/dictionary si on avait dejà tratés ce paquet
        #       Si on avait dejà tratés ce paquet, on ne va que reenvoyer le paquet existant en list/dictionary et changer rien du tout dans le code
        #           Cette méthode empêche de faire deux fois la même operation dans la base de données du serveur
        #           On va vérifier le paquet qui arrive par le nùmero_id et pour le seq_number
        #           Faire une function pour vérifier si le paquet reçu (nùmero_id,le seq_number) est le dernière paquet envoyé
        #               S'il est le paquet déjà envoyé: renvoie le paquet et retourne 1
        #               S'il n'est pas le dernière paquet envoyé: fait rien et retourne 0 
        #       On va ajouter une position de nùmero_id dans le instant que le usager bien fait un login_request
        #           Il faut une façon particulière de vérifier si on a déjà enregistrés le login en considérant que le message ne posséde pas le nùmero_id
        #               La solution est de chercher dans le objet que posséde la list de usager le nùmero_id en utilisant de le username
        #               Donc, avec le nùmero_id, on peut chercher le paquet déjà envoyè dans le dictionary et lui renvoie, retourn = 1
        #               S'il n'y a pas le username, donc on est libre pour enrégistrer le login retourn = 0
        pass



    def datagramReceived(self, datagram, host_port):
        """
        :param string datagram: the payload of the UDP packet.
        :param host_port: a touple containing the source IP address and port.
        
        Twisted calls this method when the server has received a UDP
        packet.  You cannot change the signature of this method.
        """
        
        fieldsList = unpacking.decode(datagram)
        
        i = 0
        ########### RESPONSE_USERS
        if fieldsList[0][0] == 0 :
            new_username = fieldsList[1][0]
            if self.serverProxy.getUserByName(new_username) != None :
                print(0)
                packet = packing.RESPONSE_LOGIN(fieldsList[0][1], 0, new_username, self.last_event_ID, 4)
                self.transport.write(packet, host_port)
                print(2)
            else :
                print(1)
                user_id = self.serverProxy.addUser(new_username, c2w.main.constants.ROOM_IDS.MAIN_ROOM)
                print("user id",user_id)
                packet = packing.RESPONSE_LOGIN(fieldsList[0][1], user_id, new_username, self.last_event_ID, 0)
                self.transport.write(packet, host_port)
                print(3)
"""
        elif fieldsList[0][0] == 2 :
            pass
        elif fieldsList[0][0] == 4 :
            pass
        elif fieldsList[0][0] == 6 :
            pass
        elif fieldsList[0][0] == 8 :
            pass
        elif fieldsList[0][0] == 10 :
            pass
        elif fieldsList[0][0] == 12 :
            pass
        elif fieldsList[0][0] == 14 :
            pass
"""
