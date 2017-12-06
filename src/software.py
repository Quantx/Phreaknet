#!/usr/bin/env python3

####################################
# Architect & Underground (c) 2017 #
#                                  #
# Shell and command processing     #
####################################

import init.py

import time

# A process is any piece of software running on a host
class Process:

    # pdata = ( pid, func, name )
    #
    # integer  | pid .... process id given by the system
    # function | func ... function to execute next by the cpu
    # string   | name ... name of the process
    def __init__( self, pid, func, name, user="System", params=[] ):
        # Process ID
        self.pid = pid
        # Function to execute next, None to terminate process
        self.func = func
        # Name of the process
        self.name = name
        # Owner of the process
        self.user = user
        # Additional Parameters
        self.params = params
        # Time started
        self.started = time.time( )

    # Kill this process
    # Can be called remotely or returned from an proc loop
    def kill( self ):
        self.func = None
        return None

# A program is a process that is actively controlled by a player
class Program( Process ):

    def __init__( self, pid, func, name, user, origin, params=[] )
        # Pass parent args along
        super( ).__init__( pid, func, name, user, params )

        # Stores the location of the program to send/recv data to/from
        # Basically the stdin for this program
        # Usage:
        # tuple | origin = ( ip, pid )
        # > string  | ip .... IP address of the host running the program that created this one
        # > integer | pid ... Process ID of the program that created this one
        #
        # Example:
        # Send/recv data to/from a pid on a remote host
        # self.origin = ( hostRef, 4832 )
        # Send/recv data to/from a pid on this host
        # self.origin = ( thisHostRef, 5123 )
        self.origin = origin
        # Same contents as self.origin
        # Stores the host and process to which data is sent
        # Basically the stdout for this program
        self.destin = None

        ### Storage for the Readline utility ###
        # Prompt for the readline
        self.rl_prompt = ""
        # Buffer of keystrokes (array of strings)
        # NOTE: Some keystroks are multiple chars
        self.rl_buff = []
        # readline output
        self.rl_line = ""
        # Cursor position
        self.rl_cpos = 0
        # Readline next function
        self.rl_nfunc = None
        # Readline abort (ctrl+c) function
        self.rl_afunc = None
        # Hide characters or not
        self.rl_secure = False
        # Strip leading / trailing whitespace
        self.rl_strip = True

    # Store keystroke sent from a different proccess
    #
    # string | data ... a single keystroke
    def input( self, data ):
        # See if we need to forward the data or not
        if self.destin is None:
            # This program is not attached, add it to the buffer
            self.rl_buff.append( data )
        else:
            # Forward data to process
            if not self.destin[0].input( self.destin[1], data ):
                # If the destination process does not exist, close connection
                self.destin = None

    # Send data to a different process
    def output( self, data ):
         return self.origin[0].output( self.origin[1], data )

    # Use readline as follows to request input for the next function
    # Usage:
    # function | nfunc .... function to call after readline returns
    # string   | prompt ... prompt to display to the user
    # function | afunc .... function to call if ctrl+c is pressed
    # boolean  | secure ... if true, do not echo user input
    # boolean  | purge .... discard any existing data in the buffer
    # boolean  | strip .... strip leading and trailing text
    #
    # Example:
    #     return self.readline( myNextFunc, ... )
    #
    # def myNextFunc( host ):
    #     print( self.rl_line )
    def readline( self, nfunc, prompt="?", afunc=None, secure=False, purge=True, strip=True ):
        # Set input / output
        self.rl_line = ""
        if purge: del self.buff[:]
        # Set functions
        self.rl_nfunc = nfunc
        self.rl_afunc = afunc
        # Set additional params
        self.rl_prompt = prompt
        self.rl_secure = secure
        self.rl_strip = strip
        # Return the loop
        return self._readline_loop

    # Private, do not call
    def readline_loop( self, host ):
        # Process the entire buff
        while self.rl_buff:
            # Pop the first char from the buff
            key = self.rl_buff.pop( )
            # Check if end of user input
            if key.startswith( "\r" ) or key.startswith( "\n" ):
                # Strip whitespace from text
                if self.rl_strip: self.rl_line.strip( )
                return self.rl_nfunc
            # Handle user interrupts
            elif key == "^C":
                # Eat the CTRL+C
                if self.rl_afunc is not None:
                    return self.rl_afunc
            # Backspace key pressed
            elif ( key == "\b" or key == "^H" ) and self.rl_cpos > 0:
                self.rl_line = self.rl_line[:(self.rl_cpos - 1)] + self.rl_line[self.rl_cpos:]
                self.rl_cpos -= 1
            # Delete key pressed
            elif key == "BACKSPACE":
                self.rl_line = self.rl_line[:self.rl_cpos] + self.rl_line[(self.rl_cpos + 1):]
            # Add char to the line if enough room
            elif len( self.rl_line ) < 256:
                self.rl_line += key
                self.rl_cpos += 1
        return self._readline_loop

    # Recursively kill this program and all it's children
    # Can be called remotely or returned from an prog loop
    # Extend this class with any cleanup code you might need
    # TIP: Set this as your rl_afunc, if want ctrl+c to kill
    # the program.
    def kill( self ):
        # Tell our child to kill itself
        if self.destin is not None:
            self.destin[0].kill( self.destin[1] )
        # Call parent function to terminate self
        return super( ).method( )

    # Send message to client
    # Message is sent after delay has elapsed
    def printl( self, msg, delay=0 ):
        # data = ( message, print delay, network lag )
        data = ( msg, delay, 0 )
        self.origin[0].output( self.origin[1], data )

    # Send message to client followed by a newline
    def println( self, msg="", delay=0 ):
        self.printl( msg + "\r\n", delay )

