#!/usr/bin/env python3

####################################
# Architect & Underground (c) 2017 #
#                                  #
# Shell and command processing     #
####################################

import init.py

# A process is any piece of software running on a host
class Process:

    # pdata = ( pid, func, name )
    #
    # integer  | pid .... process id given by the system
    # function | func ... function to execute next by the cpu
    # string   | name ... name of the process
    def __init__( self, pid, func, name, user="System" ):
        # Process ID
        self.pid = pid
        # Function to execute next, None to terminate process
        self.func = func
        # Name of the process
        self.name = name
        # Owner of the process
        self.user = user

# A program is a process that is actively controlled by a player
class Program( Process ):

    def __init__( self, pid, func, name, user, origin )
        # Pass parent args along
        super( ).__init__( pid, func, name, user )

        # Stores the location of the program to send/recv data to/from
        # Usage:
        # tuple | origin = ( ip, pid )
        # > string  | ip .... IP address of the host running the program that created this one
        # > integer | pid ... Process ID of the program that created this one
        #
        # Example:
        # Send/recv data to/from a pid on a remote host
        # self.origin = ( "188.32.172.4", 4832 )
        # Send/recv data to/from a pid on this host
        # self.origin = ( "localhost", 5123 )
        # self.origin = ( "127.0.0.1", 3268 )
        self.origin = origin


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

    # Store keystroke sent from the user
    #
    # string | data ... a single keystroke
    def input( self, data ):
        # Sending data is handled here as apposed to within the SSH prog
        # To avoid unfairness with the host update order
        self.rl_buff.append( data )

    # Use readline as follows to request input for the next function
    # Usage:
    # function | nfunc .... function to call after readline returns
    # function | afunc .... function to call if ctrl+c is pressed (Disabled by default)
    # string   | prompt ... prompt to display to the user
    # boolean  | secure ... if true, do not echo user input
    # boolean  | purge .... discard any existing data in the buffer
    #
    # Example:
    #     return sh.readline( myNextFunc, ... )
    #
    # def myNextFunc( sy, sh ):
    #     print( sh.rl_line )
    def readline( self, nfunc, afunc=None, prompt="?", secure=False, purge=True ):
        # Set input / output
        self.rl_line = ""
        if purge: del self.buff[:]
        # Set functions
        self.rl_nfunc = nfunc
        self.rl_afunc = afunc
        # Set additional params
        self.rl_prompt = prompt
        self.rl_secure = secure
        # Return the loop
        return self._readline_loop

    # Private, do not call
    def _readline_loop( self, host ):
        # Process the entire buff
        while self.rl_buff:
            # Pop the first char from the buff
            key = self.rl_buff.pop( )
            # Check if end of user input
            if key.startswith( "\r" ) or key.startswith( "\n" ):
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
        return self._readline_loop;

# The command interpreting shell program
# Extend this to implement unique shells
class Shell( Program ):

    def __init__( self, pid, user, origin ):
        # Pass parent args along
        super( ).__init__( pid, self.shell, "shell", user, origin )

        # The prompt for the command line
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

    def __init__( self, pid, func, name, user, origin ):
        # Pass parent args along
        super( ).__init__( pid, func, name, user, origin )

    # Override the input function to reroute the data to a remote host
    def input( self, data ):
