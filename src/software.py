#!/usr/bin/env python3

####################################
# Architect & Underground (c) 2017 #
#                                  #
# Shell and command processing     #
####################################

from init import *

import time

# Program filenames matched to their Class
progtbl = {}

# A program is a process that is actively controlled by a player
class Program( ):

    def __init__( self, func, name, user, tty, origin, params=[] ):
        ### Set by the host when the process is assigned ###
        # Host reference and PID
        self.hpid = None
        # Function to execute next, None to terminate process
        self.func = func
        # Name of the process
        self.name = name
        # Owner of the process
        self.user = user
        # Processes don't run on ttys
        self.tty = tty
        # Additional Parameters
        self.params = params
        # Time started
        self.started = time.time( )

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
        # Buffer of keystrokes (array of tuples): ( data, delay, lag )
        # NOTE: Some keystroks are multiple chars
        self.rl_buff = []
        # readline output
        self.rl_line = ""
        # Cursor position
        self.rl_cpos = 0
        # The input read timer
        self.rl_timer = time.time( )
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

        ### Storage for the Pager utility ###
        # Array of strings to display
        self.pg_lines = []
        # Which line the pager is on
        self.pg_pos = 0
        # Pager next function
        self.pg_nfunc = None

    # Store keystroke sent from a different proccess
    #
    # Host    | host ... a reference to the host this prog is running on
    # string  | data ... a single keystroke
    # boolean | echo ... should we forward this packet to stdout
    def stdin( self, data, echo=False ):
        if not echo:
            # Echo the data along
            self.stdout( data )
        else:
            # See if we need to forward the data or not
            if self.destin is None:
                # This program is not attached, add it to the buffer
                self.rl_buff.append( data )
            else:
                # Forward data to process
                if not self.hpid[0].stdout( self.destin, data, True ):
                    # If the destination process does not exist, close connection
                    self.destin = None

    # Simply forward along any stdout data
    def stdout( self, data ):
        self.hpid[0].stdout( self.origin, data )

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
    # def myNextFunc( self ):
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
        # Reset the input timer
        self.rl_timer = time.time( )

        # Print the prompt
        self.printl( self.rl_prompt )
        # Return the loop
        return self.readline_loop

    # Private, do not call
    def readline_loop( self ):
        ### Process packet ###
        # Process the entire buff
        while self.rl_buff:
            # Pop the first char from the buff
            data = self.rl_buff.pop( 0 )
            # Check if this packet can be read yet
            if time.time( ) >= self.rl_timer + data[1] + max( data[2], 0 ):
                # Update the timer
                self.rl_timer = time.time( )
            else:
                # Not ready to proccess yet
                self.rl_buff.insert( 0, data )
                return self.readline_loop
            # Extract the keypress
            key = data[0]
            ### Process keypress ###
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

        # Check if we processed any data
        if not self.rl_buff:
            # Reset timer
            self.rl_timer = time.time( )

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
        # Reset timer
        self.rl_timer = time.time( )
        # return the readchar loop
        return self.readchar_loop

    # Private, do not call
    def readchar_loop( self ):
        # Check if the buffer has data in it
        if self.rl_buff:
            # Pop one keypress and store it in the output
            data = self.rl_buff.pop( 0 )
            # Check if it's time to print
            if time.time( ) >= self.out_timer + data[1] + max( data[2], 0 ):
                # Update the timer
                self.rl_timer = time.time( )
            # Not ready to print, keep waiting
            else:
                # Put the data back
                self.rl_buff.insert( 0, data )
                return self.readchar_loop

            # Filter out any incorrect key presses
            if len( self.rl_filter ) > 0 and data[0] not in self.rl_filter:
                return self.readchar_loop

            # Store the keypress
            self.rl_line = data[0]
            # Return the next function
            return self.rl_nfunc
        # No data to read
        else:
            # Update timer
            self.rl_timer = time.time( )
            # Continue the loop
            return self.readchar_loop

    # Page data, easy too for reading long files
    def pager( self, lines, nfunc ):
        # Store the data lines
        self.pg_lines = lines
        # Reset the pager pos
        self.pg_pos = 0
        # Set the next function to call
        self.pg_nfunc = None
        # Return the pager loop
        return self.pager_loop

    def pager_loop( self ):
        pass

    # Recursively kill this program and all it's children
    # Extend this class with any cleanup code you might need
    # TIP: Set this as your rl_afunc, if want ctrl+c to kill the program.
    def kill( self ):
        # Tell our child to kill itself
        if self.destin is not None:
            self.hpid[0].resolve( self.destin[0] ).kill( self.destin[1] )
        # Call parent function to terminate self
        self.func = None
        return None

    # Send message to client
    # Message is sent after delay has elapsed
    def printl( self, msg, delay=0 ):
        # Ignore empty messages
        if msg:
            # message, print delay, network lag
            self.stdout( ( msg, delay, 0 ) )

    # Send message to client followed by a newline
    def println( self, msg="", delay=0 ):
        self.printl( msg + "\r\n", delay )

    # Send an error message to the client followed by a newline
    def error( self, msg, delay=0 ):
        self.println( "%%" + msg, delay )

    # Print a message with a delay between each char
    def sprintl( self, msg, delay=0 ):
        # Ignore empty messages
        if msg:
            # Send the first char with network lag
            self.stdout( ( msg[0], delay, 0 ) )
            # Send the rest with no lag
            for c in msg[1:]:
                # The -1 disables system lag
                self.stdout( ( c, delay, -1 ) )

    # Print a message with a delay between each char followed by a newline
    def sprintln( self, msg, delay=0 ):
        self.sprintl( msg + "\r\n", delay )

