#!/usr/bin/env python3

####################################
# Architect & Underground (c) 2017 #
#                                  #
# Terminal output formating        #
####################################

# Import init.py
from init import *

# Dependancies
import sys
import time

# Log a server action
def xlog( msg, cli=None, hst=None ):
    # Date/Time (24 hour) format: [MM/DD/YYYY|HH:MM:SS]
    out = time.strftime( "[%m/%d/%Y|%H:%M:%S]" )

    # Was a Client object specified?
    if cli is not None:
        # Assume this user isn't logged in
        username = "Guest"
        # Find this user's associated account
        if cli.account is not None:
            username = cli.account.username
        # Append to output
        out += "[" + cli.ip + ":" + str( cli.port ) + "|" + username + "]"
    # Was a host specified?
    if hst is not None:
       # Add the hostname
       out += "[" + hst.hostname
       # Add the IP
       if self.ip: out += "|" + hst.ip
       # Add the Phone number
       if self.ip: out += "|" + hst.phone
       # Add the closing bracket
       out += "]"

    # Add the msg to the output
    out += msg + "\r\n"
    # Print the output
    sys.stdout.write( out )

# Move the cursor to a postion on the screen
# Can either be a set of coords or a tuple
# (0, 0) is the top left cell
def ansi_move( *args ):
    # Check if one or two args are given
    if len( args ) == 1:
        # Only one arg, so it must be a tuple
        return "\x1B[%s;%sH" % ( args[0][0], args[0][1] )
    elif len( args ) == 2:
        # Two args given, treat each as an int
        return "\x1B[%s;%sH" % ( args[0], args[1] )
    else:
        # No idea what args were given
        return ""

# Ring the bell
def ansi_bell( ):
    return "\a"

# Move the cursor to the top left without clearing the screen
def ansi_home( ):
    return "\x1B[H"

# Clear the screen and put the cursor in the top left
def ansi_clear( ):
    return "\x1B[2J\x1B[H"

# Clear the current line
def ansi_clear_line( ):
    return "\x1B[2K\r"

# Invert the foreground and background colors for some text
def ansi_invert( msg ):
    return "\x1B[7M%s\x1B[27M" % msg
