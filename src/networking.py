#!/usr/bin/env python3

####################################
# Architect & Underground (c) 2017 #
#                                  #
# Sockets and networking           #
####################################

# Import init.py
from init import *

# Dependancies
import socket
from random import randint

# Load the login banner
login_banner = []
# Store the data entry positions (blank spots in the banner)
login_pos = [ (12, 17), (14, 57), (19, 28), (21, 28) ]
with open( '../dat/phreaknet/login.bnr' ) as bnr:
    while True:
        # Get next line, and remove \r\n
        ln = bnr.readline( ).strip( "\n" ).strip( "\r" )
        # Break on EOF
        if ln == "": break
        # Append the banner line by line
        login_banner.append( ln )

# Load the privacy banner
privacy_banner = []
# Store the data entry position for this banner
privacy_pos = ( 22, 77 )
with open( '../dat/phreaknet/privacy.bnr' ) as bnr:
    while True:
        # Get next line
        ln = bnr.readline( ).strip( "\n" ).strip( "\r" )
        # Break on EOF
        if ln == "": break
        # Append the banner line by line
        privacy_banner.append( ln )

# Load the legal banner
legal_banner = []
# Store the data entry position for this banner
legal_pos = ( 20, 63 )
with open( '../dat/phreaknet/legal.bnr' ) as bnr:
    while True:
        # Get next line
        ln = bnr.readline( ).strip( "\n" ).strip( "\r" )
        # Break on EOF
        if ln == "": break
        # Append the banner line by line
        legal_banner.append( ln )

# Load the bootmeister banner
boot_banner = []
# Store the data entry position for this banner
boot_pos = ( 22, 56 )
with open( '../dat/phreaknet/boot.bnr' ) as bnr:
    while True:
        # Get next line
        ln = bnr.readline( ).strip( "\n" ).strip( "\r" )
        # Break on EOF
        if ln == "": break
        # Append the banner line by line
        boot_banner.append( ln )

# Load the manager banner
manager_banner = []
# Store the data entry position for this banner
manager_pos = [ ( 13, 29 ), ( 13, 52 ), ( 22, 59 ) ]
with open( '../dat/phreaknet/manager.bnr' ) as bnr:
    while True:
        # Get next line
        ln = bnr.readline( ).strip( "\n" ).strip( "\r" )
        # Break on EOF
        if ln == "": break
        # Append the banner line by line
        manager_banner.append( ln )

# This server handles all external connections, NOT GAME PLAY
# There should only be functions related to managing the conns here
class Server:

    # DEV: FALSE = NORMAL_OPERATION, TRUE = DEV_MODE
    # IP: The IP address to bind
    def __init__( self, dev=False, ip="" ):
        # Specify the port to host on
        port = 23
        if dev: port = 4200

        # Array of clients
        self.clients = []

        # The server socket
        self.termserv = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        # Reuse dead sockets
        self.termserv.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
        # Bind the correct IP and Port
        self.termserv.bind(( ip, port ))
        # Set a timeout (server sockets dont support nonblocking)
        self.termserv.settimeout( 0.01 )
        # Listen for connections
        self.termserv.listen( 10 )
        # Print the starting message
        xlog( "Terminal server started on port " + str( port ) )

    # Accept all pending connections
    def accept( self ):
        # Loop and accept all incomming connections
        while True:
            try:
               # Accept the connection
               sock = self.termserv.accept( )
               # Disable socket blocking
               sock[0].setblocking( 0 )
               # Assign connection a client
               cnew = TelnetClient( self, sock )
               # Append client to array
               self.clients.append( cnew )
               xlog( "Connected to PhreakNET", cnew )
            # No remaining connections, break
            except socket.timeout:
               break

    def __del__( self ):
        # Terminate all clients
        for c in self.clients:
            c.kill( )
        # Ensure that we unbind the socket from the port
        self.termserv.close( )
        # Print shutdown message
        xlog( "Terminal server shutdown successfully" )

