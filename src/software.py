#!/usr/bin/env python3

####################################
# Architect & Underground (c) 2017 #
#                                  #
# General purpose system programs  #
####################################

from init import *

import time
import sys

# A dictionary of aliases for the readchar method
readchar_alias = {
    "\x1B[A" : "up",
    "\x1B[B" : "down",
    "\x1B[C" : "right",
    "\x1B[D" : "left",
}

# A program is a process that is actively controlled by a player
class Program:

    # Stores a list of all programs on Phreaknet
    progtbl = []

    # Dynamically build the program table
    @classmethod
    def build_progtbl( cls ):
        # Loop through every subclass of Program
        for sub in cls.__subclasses__( ):
            # Add this program to the table
            Program.progtbl.append( sub )
            # Iterate through this program's subclasses
            sub.build_progtbl( )

    # Get a program by name
    @staticmethod
    def find_prog( pname ):
        # Iterate through the table
        for prg in Program.progtbl:
            # Do a case insensitive comparison
            if prg.__name__.lower( ) == pname.lower( ):
                # Return the first matching program
                return prg
        # No program with the matching name found
        return None

    # function           | func ..... starting function for the event loop
    # string             | user ..... the owner of this process
    # string             | work ..... this process' current working directory
    # integer            | tty ...... the TTY id this process belongs to
    # (integer, integer) | size ..... the width and height of this TTY
    # (string, integer)  | origin ... the IP and PID of the parent prog
    def __init__( self, func, user, work, tty, size, origin, params=[] ):
        ### Set by the host when the process is assigned ###
        # Host reference
        self.host = None
        # THis prog's PID
        self.pid = -1
        # Function to execute next, None to terminate process
        self.func = func
        # Name of the process
        self.name = type( self ).__name__.lower( )
        # Owner of the process
        self.user = user
        # The current working directory
        self.cwd = work
        # The TTY of this Process, -1 for no TTY
        self.tty = tty
        # Size of the terminal screen ( width, height )
        self.size = size
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
        self.rl_filter = []
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
    # Host    | host ...... a reference to the host this prog is running on
    # string  | data ...... a single keystroke
    # boolean | forward ... should we forward this packet to the input buffer
    def stdin( self, data, forward=False ):
        if not forward:
            # Echo the data along
            self.stdout( data )
        else:
            # See if we need to forward the data or not
            if ( self.destin is not None
            and not self.host.stdout( self.destin, data, True ) ):
                # Destination process does not exist, close connection
                self.destin = None

            # This program is not attached, add it to the buffer
            self.rl_buff.append( data )

    # Simply forward along any stdout data
    def stdout( self, data ):
        self.host.stdout( self.origin, data )

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
            # Look at the first keypress in the buffer
            data = self.rl_buff[0]
            # Check if this packet can be read yet
            if time.time( ) >= self.rl_timer + data[1] + max( data[2], 0 ):
                # Pop the keypress from the buffer
                self.rl_buff.pop( 0 )
                # Update the timer
                self.rl_timer = time.time( )
            else:
                # Not ready to proccess yet
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
                    self.println( "^C" )
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
    # list     | filter ... which chars are allowed to be pressed
    # boolean  | purge .... discard existing input data in the buffer
    def readchar( self, nfunc, prompt="?", filter=[], purge=True ):
        # Clear stdin / stdout
        self.rl_line = ""
        if purge: del self.rl_buff[:]
        # Set filter chars
        self.rl_filter = filter
        # Set function
        self.rl_nfunc = nfunc
        # Set prompt
        self.rl_prompt = prompt
        # Reset timer
        self.rl_timer = time.time( )

        # Print the prompt
        self.printl( self.rl_prompt )
        # return the readchar loop
        return self.readchar_loop

    # Private, do not call
    def readchar_loop( self ):
        # Check if the buffer has data in it
        if self.rl_buff:
            # Look at the first keypress and store it in the output
            data = self.rl_buff[0]
            # Check if it's time to read the next packet
            if time.time( ) >= self.rl_timer + data[1] + max( data[2], 0 ):
                # Remove the data
                self.rl_buff.pop( 0 )
                # Update the timer
                self.rl_timer = time.time( )
            # Not ready to print, keep waiting
            else:
                return self.readchar_loop

            # Extract keypress
            key = data[0]
            # Ensure compatibility between terms
            if key.find( "\r" ) >= 0: key = "\r"
            # Substitute aliases
            if key in readchar_alias: key = readchar_alias[key]

            # Filter out any incorrect key presses
            if self.rl_filter and key not in self.rl_filter:
                return self.readchar_loop

            # Store the keypress
            self.rl_line = key
            # Print the keypress
            self.println( key )
            # Return the next function
            return self.rl_nfunc
        # No data to read
        else:
            # Update timer
            self.rl_timer = time.time( )
            # Continue the loop
            return self.readchar_loop

    # Page data, easy tool for reading long files
    def pager( self, lines, nfunc=None, cat=False ):
        # No next function was provided
        # NOTE: has to be done here, cannot be done in method declaration
        if nfunc is None: nfunc = self.kill
        # If the file's short enough just dump it
        if len( lines ) <= self.size[1] or cat:
            for ln in lines:
                self.println( ln )
            # We're done with this file, so just abort
            return nfunc

        # Store the data lines
        self.pg_lines = lines
        # Reset the pager pos
        self.pg_pos = 0
        # Set the next function to call
        self.pg_nfunc = None

        # Reset the readline output, not strictly nescisary
        self.rl_line = ""

        # Return the pager loop
        return self.pager_loop

    def pager_loop( self ):
        # Scroll up
        if self.rl_line == "up" and self.pg_pos > 0:
            self.pg_pos -= 1
        # Scroll down
        elif self.rl_line == "down" and self.pg_pos + self.size[1] < len( self.pg_lines ):
            self.pg_pos += 1
        # Exit pager
        elif self.rl_line == "q" or self.rl_line == "^C":
            return self.pg_nfunc

        # Print the section of the file
        for i in range( self.pg_pos, self.pg_pos + self.size[1] ):
            self.printl( self.pg_lines[i] )

        # Calculate the precentage of the way through the document
        per = ( self.pg_pos + self.size[1] ) / len( self.pg_lines )
        # Return the readchar prompt
        return self.readchar( self.pager_loop, "--More--(%s)" % per, [ "up", "down" ] )

    # DO NOT call this externally, use the Host class's kill method
    # Recursively kill this program and all it's children
    # Extend this class with any cleanup code you might need
    # TIP: Set this as your rl_afunc, if want ctrl+c to kill the program.
    def kill( self ):
        # Do we have a parent to notify?
        if self.origin is not None:
            # Find our parent's host
            dhost = self.host.resolve( self.origin[0] )
            # Make sure that the host still exists
            if dhost is not None:
                # Find our parent program
                prc = dhost.get_pid( self.origin[1] )
                # Tell our paren't that we're dead
                prc.destin = None
                self.origin = None
        # Return None to signify that we're ready to die
        return None

    # Send message to client
    # Message is sent after delay has elapsed
    def printl( self, msg, delay=0 ):
        # message, print delay, network lag
        self.stdout( ( msg, delay, 0 ) )

    # Send message to client followed by a newline
    def println( self, msg="", delay=0 ):
        # Don't add \r\n if the message fits perfectly
        if len( msg ) == self.size[0]:
            self.printl( msg, delay )
        else:
            self.printl( msg + "\r\n", delay )

    # Send an error message to the client followed by a newline
    def error( self, msg, delay=0 ):
        self.println( "%" + msg, delay )

    # Ring this user's terminal bell
    def beep( self, delay=0 ):
        self.printl( "\a", delay )

    # Print a message with a delay between each char
    def sprintl( self, msg, delay=0 ):
        # Ignore empty messages
        if msg:
            # Send the first char with network lag
            self.stdout( ( msg[0], delay, 0 ) )
            # Send the rest with no lag
            for c in msg[1:]:
                # The -1 1disables system lag
                self.stdout( ( c, delay, -1 ) )

    # Print a message with a delay between each char followed by a newline
    def sprintln( self, msg, delay=0 ):
        self.sprintl( msg + "\r\n", delay )

    # Recursively set the terminal size
    def set_size( self, size ):
        self.size = size
        # Do we have a child program
        if self.destin is not None:
            # Resolve the child program's host
            dhost = self.host.resolve( self.destin[0] )
            # Does this host exist?
            if dhost is not None:
                # Get the child process on this host
                dprg = dhost.get_pid( self.destin[1] )
                # Is the child process still running?
                if dprg is not None:
                    # Set the terminal size on that prog
                    dprg.set_size( size )
                    return
        # Could not contact the child program
        self.destin = None

