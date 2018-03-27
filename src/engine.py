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
    if not os.path.exists( "usr" ): os.makedirs( "usr" )
    # Load all accounts from disk
    Account.load( )

    # Create the host directory if it doesn't exist
    if not os.path.exists( "hst" ): os.makedirs( "hst" )

    # Create the hostdir directory if it doesn't exist
    if not os.path.exists( "dir" ): os.makedirs( "dir" )

    # Create the err directory for storing error reports
    if not os.path.exists( "err" ): os.makedirs( "err" )

    # Build the program table
    Program.build_progtbl( )

    # Load all hosts from disk
    Host.load( )

    # Init stuff here
    # Start the client server
    gameserv = Server( True )

    # Load all accounts into the system
    Account.load( )

    # Stores time between loops
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
            cur_client = gameserv.clients.pop( 0 )
            try:
                # See if this client is alive
                if cur_client.alive:
                    # Kill any robots, after 5 seconds
                    if cur_client.is_robot and time.time( ) - cur_client.first > 5:
                        cur_client.kill( )
                    # Parse any new input
                    elif cur_client.get_stdin( ):
                        # Fetch out put from the gateway
                        cur_client.get_stdout( )
                        # Add the client to the end of the queue
                        gameserv.clients.append( cur_client )
                    else:
                        # Client not connected to Phreaknet
                        cur_client.kill( )
            # An exception has occured
            except Exception as e:
                # Print it
                traceback.print_exec( )
                # Kill this client
                cur_client.kill( )
        # Reset for next loop
        cur_client = None

        # Update all hosts
        for cur_host in Host.hosts:
            # Call this host's update function
            cur_host.update( )
        # Reset for next loop
        cur_host = None

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