class Client:

    def __init__( self, tserv, addr ):
        # Store a reference to the Terminal Server
        self.tserv = tserv
        # The IP this user is connecting from
        self.ip = addr[0]
        # The port this user is connecting from
        self.port = addr[1]
        # A reference to this user's gateway machine and shell process
        self.gateway = None
        # A reference to this user's account
        self.account = None
        # Standard Terminal width and height
        self.size = ( 80, 24 )

        # Exact time this client connected
        self.first = time.time( )
        # Updated when data is recieved
        self.last = time.time( )

        # Login page data
        # Which prompt are we on?
        self.ac_prompt = 0
        # Are we logging in or registering?
        self.ac_login = True
        # Username
        self.ac_user = ""
        # Password
        self.ac_pass = ""

        # Gateway manager program data
        # What tty are we connecting to?
        self.mg_tty = ""

        # True until proven false
        self.is_robot = True

        # If this is false, the client will be removed
        # DO NOT manually set this, call self.kill()
        self.alive = True

        # Print the login banner
        self.stdout( "\r\n*** Welcome to PhreakNET ***\r\n\n" )
        self.stdout( "If you are reading this then you have not provided sufficient proof that you\r\n" )
        self.stdout( "are not a robot. Please reconnect with a modern Telnet client. You will be\r\n" )
        self.stdout( "automatically disconnected within 5 seconds.\r\n" )

    # Override this to handle output
    def stdout( self, msg ):
        pass

    # Override this to handle input, should return something
    def stdin( self ):
        # This should auto-kill anything that doesn't override this
        return None

    # Process input from the client
    def get_stdin( self ):
        # Get a list of keypresses
        msg = self.stdin( )
        # Make sure the client is still connected
        if msg is None: return False
        # Process each keypress
        for data in msg:
            # Disconnect if escape key is pressed
            if data == "\x1B":
                # Move the cursor to the last line
                self.stdout( ansi_move( self.size[1], 1 ) )
                # Disconnect
                self.kill( )
                return False

            # Check if we're connected to a gateway machine
            if self.gateway is not None:
                # Resolve the gateway from this IP
                gatehost = Host.find_ip( self.gateway[0] )
                # Does the gateway still exist?
                if gatehost is not None:
                    # Formulate packet with no delay or lag
                    msg = ( data, 0, -1 )
                    # Send data to the gateway
                    if not gatehost.stdin( self.gateway[1], msg, True ):
                        # Shell no longer exists
                        self.gateway = None
                else:
                    self.gateway = None
            else:
                # Ignore all data that's not standard ascii
                if len( data ) > 2: continue
                # Check if we're logged in
                if self.account is None:
                    self.login( data )
                else:
                    self.manager( data )

        # Return true since we're still connected
        return True

    # Print out the login banner
    def login_banner( self, msg ):
        # Clear the screen
        self.stdout( ansi_clear( ) )

        # Add newlines on big windows
        if self.size[0] > len( login_banner[0] ):
            self.stdout( "\r\n".join( login_banner ) )
        # Normal size windows
        else:
            self.stdout( "".join( login_banner ) )

        # Print out the welcome message in the correct spot
        self.stdout( ansi_move( login_pos[0] ) +
                     msg[0:47].upper( ) +
                     ansi_move( login_pos[1] ) )

    # Print the gateway manager banner
    def manager_banner( self, host ):
        # Clear the screen
        self.stdout( ansi_clear( ) )

        # Add newlines on big windows
        if self.size[0] > len( manager_banner[0] ):
            self.stdout( "\r\n".join( manager_banner ) )
        # Normal size windows
        else:
            self.stdout( "".join( manager_banner ) )

        # Fill out blanks
        pass

        # Move cursor to the TTY input field
        self.stdout( ansi_move( manager_pos[2] ) )

    # Print out banners that have 1 or less input fields
    def print_banner( self, banner, pos ):
        # Clear the screen
        self.stdout( ansi_clear( ) )

        # Add newlines on big windows
        if self.size[0] > len( banner[0] ):
            self.stdout( "\r\n".join( banner ) )
        # Normal size windows
        else:
            self.stdout( "".join( banner ) )

        # Move cursor to the correct pos
        self.stdout( ansi_move( pos ) )

    # Handle the initial login
    def login( self, data ):
        # Check which promt we're on
        if self.ac_prompt == 0 and data in "lrLR":
            # Are we logging in or registering?
            if data.lower( ) == "l":
                # Acknowlege the login
                self.ac_login = True
                self.stdout( "LOGIN" + ansi_move( login_pos[2] ) )
            else:
                # Acknowlege the register
                self.ac_login = False
                self.stdout( "REGISTER" + ansi_move( login_pos[2] ) )
            # Goto the next prompt
            self.ac_prompt += 1
        # Handle the username prompt
        elif self.ac_prompt == 1:
            # Handle the RETURN key being pressed
            if data.find( "\r" ) >= 0:
                # Was a long enough username entered?
                if len( self.ac_user ) >= 4:
                    # Goto the next prompt
                    self.ac_prompt += 1
                    self.stdout( ansi_move( login_pos[3] ) )
            elif data == "\x7F":
                # Handle backspace
                if len( self.ac_user ) > 0:
                    # Clear the current prompt
                    blank = " " * len( self.ac_user )
                    self.stdout( ansi_move( login_pos[2] ) +
                                 blank +
                                 ansi_move( login_pos[2] ) )
                    self.ac_user = ""
                else:
                    # Goto the previous prompt
                    self.stdout( ansi_move( login_pos[1] ) + "        " + ansi_move( login_pos[1] ) )
                    self.ac_prompt -= 1
            # Make sure data is printable ascii
            elif len( self.ac_user ) < 16 and ord( data ) > 31 and ord( data ) < 127:
                # Add keypress to the prompt
                self.ac_user += data.lower( )
                # Echo the keypress
                self.stdout( data.lower( ) )
        elif self.ac_prompt == 2:
            # Handle the RETURN key being pressed
            if data.find( "\r" ) >= 0:
                # No password was given
                if len( self.ac_pass ) == 0: return
                # Are we logging in?
                if self.ac_login:
                    # Find the requested account
                    for acct in Account.accounts:
                        if acct.username == self.ac_user:
                            if acct.check_pass( self.ac_pass ):
                                # Assign the account to the client
                                self.account = acct
                                # Log the event
                                xlog( "Logged in successfully", self )
                                # Resolve this account's gateway IP
                                gatehost = Host.find_ip( self.account.gateway )
                                # Does this account own a gateway
                                if gatehost is None:
                                    # Print the banner for buying a gateway
                                    self.print_banner( legal_banner, legal_pos )
                                # Is this gateway online
                                elif gatehost.online:
                                    # Print the gateway manager banner
                                    self.manager_banner( gatehost )
                                # Gateway offline
                                else:
                                    # Print the gateway boot banner
                                    self.print_banner( boot_banner, boot_pos )
                            else:
                                # An incorrect password was given
                                self.login_banner( "Incorrect password for requested account" )
                            # We found the right account, so break from loop
                            break
                    else:
                        # Desired account could not be located
                        self.login_banner( "Requested account not found" )

                    # Reset login data
                    self.ac_prompt = 0
                    self.ac_user = ""
                    self.ac_pass = ""
                else:
                    # Goto the next prompt
                    self.print_banner( privacy_banner, privacy_pos )
                    self.ac_prompt += 1
            # Handle backspace
            elif data == "\x7F":
                if len( self.ac_pass ) > 0:
                    # Clear the current prompt
                    blank = " " * len( self.ac_pass )
                    self.stdout( ansi_move( login_pos[3] ) +
                                 blank +
                                 ansi_move( login_pos[3] ) )
                    self.ac_pass = ""
                else:
                    # Goto the previous prompt
                    self.stdout( ansi_move( login_pos[2][0],
                                                   login_pos[2][1] + len( self.ac_user ) ) )
                    self.ac_prompt -= 1
            elif len( self.ac_pass ) < 36 and ord( data ) > 31 and ord( data ) < 127:
                # Add keypress to the prompt
                self.ac_pass += data
                # Echo a star since this is a password
                self.stdout( "*" )
        elif self.ac_prompt == 3 and data in "ynYN":
            # Can we create the account?
            if data.lower( ) == "y":
                # Make sure account doesn't already exist
                for acct in Account.accounts:
                    if acct.username == self.ac_user:
                        # Print error
                        self.login_banner( "Unable to register, username already taken" )
                        break
                else:
                    # Create account and reset login data
                    self.account = Account( self.ac_user, self.ac_pass )
                    # Log the event
                    xlog( "Registered successfully", self )
                    # This user cant have a gateway so ask him to make one
                    self.print_banner( legal_banner, legal_pos )
            else:
                # User did not agree to the terms
                self.login_banner( "New account registration aborted" )

            # Reset login data
            self.ac_prompt = 0
            self.ac_user = ""
            self.ac_pass = ""

    # Handle gateway management
    def manager( self, data ):
        # Resolve this account's gateway IP
        gatehost = Host.find_ip( self.account.gateway )

        # Does this user even own a gateway?
        if gatehost is None:
            # Wait for enter to get pressed
            if data.find( "\r" ) >= 0:
                # Make a new gateway
                nhst = Host( "Gateway_" + str( randint( 100000, 999999 ) ) )
                # Add our account to this gateway
                nhst.add_user( self.account, "root" )
                # Give this account root access
                nhst.join_group( self.account.username, "sudo", "root" )
                # Log the creation
                xlog( "Requested a new gateway: " + nhst.hostname + "@" + nhst.ip, self )
                # Copy the IP address
                self.account.gateway = nhst.ip
                # Print the system boot banner
                self.print_banner( boot_banner, boot_pos )
        # If the gateway is online, pick a TTY
        elif gatehost.online:
            # Did the user hit enter?
            if data.find( "\r" ) >= 0 and len( self.mg_tty ) > 0:
                # Convert tty from string to int
                ntty = int( float( self.mg_tty ) )
                # Reset prompt
                self.mg_tty = ""
                # Is this tty already in use?
                for proc in gatehost.ptbl:
                    # Check if this proc is our TTY
                    if type(proc) is PhreakShell and proc.tty == ntty:
                        # Make sure this Shell isn't in use
                        for cli in self.tserv.clients:
                            if cli.gateway == ( gatehost.ip, proc.pid ):
                                # Found another client logged into our shell
                                break
                        else:
                            # Shell not in use
                            self.stdout( ansi_clear( ) +
                                "*** RECOVERED PREVIOUS SESSION ***\r\n" )
                            # Reset the print delay timer
                            proc.out_last = time.time( )
                            # Output the scrollback buffer
                            self.stdout( proc.out_back )
                            # Connect this client to the shell
                            self.gateway = ( gatehost.ip, proc.pid )
                            break
                        # Shell is already in use, abort
                        break
                # TTY is not in use start a new shell
                else:
                    # Initialize a new shell
                    nsh = PhreakShell( self.account.username,
                        "/usr/" + self.account.username, ntty, self.size )
                    # Start the shell on the new host, and set the gateway
                    self.gateway = gatehost.start( nsh )
            # Did the user press backspace
            elif data == "\x7F" and len( self.mg_tty ) > 0:
                # Strip the last character from the string
                self.mg_tty = self.mg_tty[:-1]
                # Output a backspace
                self.stdout( "\b \b" )
            # Add the numbers to the tty
            elif data in "0123456789" and len( self.mg_tty ) < 4:
                # Append number
                self.mg_tty += data
                # Echo the number back
                self.stdout( data )
        # Gateway is offline, launch the BootMeister
        elif data in "nsNS":
            # Boot the gateway into the correct mode
            gatehost.startup( data.lower( ) == "s" )
            # Launch the gateway manager
            self.manager_banner( gatehost )

    # Fetch output from the gateway shell
    def get_stdout( self ):
        # Check if we're connected to a gateway
        if self.gateway is not None:
            # Get the shell process on the gateway
            gateshell = Host.find_ip( self.gateway[0] ).get_pid( self.gateway[1] )
            if gateshell is not None:
                # Fetch any output from the shell process and transmit it
                data = gateshell.get_stdout( )
                if data: self.stdout( data )
            else:
                # Shell doesn't exist
                self.gateway = None
                # Print the correct banner
                # Resolve gateway from IP
                gateshell = Host.find_ip( self.account.gateway )
                # User no longer owns a gateway
                if gateshell is None:
                    self.print_banner( legal_banner, legal_pos )
                # The gateway is still online
                elif gateshell.online:
                    self.manager_banner( gateshell )
                # The gateway is offline
                else:
                    self.print_banner( boot_banner, boot_pos )

    # Call this to flag this client for termination
    # Returns false if already dead
    def kill( self ):
        # Can't die twice
        if not self.alive: return False
        # Print exit banner
        xlog( "Disconnected from PhreakNET", self )
        self.stdout( ansi_move( self.size[1], 1 ) + "\r\n" )
        self.stdout( "*** Connection to PhreakNET terminated ***\r\n" )
        # Flag client for deletion
        self.alive = False
        # Died successfully
        return True