# The command interpreting shell program
# Extend this to implement unique shells
class Shell( Program ):

    def __init__( self, user, tty, size, origin, params=[] ):
        # Pass parent args along
        super( ).__init__( self.shell, user, "/usr/" + user,
                           tty, size, origin, params )

        # The default prompt for the command line
        self.sh_prompt = ">"
        # The prompt to display when a bad commmand was entered
        self.sh_error = "unknown command"
        # Stores arguments for commands
        self.sh_args = []

        # Default command table stores internal commands
        # function | fn   ... function to be run by this command
        # string   | help ... Message to display in the help menu
        #
        # Usage:
        #
        # "myCmd" : { fn : myCmdFnc, priv : <0-2>, help : "How 2 Use" },
        self.sh_ctbl = {
            "help"  : { "fn" : self.help,  "help" : "help [command]||print this list or info on a specific command", },
            "exit"  : { "fn" : self.kill,  "help" : "exit||terminate connection to this system", },
            "cd"    : { "fn" : self.cdir,  "help" : "cd [path]||change the working directory", },
            "pwd"   : { "fn" : self.pwd,   "help" : "pwd||print the current working directory", },
            "clear" : { "fn" : self.clear, "help" : "clear||clear the terminal screen", },
        }

    # The call to start the command processor
    def shell( self ):
        return self.readline( self.shell_resolve, self.sh_prompt )

    # Resolve the command line input
    def shell_resolve( self ):
        # Split the readline input
        self.sh_args = self.rl_line.split( )
        # Confirm that there's actually text here
        if self.sh_args:
            # Extract the command from the string
            cmd = self.sh_args.pop( 0 )
            # Check if this command is an external program
            pclass = Program.find_prog( cmd )

            if cmd in self.sh_ctbl:
                # Command was an internal command
                return self.sh_ctbl[cmd]["fn"]
            elif pclass is not None:
                # Command is an external program
                prg = pclass( self.user, self.cwd, self.tty, self.size,
                              ("127.0.0.1", self.pid), self.sh_args )
                # Start the new program and set the destination
                self.destin = self.host.start( prg )
            else:
                self.error( self.sh_error )

        return self.shell

    # Print the help screen
    def help( self ):
        # The pager file
        out = []
        # Iterate through the command table
        for cmd in self.sh_ctbl:
            # Split the command from the help message
            hlp = self.sh_ctbl[cmd]["help"].split( "||" )
            # Calculate the correct number of tabs
            tabs = "\t" * int(max( 4 - len( hlp[0] ) / 8, 0 ))
            # Add the help for this command to the output
            out.append( hlp[0] + tabs + hlp[1] )

        out.append( "For more help, try the man program" )

        return self.pager( out, self.shell )

    # Alter the current working directory
    def cdir( self ):
        if self.sh_args:
            # Calculate the correct directory
            sol = os.path.normpath( os.path.join( self.cwd, self.sh_args[0] ) )

            # Is this path a file?
            if os.path.isfile( "dir/" + self.host.hostid + sol ):
                self.error( "Not a directory" )
            # Is this path a directory?
            elif os.path.isdir( "dir/" + self.host.hostid + sol ):
                try:
                    # Do we have read privs for this directory?
                    if self.host.path_priv( "dir/" + self.host.hostid + sol,
                                            self.user, 2 ):
                        # Set our new directory
                        self.cwd = sol
                    else:
                        self.error( "Permission denied" )
                except PhreaknetOSError as e:
                    self.error( e.args[0] )
            # Invalid path
            else:
                self.error( "No such file or directory" )
        else:
            # No path specified, set the working dir to the home dir
            self.cwd = "/usr/" + self.user

        return self.shell

    # Print the current working directory
    def pwd( self ):
        self.println( self.cwd )
        return self.shell

    # Clear the terminal screen
    def clear( self ):
        self.printl( ansi_clear( ) )
        return self.shell

