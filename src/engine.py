#!/usr/bin/env python3

####################################
# Architect & Underground (c) 2017 #
#                                  #
# Run to start Phreaknet Server    #
####################################

from init import *

import sys

def main( ):
    # Init stuff here
    # Start the client server
    gameserv = net.server( dev, ip )

    # Start loop
    while 1:
        # Accept any new connections
        gameserv.accept( )

        # Update all client connections
        for c in gameserv.clients:
            pass

        # Update all hosts
        for h in Host.hosts:

# Run main function, THIS MUST BE THE LAST LINE IN THIS FILE
if __name__ == "__main__": main( )
