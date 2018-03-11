#!/usr/bin/env python3

####################################
# Architect & Underground (c) 2017 #
#                                  #
# Client account data              #
####################################

from init import *

import time
from hashlib import pbkdf2_hmac
import os
import pickle

class Account:

    accounts = []

    @staticmethod
    def load( ):
        # Abort unless accounts is empty
        if Account.accounts: return False
        # Get all files in the usr/ directory
        usrs = next( os.walk( 'usr' ) )[2]
        # Load each file
        for usr in usrs:
            if usr.endswith( '.usr' ):
                with open( 'usr/' + usr, 'rb' ) as f:
                    Account.accounts.append( pickle.load( f ) )
        return True

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
        # The IP adresses of this account's gateway
        self.gateway = ""
        # 0=Normal user, 1=Operator, 2=Admin
        self.phreakpriv = 2

        # Add us to the list of accounts
        Account.accounts.append( self )

    # Serialize this account and save it to disk
    def save( self ):
        with open( 'usr/%s.usr' + self.username, 'wb+' ) as f:
            pickle.dump( self, f )

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
        if len( pwd ) > 64: raise PassOverflow(pwd,len(pwd))
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

# Raised when trying to hash a password that is too long
class PassOverflow( Exception ): pass