# Starts a Shell session on a remote host
class SSH( Program ):

    def __init__( self, user, work, tty, size, origin, params=[] ):
        # Pass parent args along
        super( ).__init__( self.ssh, user, work, tty, size, origin, params )

    # Connect to a remote host and start a shell
    def ssh( self ):
        if self.params:
            # Resolve the remote host form IP
            dhost = self.host.resolve( self.params[0] )
            # Check if this is a real host
            if dhost is not None:
                # Request a new TTY
                self.ssh_ntty = dhost.request_tty( )
                # Make sure this host has free TTYs
                if self.ssh_ntty is not None:
                    # Check if this host has a hostname
                    hname = self.params[0]
                    if dhost.hostname: hname = dhost.hostname
                    # Get the user's password
                    return self.readline( self.login, self.user + "@"
                        + hname + "'s password: ", self.kill, True )
                else:
                    self.error( "unable to procure free TTY" )
            else:
                self.error( "no response from host at " + self.params[0] )
        else:
            self.error( "usage: ssh <ip address>" )

        # Close the program if there was an error
        return self.kill

    # Check if we can login to this host
    def login( self ):
        # Resolve the remote host form IP
        dhost = self.host.resolve( self.params[0] )
        # Check the password
        if dhost.check_pass( self.user, self.rl_line, "root" ):
            self.println( "Logged in as user " + self.user.upper() )
            # Create a new shell
            nsh = Shell( self.user, self.ssh_ntty, self.size,
                ( self.host.ip, self.pid ) )
            # Start a shell on the remote host, and set the destination
            self.destin = dhost.start( nsh )
        else:
            self.error( "login failed" )
        # Don't store the password past this point
        self.rl_line = ""
        # Close the program once the shell is closed
        return self.kill

