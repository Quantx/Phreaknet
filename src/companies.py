#!/usr/bin/env python3

####################################
# Architect & Underground (c) 2017 #
#                                  #
# Company servers and management   #
####################################

from init import *

# A basic company
class Company:

    # Store all companies
    companies = []

    # Load all accounts from disk
    @staticmethod
    def load( ):
        # Abort unless hosts is empty
        if Company.companies: return False
        # Get all files in the hst directory
        cmps = next( os.walk( 'cmp' ) )[2]
        # Load each file
        for cmp in cmps:
            if cmp.endswith( '.cmp' ):
                with open( 'cmp/' + cmp, 'rb' ) as f:
                    Company.companies.append( pickle.load( f ) )

    def __init__( self ):
        # Generate a random name
        self.name = Person.random_name( "company" )

# A banking company
class Bank( Company ):
    pass

# A Tech company
class Tech( Company ):
    pass

# A university or college
class College( Company ):
    pass

# A security orginization like the FIB, NSA, etc.
class Security( Company ):
    pass
