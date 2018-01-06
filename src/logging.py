#!/usr/bin/env python3

####################################
# Architect & Underground (c) 2017 #
#                                  #
# Log data on disk                 #
####################################

# Import init
from init import *

# Dependancies
import sys
import time

# Log a server action
def xlog( msg ):
    # Date/Time (24 hour) format: [MM/DD/YYYY|HH:MM:SS]
    out = time.strftime( "[%m/%d/%Y|%H:%M:%S]" ) + msg + "\r\n"
    sys.stdout.write( out )

# Log a client action
# The clit varaible should be of type Client
def clog( cli, msg ):
    # Assume this user isn't logged in
    username = "Guest"
    # Find this user's associated account
    if cli.account is not None:
        username = cli.account.username
    # Log to server
    xlog( "[" + cli.ip + ":" + str( cli.port ) + "|" + username + "]" + msg )
