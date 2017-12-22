#!/usr/bin/env python3

####################################
# Architect & Underground (c) 2017 #
#                                  #
# Run to start Phreaknet Server    #
####################################

# Import all engine files
from init.py import *

import sys

def main( ):
    # Init stuff here
    # Start the client server
    gameserv = net.server( dev, ip )

    # Load all accounts into the system
    Account.load( )

    # Start loop
    while 1:
        # Accept any new connections
        gameserv.accept( )

        # Update all client connections
        clen = len( gameserv.clients )
        for _ in range( clen ):
            # Get the next client to update
            c = gameserv.clients.pop( )
            # See if this client is alive
            if c.alive:
                # Parse any new input
                if c.input( ):
                    # Get the shell process on the gateway
                    gateshell = c.gateway[0].get_pid( c.gateway[1] )
                    if gateshell is not None:
                        # Fetch any output from the shell process
                        gateshell.get_output( )
                    else:
                        # Shell doesn't exist
                        c.gateway = None
                    # Add the client to the end of the queue
                    gameserv.clients.append( c )
                else:
                    # Client not connected to Phreaknet
                    c.kill( )

        # Update all hosts
        for h in Host.hosts:
            # Call this host's update function
            h.update( )

# Run main function, THIS MUST BE THE LAST LINE IN THIS FILE
if __name__ == "__main__": main( )
