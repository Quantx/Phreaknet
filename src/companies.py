#!/usr/bin/env python3

####################################
# Architect & Underground (c) 2017 #
#                                  #
# Company servers and management   #
####################################

from init import *

import uuid

# A basic company
class Company:

    # Store all companies
    companies = []

    # Generate a bunch of companies for Phreaknet DO THIS ONCE
    @classmethod
    def generate_companies( cls ):
        # Abort unless companies is empty
        if Company.companies: return False
        # Make sure we don't make duplicate companies
        excomp = []
        for comp in next( os.walk( 'cmp' ) )[2]:
            # Strip the file extension
            excomp.append( comp[:-4] )
        # List through all our child classes
        for sub in cls.__subclasses__( ):
            # Get the type of company
            ctype = sub.__name__.lower()
            # Is this an abstract company?
            if not os.path.isfile( "dat/companies/" + ctype ): continue
            # Load this company's data file
            with open( "dat/companies/" + ctype ) as fd:
                # Iterate through each line of this file
                for comp in fd.readlines( ):
                    # Make sure this company doesnt already exist
                    if comp in excomp: continue
                    # Generate the company and store it
                    Company.companies.append( sub( comp, 0 ) )

    # Return the PhreakNET organization
    @staticmethod
    def get_phreaknet( ):
        # Iterate through all the companies
        for cmp in Company.companies:
            # Is this the correct company?
            if type( cmp ) is PhreaknetOrg:
                # Return it
                return cmp
        # If this function returns None then there is a problem
        return None

    # Load all accounts from disk
    @staticmethod
    def load( ):
        # Abort unless companies is empty
        if Company.companies: return False
        # Get all files in the hst directory
        cmps = next( os.walk( 'cmp' ) )[2]
        # Load each file
        for cmp in cmps:
            if cmp.endswith( '.cmp' ):
                with open( 'cmp/' + cmp, 'rb' ) as f:
                    Company.companies.append( pickle.load( f ) )

    def __init__( self, name, geoloc ):
        # Generate a unique id for the company
        self.uid = str( uuid.uuid4( ) )
        # Generate a random name
        self.name = name
        # The location of this company
        self.geoloc = geoloc
        # Store this company's staff
        self.staff = []
        # Store this company's hosts
        self.hosts = []

    # Add a new host to this company, returns host id
    def add_host( self, hostname ):
        # Create the host
        hst = Host( hostname, self.geoloc )
        # Add it to the list
        self.hosts.append( hst )
        # Return the host ID
        return hst.uid

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

# A internet service provider company
class ISP( Company ):
    pass

# A special company for PhreakNET in-game corporation
class PhreaknetOrg( Company ):

    def __init__( self, name, geoloc ):
        # Call super
        super( ).__init__( name, getCityName( "us", "ca", "palo alto" ) )
        # Generate the Router
        self.add_host( "PhreakNET " )
