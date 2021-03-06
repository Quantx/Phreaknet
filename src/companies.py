#!/usr/bin/env python3

####################################
# Architect & Underground (c) 2017 #
#                                  #
# Company servers and management   #
####################################

from init import *

from uuid import uuid4

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

        # Get a list of all subclasses
        comps = cls.__subclasses__( )
        # Ensure ISPs are handled first
        comps.insert(0, comps.pop( comps.index( ISP ) ) )

        # List through all our child classes
        for sub in comps:
            # Get the type of company
            ctype = sub.__name__.lower( )
            # Is this an abstract company?
            if not os.path.isfile( "dat/companies/" + ctype ): continue
            # Read this company's data file
            with open( "dat/companies/" + ctype ) as fd:
                # Count the companies
                ccnt = 0
                # Iterate through each line of this file
                for comp in fd:
                    # Generate the company and store it
                    Company.companies.append( sub( comp.strip( ), getCityRandom( ) ) )
                    # Add 1 to the count
                    ccnt += 1
                # Store the number of companies generated
                sub.count = ccnt
                # Debug
                if ccnt: xlog( "Created %s %s companies" % ( ccnt, ctype ) )

    # Get a random company
    @classmethod
    def random_company( cls ):
        # No companies of this type
        if not hasattr( cls, "count" ): return ""
        # Get a random company
        i = random.randint( 0, cls.count - 1 )
        # Return that company
        return Company.companies[i].uid

    # Save all companies to disk
    @staticmethod
    def save( ):
        # Save a count
        ccnt = 0
        # Iterate through all companies
        for cmp in Company.companies:
            # Save company to disk
            with open( 'cmp/%s.cmp' % cmp.uid, 'wb+' ) as fd:
                pickle.dump( cmp, fd )
            # Increase the count
            ccnt += 1
        # Log the action
        if ccnt: xlog( "Saved %s companies" % ccnt )
        # Return the count
        return ccnt

    # Load all companies from disk
    @staticmethod
    def load( ):
        # Abort unless companies is empty
        if Company.companies: return 0
        # Keep a count
        ccnt = 0
        # Get all files in the hst directory
        cmps = next( os.walk( 'cmp' ) )[2]
        # Load each file
        for cmp in cmps:
            if cmp.endswith( '.cmp' ):
                with open( 'cmp/' + cmp, 'rb' ) as fd:
                    # Unpack the company
                    ccls = pickle.load( fd )
                    # Increase the count
                    if hasattr( type( ccls ), "count" ):
                        type( ccls ).count += 1
                    # Class doesn't have a count yet
                    else:
                        type( ccls ).count = 1
                    Company.companies.append( ccls )
                # Increase the count
                ccnt += 1
        # Log the action
        if ccnt: xlog( "Loaded %s companies" % ccnt )
        # Return the count
        return ccnt

    def __init__( self, name, geoloc=None ):
        # Generate a unique id for the company
        self.uid = str( uuid4( ) )
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
        rout = None
        # Check if we need an ISP class router
        if type( self ) is ISP:
            # We're an ISP
            rout = ISPRouter( self.name, self.geoloc )
        else:
            # We're not an ISP so we need to subscribe to one
            self.isp = ISP.random_company( )
            # Get that ISP's router
            routerid = Company.find_id( self.isp ).router
            # Create our router
            rout = Router( self.name, self.geoloc, routerid )
        # Store this router's id
        self.router = rout.uid
        # Boot the router
        rout.startup( )

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
