#!/usr/bin/env python3

####################################
# Architect & Underground (c) 2017 #
#                                  #
# Sockets and networking           #
####################################

# Import init.py
import init.py

# Dependancies
import socket

# Set non-blocking mode for all sockets
socket.setdefaulttimeout( 0 )

class Server:

    clients = []

    # DEV: FALSE = NORMAL_OPERATION, TRUE = DEV_MODE
    # IP: The IP address to bind
    def __init__( self, dev=False, ip="" ):
        port = 23
        if mode: port = 4200

        self.termserv = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        self.termserv.bind(( ip, port ))
        self.termserv.listen( 10 )
        log.server( "Terminal server started on port " + str( port ) )

    # Accept all pending connections
    def accept( self ):
        while True:
            try:
               sock = self.termserv.accept( );
               cnew = Client( sock )
               Server.clients.append( cnew )
               log.client( cnew, "Connected to Phreaknet" )
            except socket.timeout:
               break
            except ex:
               raise ex

    def __del__( self ):
        self.termserv.close( )


class Client:

    def __init__( self, conn ):
        # Store ip, port and socket
        ( self.sock, ( self.ip, self.port ) ) = conn
        # This client's account
        self.acct = "guest"
        # A reference to this user's gateway machine and shell process
        self.gateway = [ None, 0 ]
        # Store buffered input from user
        self.buff = ""
        # Standard Terminal width and height
        self.width = 80
        self.height = 24

        # Send terminal initialization string
        self.sock.send( b"\xFF\xFD\x22\xFF\xFB\x01\xFF\xFB\x03\xFF\xFD\x1F" )

    # Send data to the terminal
    def output( self, msg ):
        # Encode the message if needed
        if not type( msg ) is bytes: msg = msg.encode( )
        self.sock.send( msg )

    # Buffer input from this client's socket
    # Return true if the client is still connected
    def input( self ):
        # Loop until we get a timeout exception
        while True:
            try:
                data = self.sock.recv( 1024 )
                if not data: return 0
                # Process IAC commands
                data = self.iac( data )
                # Append key press to buffer
                self.gateway[0].input( self.gateway[1], data.decode( ) )
            # No more data to recieve, timeout exception thrown
            except socket.timeout:
                return 1

    # Process terminal commands sent form the client
    def iac self, data ):
        # Process NAWS and record terminal height/width
        if (np = data.find( b"\xFF\xFA\x1F" )) >= 0):
            self.width  = int(data[np    ]) * 256 + int(data[np + 1])
            self.height = int(data[np + 2]) * 256 + int(data[np + 3])
            data.replace( b"\xFF\xFA\x1F", b"" )

        # Return the string without any of the commands
        return data

    def __del__( self ):
        self.println( )
        self.error( "Connection to Phreaknet terminated" )
        self.sock.close( )
