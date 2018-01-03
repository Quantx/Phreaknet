#!/usr/bin/env python3

####################################
# Architect & Underground (c) 2017 #
#                                  #
# Shell and command processing     #
####################################

from init import *

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
    def kill( self, host=None ):
        self.func = None
        return None

# A program is a process that is actively controlled by a player
class Program( Process ):

    def __init__( self, pid, func, name, user, origin, params=[] ):
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
        # self.origin = ( IPaddr, 4832 )
        # Send/recv data to/from a pid on this host
        # self.origin = ( IPaddr, 5123 )
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
        # Used by readchar, filters out all chars except...
        self.rl_filter = ""
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
    def stdin( self, data ):
        # See if we need to forward the data or not
        if self.destin is None:
            # This program is not attached, add it to the buffer
            self.rl_buff.append( data )
        else:
            # Forward data to process
            if not Host.resolve( self.destin[0] ).stdin( self.destin[1], data ):
                # If the destination process does not exist, close connection
                self.destin = None

    # Send data to a different process
    def stdout( self, data, delay=0 ):
         Host.resolve( self.origin[0] ).stdout( self.origin[1], data )

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
        # Purge stdin / stdout
        self.rl_line = ""
        if purge: del self.rl_buff[:]
        # Set functions
        self.rl_nfunc = nfunc
        self.rl_afunc = afunc
        # Set additional params
        self.rl_prompt = prompt
        self.rl_secure = secure
        self.rl_strip = strip
        # Reset the cursor pointer
        self.rl_cpos = 0
        # Return the loop
        return self.readline_loop

    # Private, do not call
    def readline_loop( self, host ):
        # Process the entire buff
        while self.rl_buff:
            # Pop the first char from the buff
            key = self.rl_buff.pop( )
            # Check if end of user input
            if key.find( "\r" ) >= 0:
                # Strip whitespace from text
                if self.rl_strip: self.rl_line.strip( )
                self.println( )
                return self.rl_nfunc
            # Handle user interrupts
            elif key == "^C":
                # Eat the CTRL+C
                if self.rl_afunc is not None:
                    return self.rl_afunc
            # Backspace key pressed
            elif ( key == "^H" or key == "\x7F" ) and self.rl_cpos > 0:
                self.rl_line = self.rl_line[:(self.rl_cpos - 1)] + self.rl_line[self.rl_cpos:]
                self.rl_cpos -= 1
                # Output a backspace
                self.printl( "\b \b" )
            # Delete key pressed
            elif key == "[DELETE]":
                self.rl_line = self.rl_line[:self.rl_cpos] + self.rl_line[(self.rl_cpos + 1):]
            # Make sure they keypress is printable ASCII
            elif len( key ) == 1 and ord( key ) > 31 and ord( key ) < 127:
                # Make sure that the output isn't too long
                if len( self.rl_line ) < 100:
                    # Check if we're in secure mode
                    if self.rl_secure:
                        # Echo a star
                        self.printl( "*" )
                    else:
                        # Echo the key
                        self.printl( key )
                    # Add the key to the output
                    self.rl_line += key
                    self.rl_cpos += 1
        return self.readline_loop

    # Get exactly one char from the client
    # function | nfunc .... the function to execute after a key is pressed
    # string   | prompt ... the prompt to display to the client
    # boolean  | purge .... discard existing input data in the buffer
    def readchar( self, nfunc, prompt="?", filter="", purge=True ):
        # Clear stdin / stdout
        self.rl_buff = ""
        if purge: del self.rl_buff[:]
        # Set filter chars
        self.rl_filter = filter
        # Set function
        self.rl_nfunc = nfunc
        # Set prompt
        self.rl_prompt = prompt
        # return the readchar loop
        return self.readchar_loop

    # Private, do not call
    def readchar_loop( self, host ):
        # Check if the buffer has data in it
        if self.rl_buff:
            # Pop one keypress and store it in the output
            key = self.rl_buff.pop( )
            # Filter out any incorrect key presses
            if len( self.rl_filter ) > 0 and key not in self.rl_filter:
                return self.readchar_loop
            self.rl_line = key
            # Return the next function
            return self.rl_nfunc
        else:
            # Continue the loop
            return self.readchar_loop

    # Recursively kill this program and all it's children
    # Can be called remotely or returned from an prog loop
    # Extend this class with any cleanup code you might need
    # TIP: Set this as your rl_afunc, if want ctrl+c to kill
    # the program.
    def kill( self, host=None ):
        # Tell our child to kill itself
        if self.destin is not None:
            Host.resolve( self.destin[0] ).kill( self.destin[1] )
        # Call parent function to terminate self
        return super( ).kill( )

    # Send message to client
    # Message is sent after delay has elapsed
    def printl( self, msg, delay=0 ):
        # message, print delay, network lag
        self.stdout( ( msg, delay, 0 ) )

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
        self.sh_prompt = ">"

        # Default command table, commands common to all hosts
        # function | fn   ... Function to call when command executed
        # integer  | priv ... 0 = Guest, 1 = User, 2 = Root
        # string   | help ... Message to display in the help menu
        #
        # Usage:
        #
        # "myCmd" : { fn : myCmdFunc, priv : <0-2>, help : "How 2 Use" },
        self.sh_ctbl = {
            "exit" : { "fn" : self.kill, "priv" : 0, "help" : "Terminate connection to this system" },
        }

    # The call to start the command processor
    def shell( self, host ):
        return self.readline( self.shell_resolve, self.sh_prompt )

    # Resolve the command line input
    def shell_resolve( self, host ):
        pass

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
        dhost = Host.resolve( self.rl_line )
        # Check if this is a real host
        if dhost is not None:
            # Get a free process id from that host
            npid = dhost.get_npid( )
            # Start a shell on the remote host
            dhost.start( Shell( npid, self.user, ( host, self.pid ) ) )
            # Forward any input to that shell
            self.destin = ( dhost, npid )
        else:
            # Send an error message
            self.println( "%%no response from host at " + self.rl_line )

        return None
