# -*- coding: utf-8 -*-
from twisted.internet.protocol import DatagramProtocol
import struct
import time
import math
from twisted.internet import reactor

class SibylServerTimerUdpBinProtocol(DatagramProtocol):
    """The class implementing the Sibyl UDP binary server protocol.

        .. note::
            You must not instantiate this class.  This is done by the code
            called by the main function.

        .. note::

            You have to implement this class.  You may add any attribute and
            method that you see fit to this class.  You must implement the
            following method (called by Twisted whenever it receives a
            datagram):
            :py:meth:`~sibyl.main.protocol.sibyl_server_udp_bin_protocol.datagramReceived`
            See the corresponding documentation below.

    This class has the following attribute:

    .. attribute:: SibylServerProxy

        The reference to the SibylServerProxy (instance of the
        :py:class:`~sibyl.main.sibyl_server_proxy.SibylServerProxy` class).

            .. warning::

                All interactions between the client protocol and the server
                *must* go through the SibylServerProxy.

    """

    def __init__(self, sibylServerProxy):
        """The implementation of the UDP server text protocol.

        Args:
            sibylServerProxy: the instance of the server proxy.
        """
        self.sibylServerProxy = sibylServerProxy
    
        
    def datagramReceivedNoDelay(self,t, mess, host_port):
        """Called by Twisted whenever a datagram is received

        Twisted calls this method whenever a datagram is received.

        Args:
            datagram (bytes): the payload of the UPD packet;
            host_port (tuple): the source host and port number.

            .. warning::
                You must implement this method.  You must not change the
                parameters, as Twisted calls it.

        """
        s =  mess + chr(13)+chr(10)
        le = str(5 + len(s))
        code = '4s1s' + str(len(s)) + 's'
        buf = struct.pack(code,t.encode('utf-8'),le.encode('utf-8'),s.encode('utf-8'))
        ans = self.transport.write(buf,host_port)     


    def datagramReceived(self, datagram, host_port):
        """Called by Twisted whenever a datagram is received

        Twisted calls this method whenever a datagram is received.

        Args:
            datagram (bytes): the payload of the UPD packet;
            host_port (tuple): the source host and port number.

            .. warning::
                You must implement this method.  You must not change the
                parameters, as Twisted calls it.

        """
        data = datagram[5:]
        a = data.decode()
        b = a.find(' ') + 1
        c = a.find(chr(13))
        d = a[b:c]
        mess = self.sibylServerProxy.generateResponse(d)
        t1 = datagram[:4]
        t = t1.decode('utf-8')
       	x = math.ceil(math.log(len(mess)))
       	reactor.callLater(x, self.datagramReceivedNoDelay,t, mess, host_port)
        #self.datagramReceivedNoDelay(t, mess, host_port)
        
        
    