# The command interpreting shell program
# Extend this to implement unique shells
class Shell( Program ):

    def __init__( self, user, tty, origin, params=[] ):
        # Pass parent args along
        super( ).__init__( self.shell, "shell", user, tty, origin, params )

        # The default prompt for the command line
        self.sh_prompt = ">"
        # Stores arguments for commands
        self.sh_args = []
        # Stores the current working directory
        self.sh_cwd = "/usr/" + self.user

        # Default command table, commands common to all hosts
        # Program  | prg  ... Program to be run by this command
        # integer  | priv ... 0 = Guest, 1 = User, 2 = Root
        # string   | help ... Message to display in the help menu
        #
        # Usage:
        #
        # "myCmd" : { prg : myProgObj, priv : <0-2>, help : "How 2 Use" },
        self.sh_ctbl = {
            "exit" : { "prg" : self.kill, "priv" : 0, "help" : "exit||Terminate connection to this system" },
            "run"  : { "prg" : self.run,  "priv" : 1, "help" : "run <file>||Run an executable program on disk", },
            "ssh"  : { "prg" : self.ssh,  "priv" : 1, "help" : "ssh <ip address>||Start a Shell session on a remote host", },
        }

    # The call to start the command processor
    def shell( self ):
        return self.readline( self.shell_resolve, self.sh_prompt )

    # Resolve the command line input
    def shell_resolve( self ):
        # Split the readline input
        self.sh_args = self.rl_line.split( )
        # Extract the command from the string
        cmd = self.sh_args.pop( 0 )

        if cmd in self.sh_ctbl:
            if "fn" in self.sh_ctbl[cmd]:
                # Command is an internal function
                return self.sh_ctbl[cmd]["fn"]
            else:
                # Command is an external program
                prg = self.sh_ctbl[cmd]["prg"]( self.user, self.tty, self.hpid, self.sh_args )
                # Start the new program and set the destination
                self.destin = self.hpid[0].start( prg )
                # Return a shell for when we quit
                return self.shell
        else:
            self.error( "unknown command" )

        return self.shell

    # The run command
    def run( self ):
        pass

progtbl["shell"] = Shell

# Starts a Shell session on a remote host
class SSH( Program ):

    def __init__( self, user, tty, origin, params=[] ):
        # Pass parent args along
        super( ).__init__( self.ssh, "ssh", user, tty, origin, params )

    # Connect to a remote host and start a shell
    def ssh( self ):
        if self.sh_args:
            # Resolve the remote host form IP
            dhost = self.hpid[0].resolve( self.sh_args[0] )
            # Check if this is a real host
            if dhost is not None:
                # Request a new TTY
                ntty = dhost.request_tty( )
                # Make sure this host has free TTYs
                if ntty is not None:
                    # Create a new Shell
                    nsh = Shell( self.user, ntty, self.hpid )
                    # Start a shell on the remote host, and set the destination
                    self.destin = dhost.start( nsh )
                else:
                    self.error( "unable to procure free TTY" )
            else:
                self.error( "no response from host at " + self.rl_line )
        else:
            self.error( "usage: ssh <ip address>" )

        # Close the program once the shell is closed
        return self.kill

progtbl["ssh"] = SSH
