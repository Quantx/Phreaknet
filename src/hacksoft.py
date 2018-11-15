#!/usr/bin/env python3

####################################
# Architect & Underground (c) 2017 #
#                                  #
# General purpose hacking programs #
####################################

# Import init.py
from init import *

# An homage to Forbin
class Porthack( Program ):

    def __init__( self, user, work, tty, size, origin, params=[] ):
        # Pass parent args along
        super( ).__init__( user, work, tty, size, origin, params )
        # Stores the target host's IP
        self.ph_host = ""

    # Print the startup banner
    def run( self ):
        # Did the user already specify a host?
        if self.params:
            self.ph_host = self.params[0]
            return self.listhost

        self.println( )
        self.println( "    ///////////////////////////////////////" )
        self.println( "   //  Porthack 2.1          by FORBIN  //" )
        self.println( "  ///////////////////////////////////////" )
        self.println( )
        # Prompt the user with Y/N
        return self.readchar( self.pickhost, "Continue? (y/n) ", ["y", "n"] )

    # Pick a host to hack
    def pickhost( self ):
        # User does not want to start Porthack
        if self.rl_line == "n": return self.kill

        return self.readline( self.listhost, "enter host IP: ", self.kill )

    # Connect to host and list all the services
    def listhost( self ):
        # Set the IP if this is our first time calling this func
        if not self.ph_host: self.ph_host = self.rl_line
        # Resolve the host we're hacking
        dhost = self.host.resolve( self.ph_host )
        # Does this host exist?
        if dhost is None:
            # No response, terminate Porthack
            self.error( "no response from host at " + self.ph_host )
            return self.kill
        # Do we already have an account on this host?
        elif dhost.check_user( self.user, "root" ):
            self.error( "account %s already exists on %s"
                % ( self.user, self.ph_host ) )
            return self.kill
        # Print out all currently running services
        self.println( )
        self.println( " port  service     desc" )
        self.println( " ----  -------     ----" )

        return self.readline( self.hackhost, "port to try? ", self.kill )

    # Attempt to hack the host
    def hackhost( self ):
        # Re-resolve the host, it's important we don't keep a permanent ref
        dhost = self.host.resolve( self.ph_host )
        # Does this host exist?
        if dhost is None:
            # No response, terminate Porthack
            self.error( "no response from host at " + self.ph_host )
            return self.kill

        # Convert the readline port to integer
        port = -1
        try:
           port = int( float( self.rl_line ) )
           # Is this a valid port?
           if port < 0 or port > 65535: raise ValueError( "Out of range" )
        except ValueError:
           self.error( "bad port" )
           return self.listhost

        self.println( "attempting buffer overrun against port %d/login..." % port )

        # Check to see if the port was the correct one
        if port == 0:
            # Correct port guessed, add our account
            self.println( "account added successfully" )
            dhost.add_user( self.user, "root" )
            return self.kill
        # Incorrect port guessed, retry
        self.error( "porthack error - buffer overrun exploit failed" )
        self.println( "...try another port" )
        return self.listhost
