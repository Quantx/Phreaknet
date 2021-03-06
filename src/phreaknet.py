#!/usr/bin/env python3

####################################
# Architect & Underground (c) 2017 #
#                                  #
# Phreaknet Host related things    #
####################################

from init import *

# This is a special shell, used on Phreaknet gateways
# It bridges the I/O of clients with the I/O of programs
# DO NOT use this shell on any host except Phreaknet gateways
class PhreakShell( Qash ):

    def __init__( self, user, work, tty, size, params=[] ):
        # Substitute None for origin since it's not used
        super( ).__init__( user, work, tty, size, None, params=[] )

        # Disguise ourself as a normal shell
        self.name = "qash"

        # Use the @ symbol for a prompt
        self.sh_prompt = "@"
        # Set a more usefull error prompt
        self.sh_error = "unknown command - try 'help' without quotes"

        # Stores a queue of (string, delay, lag) to be sent to clients
        self.out_buff = []
        # Stores the scrollback for this client
        self.out_back = ""
        # NOTE: set this value back to time.time( ) when a client reconnects
        # Stores the time the last message was sent
        self.out_timer = time.time( )

        # Set our custom starting function
        self.func = self.gateway_intro

    # Override parrent function
    # Cache all incoming data until needed by the client
    def stdout( self, data ):
        self.out_buff.append( data )

    # Called by the conn update cycle to fetch any outgoing data
    def get_stdout( self ):
        # Confirm there's a conn connected to this shell
        if self.out_buff:
            # Check if the print delay has expired
            data = self.out_buff.pop( 0 )
            # Check if it's time to print
            if time.time( ) >= self.out_timer + data[1] + max( data[2], 0 ):
                # Update the timer
                self.out_timer = time.time( )
                # Update the scrollback
                self.out_back += data[0]
                # Cull out the scrollback
                while self.out_back.count( "\n" ) > self.size[1]:
                    # Remove the first line in the buffer
                    self.out_back = self.out_back.split("\n", 1)[-1]
                # Return data
                return data[0]
            # Not ready to print, keep waiting
            else:
                self.out_buff.insert( 0, data )
        else:
            # Pause print delay, no conn or no data
            self.out_timer = time.time( )
            return ""

    # Print a more useful help screen
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
        # Add this message
        out.append( "For more help, try the man program" )

        return self.pager( out, self.run )

    # The intro to play when connecting to the gateway
    def gateway_intro( self ):
        self.printl( ansi_clear( ) )

        self.sprintln( "CONNECTED TO " + self.host.hostname.upper( ), 0.03 )
        self.sprintln( "SYSTEM ................... READY", 0.03 )
        # Let the user know they're in safe mode
        if self.host.safemode:
            self.println( "*** SAFEMODE ENGAGED, NO NETWORK CONNECTION ***", 0.2 )

        # Return the command shell
        return self.run

# An admin control shell for PhreakNET
class PhreakAdmin( Shell ):

    def __init__( self, *args, **kwargs ):
        # Call super
        super( ).__init__( *args, **kwargs )

        # Disguise ourself as a normal shell
        self.name = "shell"

        # Use the @ symbol for a prompt
        self.sh_prompt = "admin shell>"

        # Overwrite the cmd table
        self.sh_ctbl.update({
            "savedb" : { "fn" : self.savedb, "help" : "savedb||save the PhreakNET database", },
        })

    # Check if we're a valid admin
    def run( self ):
        # Only admins can run this
        acct = Account.find_account( self.user )
        if acct is None or not acct.is_admin( ):
            self.error( "access restricted to PhreakDEVs" )
            return self.kill
        # Start the shell
        return self.readline( self.shell_resolve, self.sh_prompt )

    # Save the PhreakNET database
    def savedb( self ):
        # Set this in advance so that we don't save twice
        self.func = self.run

        # Save accounts
        cnt = Account.save( )
        self.println( "Saved %s accounts" % cnt )
        # Save companies
        cnt = Company.save( )
        self.println( "Saved %s companies" % cnt )
        # Save hosts
        cnt = Host.save( )
        self.println( "Saved %s hosts" % cnt )

        # We're done here
        return self.run
