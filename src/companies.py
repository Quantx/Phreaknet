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

    # Find company by id
    @staticmethod
    def find_id( cid ):
        # Make sure we got a valid uuid
        if cid and len( cid ) != 36: return None
        # Iterate through id
        for cmp in Company.companies:
            # Is this the correct host
            if cmp.uid == cid:
                return cmp
        # No host matches this ID
        return None

    # Generate a bunch of companies for Phreaknet DO THIS ONCE
    @classmethod
    def generate_companies( cls ):
        # Abort unless companies is empty
        if Company.companies: return False
        # Load ISPs first
        with open( "dat/companies/isp" ) as fd:
             # Count the companies
             ccnt = 0
             # Iterate through each line of this file
             for comp in fd.readlines( ):
                 # Generate the company and store it
                 Company.companies.append( ISP( comp, getCityRandom( 3 ) ) )
                 # Add 1 to the count
                 ccnt += 1
             # Debug
             xlog( "Created %s isp companies" % ccnt )

        # List through all our child classes
        for sub in cls.__subclasses__( ):
            # Get the type of company
            ctype = sub.__name__.lower( )
            # Already did ISPs skip this
            if ctype == "isp": continue
            # Is this an abstract company?
            if not os.path.isfile( "dat/companies/" + ctype ): continue
            # Load this company's data file
            with open( "dat/companies/" + ctype ) as fd:
                # Count the companies
                ccnt = 0
                # Iterate through each line of this file
                for comp in fd.readlines( ):
                    # Generate the company and store it
                    Company.companies.append( sub( comp, getCityRandom( ) ) )
                    # Add 1 to the count
                    ccnt += 1
                # Debug
                xlog( "Created %s %s companies" % ( ccnt, ctype ) )

    # Get a random company
    @classmethod
    def random_company( cls ):
        # Choices list
        output = []
        # Iterate through all companies
        for cmp in Company.companies:
            # Check if this is the right type of company
            if isinstance( cmp, cls ):
                # Add it to the list
                output.append( cmp.uid )
        # No companies of this type
        if not output: return ""
        # Get a random company
        i = random.randint( 0, len( output ) - 1 )
        # Return that company
        return output[i]

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

    def __init__( self, name, geoloc=None ):
        # Generate a unique id for the company
        self.uid = str( uuid.uuid4( ) )
        # Generate a random name
        self.name = name
        # The location of this company
        if geoloc:
            self.geoloc = geoloc
        else:
            self.geoloc = getCityRandom( )
        # Store this company's staff
        self.staff = []
        # Store this company's hosts
        self.hosts = []
        # Store this company's ip
        self.isp = ""
        # Store this company's router
        # Check if we need an ISP class router
        if type( self ) is ISP:
            self.router = ISPRouter( self.name, self.geoloc ).uid
        else:
            self.isp = ISP.random_company( )
            routerid = Company.find_id( self.isp ).router
            self.router = Router( self.name, self.geoloc, routerid ).uid

    # Add a new host to this company, returns host id
    def add_host( self, hostname ):
        # Create the host
        hst = Host( hostname, self.geoloc, self.router )
        # Add it to the list
        self.hosts.append( hst.uid )
        # Return the host
        return hst

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

    def __init__( self, name, geoloc ):
        # Call super
        super( ).__init__( name, getCityName( "us", "ca", "palo alto" ) )