# The command interpreting shell program
# Extend this to implement unique shells
class Shell( Program ):

    def __init__( self, pid, user, origin, params=[] ):
        # Pass parent args along
        super( ).__init__( pid, self.shell, "shell", user, origin, params )

        # The default prompt for the command line
        self.sh_prompt = "@"

        # Default command table, commands common to all hosts
        # function | fn   ... Function to call when command executed
        # integer  | priv ... 0 = Guest, 1 = User, 2 = Root
        # string   | help ... Message to display in the help menu
        #
        # Usage:
        #
        # "myCmd" : { fn : myCmdFunc, priv : <0-2>, help : "How 2 Use" },
        self.sh_ctbl = {
            "exit" : { fn : None, priv : 0, help : "Terminate connection to thi$
        }

    # The call to start the command processor
    def shell( self, host ):
        return readline( self.shell_resolve, self.sh_prompt )

    # The run command
    def run( self, host ):
        pass

class SSH( Program ):

    def __init__( self, pid, user, origin, params=[] ):
        # Pass parent args along
        super( ).__init__( pid, self.ssh, "SSH", user, origin, params )

    def ssh( self, host ):
        # Was the host defined as an arg?
        if self.params:
            # Set the readline to the host
            self.rl_line = self.params[0]
            # Return the resolve function
            return self.ssh_resolve

        return self.readline( self.ssh_resolve, "Remote host IP? " )

    def ssh_resolve( self, host ):
        # Resolve the remote host form IP
        dhost = host.resolve_host( self.rl_line )
        # Check if this is a real host
        if dhost is not None:
            # Get a free process id from that host
            npid = dhost.get_npid( )
            # Start a shell on the remote host
            dhost.start_process( Shell( npid, self.user, ( host, self.pid ) ) )
            # Forward any input to that shell
            self.destin = ( dhost, npid )
        else:
            # Send an error message
            self.println( "%%no response from host at " + self.rl_line )

        return None

# This is a special shell, used on Phreaknet gateways
# It bridges the I/O of clients with the I/O of programs
# DO NOT use this shell on any host except Phreaknet gateways
class PhreakShell( Shell ):

    def __init__( self, pid, user, origin, params=[] ):
        super( ).__init__( pid, user, origin, params )
        # Which conn is connected to this shell
        # Used in place of origin, to bridge the connection
        self.out_tty = None
        # Stores a queue of (string, delay, lag) to be sent to clients
        self.out_buff = []
        # Stores the time the last message was sent
        self.out_last = time.time( )

    # Override parrent function
    # Cache all incoming data until needed by the client
    def output( self, data ):
        self.out_last.append( data )

    # Called by the conn update cycle to fetch any outgoing data
    def get_output( self ):
        # Confirm there's a conn connected to this shell
        if self.out_buff and self.out_tty is not None:
            # Check if the print delay has expired
            b = self.out_buff.pop( )
            # Check if it's time to print
            if time.time( ) >= self.out_last > b[1] + b[2]:
                # Update the next print statement with the current time
                self.out_last = time.time( )
                # Return data
                return b[0]
            # Not ready to print, keep waiting
            else:
                self.out_buff.push( b )
        else:
            # Pause print delay, no conn or no data
            self.out_last = time.time( )
            return ""
