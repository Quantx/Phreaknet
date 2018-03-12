#!/usr/bin/env python3

####################################
# Architect & Underground (c) 2017 #
#                                  #
# Run to start Phreaknet Server    #
####################################

# Import all engine files
from init import *

import sys
import os

def main( ):
    # Set the working directory
    os.chdir( ".." )

    # Create the user directory if it doesn't exist
    if not os.path.exists( "usr" ):
        os.makedirs( "usr" )
    # Load all accounts from disk
    Account.load( )

    # Create the host directory if it doesn't exist
    if not os.path.exists( "hst" ):
        os.makedirs( "hst" )

    # Build the program table
    Program.build_progtbl( )
    # Dump the program table
    # for p in Program.progtbl: print( p.__name__ )

    # Load all hosts from disk
    Host.load( )

    # Init stuff here
    # Start the client server
    gameserv = Server( True )

    # Load all accounts into the system
    Account.load( )

    lastloop = time.time( )

    # Start loop
    while 1:
        # Accept any new connections
        gameserv.accept( )

        # Update all client connections
        clen = len( gameserv.clients )
        # Client update cycle: Recieve Input, Send Output
        for _ in range( clen ):
            # Get the next client to update
            c = gameserv.clients.pop( 0 )
            # See if this client is alive
            if c.alive:
                # Parse any new input
                if c.get_stdin( ):
                    # Fetch out put from the gateway
                    c.get_stdout( )
                    # Add the client to the end of the queue
                    gameserv.clients.append( c )
                else:
                    # Client not connected to Phreaknet
                    c.kill( )

        # Update all hosts
        for h in Host.hosts:
            # Call this host's update function
            h.update( )

        # Did that take too long
        if time.time( ) - lastloop > 0.1:
            xlog( "That took too long: %s" % ( time.time() - lastloop ) )

        lastloop = time.time( )

# Run main function, THIS MUST BE LAST IN THIS FILE
if __name__ == "__main__":
    try:
        main( )
    except KeyboardInterrupt:
        # Quit the program
        sys.exit( 0 )
