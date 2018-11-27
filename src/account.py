#!/usr/bin/env python3

####################################
# Architect & Underground (c) 2017 #
#                                  #
# Client account data              #
####################################

from init import *

import time
from hashlib import pbkdf2_hmac
import random
import os
import pickle

class Account:

    accounts = []

    # Serialize all accounts and save them to disk
    @staticmethod
    def save( ):
        # Keep a count
        acnt = 0
        # Iterate through all accounts
        for act in Account.accounts:
            with open( 'usr/%s.usr' % act.username, 'wb+' ) as fd:
                pickle.dump( act, fd )
            # Increase the cound
            acnt += 1
        # Log the action
        if acnt: xlog( "Saved %s accounts" % acnt )
        # Return the count
        return acnt

    # Load all acounts
    @staticmethod
    def load( ):
        # Abort unless accounts is empty
        if Account.accounts: return 0
        # Keep a count
        acnt = 0
        # Get all files in the usr/ directory
        usrs = next( os.walk( 'usr' ) )[2]
        # Load each file
        for usr in usrs:
            if usr.endswith( '.usr' ):
                with open( 'usr/' + usr, 'rb' ) as fd:
                    Account.accounts.append( pickle.load( fd ) )
                # Increase the count
                acnt += 1
        # Log the action
        if acnt: xlog( "Loaded %s accounts" % acnt )
        # Return the count
        return acnt

    # Returns the account with the specified username
    # Returns none if no such account exists
    @staticmethod
    def find_account( username ):
        for acct in Account.accounts:
            if acct.username == username:
                return acct
        return None

    def __init__( self, uname, pwd ):
        # Username and Password for this account
        self.username = uname
        # Salts prevent rainbow table attacks
        self.passsalt = os.urandom( 64 )
        self.password = self.hash_pass( pwd )
        # Exact time this account was created
        self.first = time.time( )
        # The UID of this account's gateway
        self.gateway = ""
        # 0=Normal user, 1=Operator, 2=Admin
        self.phreakpriv = 0
        # Check if we're in dev mode
        from networking import Server
        if Server.devmode: self.phreakpriv = 2
        # Add us to the list of accounts
        Account.accounts.append( self )

    # Set a new password for this account
    # Returns if successful
    def set_pass( self, oldpass, newpass ):
        # Make sure we're authorized to change the password
        if not self.check_pass( oldpass ): return False
        # Get ourselves a new random salt
        self.passsalt = os.urandom( 64 )
        self.password = self.hash_pass( newpass )

        return True

    # Check the password for this account
    def check_pass( self, pwd ):
        return self.password == self.hash_pass( pwd )

    # Get a cryptographically secure hash of a password
    # THIS IS A SLOW FUNCTION, use it sparingly
    def hash_pass( self, pwd ):
        # Make sure the request is reasonable
        if len( pwd ) > 64: raise PassOverflow(len(pwd))
        # Password hashing function, with sha512
        return pbkdf2_hmac( 'sha512',
                            # Encode the password into utf-8
                            pwd.encode( ),
                            # Add in the random salt
                            self.passsalt,
                            # Use 100,000 rounds for security
                            100000 )

    # Returns true if this user is an Operator or Admin
    def is_oper( self ):
        return self.phreakpriv > 0

    # Returns true if this user is an Admin
    def is_admin( self ):
        return self.phreakpriv > 1

# This is the base class for a Phreaknet NPC
class Person:

    # List of people
    people = []

    # Generate all the NPCs used in Phreaknet
    @classmethod
    def generate_people( cls, size ):
        # Abort if people already generated
        if Person.people: return False
        # Generate grandparents (age 60+)
        for _ in range( size ):
            # Generate a new person
            pass

    # Load all accounts from disk
    @staticmethod
    def load( ):
        # Abort unless hosts is empty
        if Person.people: return False
        # Get all files in the hst directory
        pers = next( os.walk( 'per' ) )[2]
        # Load each file
        for per in pers:
            if per.endswith( '.per' ):
                with open( 'per/' + per, 'rb' ) as f:
                    Person.people.append( pickle.load( f ) )

    # Pick a random name from the given file
    # FILE: male, female, last, hacker
    @staticmethod
    def random_name( file ):
        # Make sure this is an actual file
        if not os.path.isfile( "dat/names/" + file ): return ""
        # Try to open the file
        with open( "dat/names/" + file ) as fd:
            # Read the file and store each line in an array
            names = fd.read( ).splitlines( )
            # Generate a random index of the array
            i = random.randint( 0, len( names ) - 1 )
            # Return that index
            return names[i]

    # Generate a social security number (SSN)
    # This will be uniqure for every person
    def random_ssn( ):
        # Loop until done
        while True:
            # Generate a new 9 digit SSN as a string
            # Template: ###-##-####
            ssn =   "" + random.randint( 100, 999 )
            ssn += "-" + random.randint( 10, 99 )
            ssn += "-" + random.randint( 1000, 9999 )
            # Make sure it's unique
            for per in Person.people:
                # We got a match, try again
                if per.ssn == ssn: break
            else:
                # No match, return it
                return ssn

    def __init__( self ):
        # Is this person male?
        self.male = bool( random.getrandbits(1) )
        # Generate a random first name
        fnf = "female"
        if self.male: fnf = "male"
        self.first = Person.random_name( fnf )
        # Generate a random last name
        self.last = Person.random_name( "last" )
        # Generate a username from the lastname and some numbers
        self.username = self.first[0] + self.last + str( random.randint( 1000, 9999 ) )
        # Generate a unique social security nubmer
        self.ssn = Person.random_ssn( )

        # Add ourselves to the list
        Person.people.append( self )

# A system admin NPC
class Admin( Person ):

    def __init__( self ):
        # Call super init
        super( ).__init__( )

# A hacker NPC
class Hacker( Person ):

    def __init__( self ):
        # Call super init
        super( ).__init__( )
        # Generate a hacker name
        self.username = Person.random_name( "hacker" )
