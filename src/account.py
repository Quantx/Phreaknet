#!/usr/bin/env python3

####################################
# Architect & Underground (c) 2017 #
#                                  #
# Client account data              #
####################################

from init.py import *

import time
import hashlib
import os
import pickle

class Account:

    accounts = []

    @staticmethod
    def load( ):
        # Abort unless accounts is empty
        if Account.accounts: return False
        # Get all files in the usr/ directory
        usrs = next( os.walk( '/usr' ) )[2];
        # Load each file
        for usr in usrs:
            if usr.endswith( '.usr' ):
                with open( '/usr/' + usr, 'rb' ) as f:
                    Account.accounts.append( pickle.load( f ) )
        return True

    def __init__( self, uname, pwd ):
        # Username and Password for this account
        self.username = uname
        # Salts prevent rainbow table attacks
        self.passsalt = os.urandom( 64 )
        self.password = self.hashpass( pwd )
        # Exact time this account was created
        self.birth = time.time( )

        # Add us to the list of accounts
        Account.accounts.append( self )

    # Serialize this account and save it to disk
    def save( self ):
        with open( '/usr/%s.usr' + self.username, 'wb+' ) as f:
            pickle.dump( self, f )

    # Set a new password for this account
    # Returns if successful
    def setpass( self, oldpass, newpass ):
        # Make sure we're authorized to change the password
        if not self.checkpass( oldpass ): return False
        # Get ourselves a new random salt
        self.passsalt = os.urandom( 64 )
        self.password = self.hashpass( newpass )

        return True

    # Check the password for this account
    def checkpass( self, pwd ):
        return self.password == self.hashpass( pwd )

    # Get a cryptographically secure hash of a password
    # THIS IS A SLOW FUNCTION, use it sparingly
    def hashpass( self, pwd ):
        # Make sure the request is reasonable
        if len( pwd ) > 64: return b""
        # Password hashing function, with sha512
        return hashlib.pbkdf2_hmac( 'sha512',
                                    # Encode the password into utf-8
                                    pwd.encode( ),
                                    # Add in the random salt
                                    self.passsalt,
                                    # Use 100,000 rounds for security
                                    100000 )
