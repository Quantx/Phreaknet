#!/usr/bin/env python3

####################################
# Architect & Underground (c) 2017 #
#                                  #
# Ingame exceptions                #
####################################

from init import *

# All ingame exceptions should inherit from this one
# The first arg must be a string to be displayed
class PhreaknetException( Exception ): pass

# An ingame Operating System error, such as "File not found"
class PhreaknetOSError( PhreaknetException ): pass

# Thrown when an invalid value was entered, such as a PID less than 0
class PhreaknetValueError( PhreaknetException ): pass