# The specific client for Telnet connections
class TelnetClient( Client ):

    def __init__ ( self, tserv, conn ):
        # Extract the socket from the conn
        self.sock = conn[0]
        # Send terminal initialization string
        self.sock.send( b"\xFF\xFD\x22\xFF\xFB\x01\xFF\xFB\x03\xFF\xFD\x1F" )
        # Init super last, with the IP and Port
        super( ).__init__( tserv, conn[1] )

    # Send data to the terminal
    def stdout( self, msg ):
        # Encode the message if needed
        if not type( msg ) is bytes: msg = msg.encode( )
        # Send the message to the client as bytes
        try:
            self.sock.send( msg )
        except BrokenPipeError:
            pass


    # Handle input
    def stdin( self ):
        # Stores the keypresses
        msg = []
        # Process all the input
        while True:
            try:
                data = self.sock.recv( 1024 )
                # Check if this socket is still connected
                if not data: return None
                # Process IAC commands
                if self.iac( data ): continue
                # Not an IAC command so decode the data
                data = data.decode( )
                # Nothing left to handle
                msg.append( data )
            # If either of these errors occur, there's no more input to process
            except ( socket.timeout, BlockingIOError ):
                # Return the keypresses
                return msg

    # Process terminal commands sent form the client
    # Returns true if this was a command string
    def iac( self, data ):
        # Robots don't send IAC messages
        self.is_robot = False
        # Process NAWS and record terminal height/width
        np = data.find( b"\xFF\xFA\x1F" )
        if np >= 0:
            # Get the correct offset
            np += 3
            # Set width and height (min of 80x24)
            self.size = ( max( int(data[np    ]) * 256 + int(data[np + 1]), 80 ),
                          max( int(data[np + 2]) * 256 + int(data[np + 3]), 24 ) )

            # Did we just connect?
            # Reprint login prompt
            if self.account is None and self.ac_prompt == 0:
                self.login_banner( "Welcome to PhreakNET" )

            # Update our gateway's size too
            if self.gateway is not None:
                gateshell = Host.find_ip( self.gateway[0] ).get_pid( self.gateway[1] )
                gateshell.set_size( self.size )
            # Was a command string
            return True

        # Not a command String
        return False

    # Handle being killed
    def kill( self ):
        # Close the connection, terminate this client
        if super( ).kill( ): self.sock.close( )

# The specific Client for SSH connections
class SSHClient( Client ):

     def __init__( self ):
         pass
