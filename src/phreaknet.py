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
class PhreakShell( Shell ):

    def __init__( self, user, tty, size, params=[] ):
        # Substitute None for origin since it's not used
        super( ).__init__( user, tty, size, None, params=[] )

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
                    # Get the position of the end of the first line
                    rpos = self.out_back.find( "\n" )
                    # Splice out the first line
                    self.out_back = self.out_back[rpos:]
                # Return data
                return data[0]
            # Not ready to print, keep waiting
            else:
                self.out_buff.insert( 0, data )
        else:
            # Pause print delay, no conn or no data
            self.out_timer = time.time( )
            return ""

    # The intro to play when connecting to the gateway
    def gateway_intro( self ):
        self.printl( ansi_clear( ) )

        self.sprintln( "CONNECTED TO " + self.host.hostname.upper( ), 0.03 )
        self.sprintln( "SYSTEM ................... READY", 0.03 )

        # Return the command shell
        return self.shell