# Prints the contents of a directory
class LS( Program ):

    def __init__( self, user, work, tty, size, origin, params=[] ):
        # Pass parent args along
        super( ).__init__( self.list, user, work, tty, size, origin, params )

    def list( self ):
        try:
            # List all the files and directories at the path
            dnames, fnames = self.host.list_dir( self.cwd, self.user )
            # Add the slash to the end
            dnames[:] = [dn + "/" for dn in dnames]
            # Merge the lists
            fnames.extend( dnames )
            # Start the pager
            return self.pager( sorted(fnames) )
        except PhreaknetOSError as e:
            # An in-game error occured, print it out
            self.error( e.args[0] )
            return self.kill

# List the process tabke
class PS( Program ):

    def __init__( self, user, work, tty, size, origin, params=[] ):
        super( ).__init__( self.list, user, work, tty, size, origin, params )

    def list( self ):
        # Print the header
        self.println( "  PID TTY          TIME CMD" )

        # Print out each entry of the PID sorted table
        for prc in sorted(self.host.ptbl, key=lambda x: x.pid):
            # Check which if a TTY is running this process
            vtty = "?"
            if prc.tty >= 0: vtty = prc.tty
            # Print the line
            self.println( "%5s pts/%-4s 00:00:00 %s" % ( prc.pid, vtty, prc.name ) )

        # Terminate the program
        return self.kill

# List information about a host
class Hostname( Program ):

    def __init__( self, user, work, tty, size, origin, params=[] ):
        super( ).__init__( self.info, user, work, tty, size, origin, params )

    def info( self ):
        # Print the hostname
        self.println( self.host.hostname )
        # Does this host have an IP address assigned?
        if self.host.ip:
            self.println( self.host.ip )
        else:
            self.println( "No IP address" )
        # Does this host have a Phone number assigned?
        if self.host.phone:
            self.println( self.host.phone )
        else:
            self.println( "No Phone number" )

        # Only Admins should be able to see this
        acct = Account.find_account( self.user )
        # Make sure account exists and account is Admin
        if acct is not None and acct.is_admin( ):
             self.println( self.host.hostid )

        # Terminate ourselves
        return self.kill

# Terminate a process
class Kill( Program ):

    def __init__( self, user, work, tty, size, origin, params=[] ):
        super( ).__init__( self.murder, user, work, tty, size, origin, params )

    def murder( self ):
        # Did the user specify a PID?
        if self.params:
            # Make sure we were given a job ID
            try:
                # Convert the input to an integer
                cpid = int( float( self.params[0] ) )
                # Make sure this PID is 2 bytes
                if cpid < 0 or cpid > 65535: raise ValueError( "Not 2 bytes" )
                # Run the kill command on this host
                if not self.host.kill( cpid ): self.error( "no such process" )
            except ValueError:
                # We were not given a valid PID
                self.error( "arguments must be process or job IDs" )
        else:
            self.error( "usage: kill <pid>" )

        # We're done here
        return self.kill

# Make a new directory
class Mkdir( Program ):

    def __init__( self, user, work, tty, size, origin, params=[] ):
        # Pass args to parent
        super( ).__init__( self.create, user, work, tty, size, origin, params )

    # Create the directory
    def create( self ):
        # Did the user specify a directory to make
        if self.params:
            # Create the actual directory
            os.mkdir( "dir/" + self.host.hostid + self.cwd + "/" + self.params[0] )
            # Build the inode file with default privs
            with open( "dir/" + self.host.hostid + self.cwd + "/" + self.params[0] + "/.inode", "w" ) as fd:
                fd.write( "rwxrwxr-x " + self.user + " " + self.user )
        else:
            # No params were given
            self.error( "missing operand" )

        return self.kill
