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

    # DEV: FALSE = NORMAL_OPERATION, TRUE = DEV_MODE
    # IP: The IP address to bind
    def __init__( self, dev=False, ip="" ):
        # Specify the port to host on
        port = 23
        if mode: port = 4200

        # Array of clients
        self.clients = []

        # The server socket
        self.termserv = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        self.termserv.bind(( ip, port ))
        self.termserv.listen( 10 )
        # Print the starting message
        log.server( "Terminal server started on port " + str( port ) )

    # Accept all pending connections
    def accept( self ):
        # Loop and accept all incomming connections
        while True:
            try:
               # Accept the connection
               sock = self.termserv.accept( )
               # Assign connection a client
               cnew = Client( sock )
               # Append client to array
               self.clients.append( cnew )
               log.client( cnew, "Connected to Phreaknet" )
            # No remaining connections, break
            except socket.timeout:
               break

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

        # If this is false, the client will be removed
        # DO NOT manually set this, call self.kill()
        self.alive = True

        # Send terminal initialization string
        self.sock.send( b"\xFF\xFD\x22\xFF\xFB\x01\xFF\xFB\x03\xFF\xFD\x1F" )

    # Send data to the terminal
    def output( self, msg ):
        # Encode the message if needed
        if not type( msg ) is bytes: msg = msg.encode( )
        self.sock.send( msg )

    # Buffer input from this client's socket
    # Return True if the client is still connected
    def input( self ):
        # Loop until we get a timeout exception
        while True:
            try:
                data = self.sock.recv( 1024 )
                if not data: return False
                # Process IAC commands
                data = self.iac( data )
                # Append key press to buffer
                self.gateway[0].input( self.gateway[1], data.decode( ) )
            # No more data to recieve, timeout exception thrown
            except socket.timeout:
                return True

    # Process terminal commands sent form the client
    def iac self, data ):
        # Process NAWS and record terminal height/width
        if (np = data.find( b"\xFF\xFA\x1F" )) >= 0):
            self.width  = int(data[np    ]) * 256 + int(data[np + 1])
            self.height = int(data[np + 2]) * 256 + int(data[np + 3])
            # Remove initial response string
            data.replace( b"\xFF\xFA\x1F", b"" )
            # Remove the 4 data bytes
            data = data[:np] + data[:np + 3]

        # Return the string without any of the commands
        return data

    # Call this to flag this client for termination
    def kill( self ):
        # Check if this client was connected to a tty
        if self.gateway is not None:
            # Tell the PhreakShell that it has no client
            self.gateway.tty = None
        # Print exit banner
        self.println( )
        self.error( "Connection to Phreaknet terminated" )
        self.sock.close( )
        # Flag client for deletion
        self.alive = False
