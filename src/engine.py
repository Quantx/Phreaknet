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

# The directories needed by phreaknet
phreakdirs = [ "usr", "hst", "dir", "err", "per", "cmp" ]

def main( ):
    # Set the working directory
    os.chdir( ".." )

    # Create all the dirs PhreakNET needs
    for pdir in phreakdirs:
        # Check if the directory doesn't exist
        if not os.path.isdir( pdir ):
            # Make this directory
            os.makedirs( pdir )

    # Load all accounts from disk
    Account.load( )
    # Load all NPCs from disk
    Person.load( )
    # Load all Companies from disk
    Company.load( )

    # Generate all the companies
    Company.generate_companies( )

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
            Server.cur_client = gameserv.clients.pop( 0 )
            try:
                # See if this client is alive
                if Server.cur_client.alive:
                    # Kill any robots, after 5 seconds
                    if Server.cur_client.is_robot and time.time( ) - Server.cur_client.first > 5:
                        Server.cur_client.kill( )
                    # Parse any new input
                    elif Server.cur_client.get_stdin( ):
                        # Fetch out put from the gateway
                        Server.cur_client.get_stdout( )
                        # Add the client to the end of the queue
                        gameserv.clients.append( Server.cur_client )
                    else:
                        # Client not connected to Phreaknet
                        Server.cur_client.kill( )
            # An exception has occured
            except Exception as e:
                # Print it
                traceback.print_exc( )
                # Kill this client
                Server.cur_client.kill( )
        # Reset for next loop
        Server.cur_client = None

        # Update all hosts
        for hst in Host.hosts:
            # Update the global value
            Host.cur_host = hst
            # Call this host's update function
            Host.cur_host.update( )
        # Reset for next loop
        Host.cur_host = None

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
