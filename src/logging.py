#!/usr/bin/env python3

####################################
# Architect & Underground (c) 2017 #
#                                  #
# Log data on disk                 #
####################################

# Import init.py
import init.py

# Dependancies
import sys
import time

# Log a server action
def server( msg ):
    # Date/Time (24 hour) format: [MM/DD/YYYY|HH:MM:SS]
    sys.stdout.write( time.strftime( "[%m/%d/%Y|%H:%M:%S]" ) + msg + "\n" )

# Log a client action
# The clit varaible should be of type Client
def client( cli, msg ):
    server( "[" + cli.ip + ":" + cli.port + "|" + cli.acct + "]" + msg )
