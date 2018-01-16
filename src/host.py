#!/usr/bin/env python3

####################################
# Architect & Underground (c) 2017 #
#                                  #
# Virtual, in game, hosts          #
####################################

from init import *

import os
import string
import random
import binascii

class Host:

    hosts = []

    # Return a host with an IP address
    @staticmethod
    def find_ip( ip ):
        # Handle some exceptions
        if not ip or ip == "localhost" or ip == "127.0.0.1": return None
        # Crosscheck against all hosts
        for h in Host.hosts:
            if h.ip == ip:
                return h
        # No host matches
        return None

    # Request a new IP address
    # Change this when we implement ISPs
    @staticmethod
    def new_ip( ):
        # Loop until we get an unused IP
        while True:
            # Generate a random IPv4 compatible IP
            ip = ".".join(str(random.randint(1, 254)) for _ in range(4))
            # Make sure the IP is unused
            for h in Host.hosts:
                if h.ip == ip:
                    break
            else:
                return ip

    # Load all hosts from disk
    @staticmethod
    def load( ):
        # Abort unless hosts is empty
        if Host.hosts: return False
        # Get all files in the hst directory
        hsts = next( os.walk( 'hst' ) )[2]
        # Load each file
        for hst in hsts:
            if hst.endswith( '.hst' ):
                with open( 'hst/' + hst, 'rb' ) as f:
                    Account.accounts.append( pickle.load( f ) )
        return True

    def __init__( self, name ):
        # The unique ID of this host
        self.hostid = "".join([random.choice(string.ascii_letters + string.digits) for n in range(16)])

        ### Host info ###
        # Name of the host
        self.hostname = name
        # IP Address of the host, "" = no network
        self.ip = Host.new_ip( )
        # Phone number of the host, "" = no landline
        self.phone = ""
        # Is this booted and running?
        self.online = False
        # Booting into safemode disables network and dialup
        self.safemode = False
        # Stores the hardware specs for this machine
        self.specs = {}

        # When was this system created
        self.sysgen = time.time( )
        # How long has this system been online
        self.alive = time.time( )

        ### File System ###
        # Build the root directory
        os.makedirs( "dir/" + self.hostid )
        # Build the SYS directory
        os.makedirs( "dir/" + self.hostid + "/sys" )
        # Build the BIN directory
        os.makedirs( "dir/" + self.hostid + "/bin" )
        # Build the LOG directory
        os.makedirs( "dir/" + self.hostid + "/log" )
        # Build the USR directory
        os.makedirs( "dir/" + self.hostid + "/usr" )

        # Build the directory.priv files                            owner, group, other = perms    owner group
        with open( "dir/" + self.hostid + "/.directory.priv",     "w" ) as dp: dp.write( "r-xr-xr-x root root" )
        with open( "dir/" + self.hostid + "/sys/.directory.priv", "w" ) as dp: dp.write( "rwxr-xr-x root root" )
        with open( "dir/" + self.hostid + "/bin/.directory.priv", "w" ) as dp: dp.write( "rwxr-xr-x root root" )
        with open( "dir/" + self.hostid + "/log/.directory.priv", "w" ) as dp: dp.write( "rwxrwxr-x root root" )
        with open( "dir/" + self.hostid + "/usr/.directory.priv", "w" ) as dp: dp.write( "rwxrwxr-x root root" )

        ### Process table ###
        # Stores all the processes running on this host
        self.ptbl = []
        # Stores the next pid to assign
        self.npid = 0
        # Stores the maximum number of processes this host can run
        self.mpid = 65335

        ### TTYs below 64 are reserved for non network connections ###
        # Stores the next tty to assign
        self.ntty = 64
        # Stores the maximum number of ttys this host has
        self.mtty = 256

        # Add this host to the master host array
        Host.hosts.append( self )

    # Serialize this host and save it to disk
    def save( self ):
        with open( 'hst/%s.hst' + self.hostname, 'wb+' ) as f:
            pickle.dump( self, f )

    # Relay input to the respective PID
    # Returns if the process is still running
    def stdin( self, pid, data, echo ):
        for p in self.ptbl:
            if p.pid == pid:
                 # Pass the data
                 p.stdin( data, echo )
                 return True
        return False

    # Relay output to the respective PID
    def stdout( self, target, data, echo=False ):
        # Resolve the destination host from the IP
        dhost = self.resolve( target[0] )
        if dhost is not None:
            # Transmit the data
            return dhost.stdin( target[1], data, echo )
        return False

    # Get a reference for the following PID
    # Returns None if no PID is found
    def get_pid( self, pid ):
        for p in self.ptbl:
            if p.pid == pid:
                 return p
        return None

    # Check if a TTY is in use
    def check_tty( self, tty ):
        for p in self.ptbl:
            if p.tty == tty:
                return True
        return False

    # Request a new unused TTY
    def request_tty( self ):
        # Loop until a free TTY is found
        for _ in range( self.mtty - 64 ):
            # Increment self.ntty from last time
            self.ntty += 1
            # Make sure self.ntty isn't greater then self.mtty
            if self.ntty >= self.mtty:
                self.ntty = 64

            # Make sure the TTY is free
            if self.get_tty( self.ntty ): continue

            # TTY is not in use, return it
            return self.ntty

        # No TTYs available
        return None

    # Start a new proc on this host
    # Returns a tuple ( host, pid ) of the new process or None if it didnt start
    def start( self, proc ):
        ### Request a free PID ###
        # If no PID was found within self.mpid attempts then self.ptbl is full
        for _ in range( self.mpid ):
            # Increment self.npid from last time
            self.npid += 1
            # Make sure self.npid isn't greater then self.ntty
            if self.npid >= self.mpid:
                self.npid = 1

            for p in self.ptbl:
                # Break if PID in use
                if self.npid == p.pid: break
            else:
                # PID is free, exit loop
                break
        else:
            # ptbl is full cant start
            return None

        # Pass this host's IP and the new PID
        proc.host = self
        proc.pid = self.npid

        # Append program to our ptbl
        self.ptbl.append( proc )
        # Program started, return the tuple
        return ( self.ip, self.npid )

    # Processes and Programs should use this as much as possible
    def resolve( self, ip ):
        # Is this a local IP?
        if ip == "localhost" or ip == "127.0.0.1": return self
        # Is this host running in safe mode?
        if self.safemode: return None
        # It must be an external IP
        return Host.find_ip( ip )

    # Kill a process running on this host
    # Returns if sucessful or not
    def kill( self, pid ):
        for p in self.ptbl:
            if p.pid == pid:
                # Kill the process and pass a reference
                p.kill( )
                return True
        return False

    # Update all aspects of this host
    def update( self ):
        # Calculate how many threads to update
        cpu = 8
        # Update processes
        i = 0
        while i < cpu:
            # Abort if nothing to update
            if not self.ptbl: return
            # Fetch next process
            proc = self.ptbl.pop( 0 )
            # Make sure process isn't attached
            if proc.destin is not None: continue
            # Execute process
            proc.func = proc.func( )
            # Increment cycle counter
            i += 1
            # Add running processes to the end of the queue
            # Processes with a TTY set to None were created in error
            if proc.func is not None or proc.tty is None:
                self.ptbl.append( proc )
            else:
                # Ensure the process is dead
                proc.kill( )

    # Startup this host
    def startup( self, safemode=False ):
        # Mark this host as online
        self.online = True
        # Configure safe mode
        self.safemode = safemode
        # Reset the active timer
        self.alive = time.time( )

    # Shutdown this host
    def shutdown( self ):
        # Mark this host as offline
        self.online = False

    # Set privlages for a direcory
    # Returns true if privs were altered
    # priv should be a 9 character string in this format:
    # O  G  O
    # W  R  T
    # N  O  H
    # E  O  E
    # R  P  R
    # rwxrwxrwx
    def set_priv( self, path, user, priv ):
        # Are we allowed to edit this directory
        if not self.path_priv( path, user, 1 ): return False
        # Get the correct priv file
        if os.path.isdir( path ):
            path += "/.directory.priv"
        elif os.path.isfile( path ):
            path = os.path.dirname( path ) + "/.directory.priv"
        else:
            return False

        # Validate priv string
        if len( priv ) != 9: return False
        for i in range(9):
            if priv[i] != "-" and priv[i] != "rwxrwxrwx"[i]: return False

        # Get previous priv data
        with open( path ) as dp:
            oldp = dp.readline( ).strip( )

        # Create the new priv string
        newp = priv + oldp[:9]

        # Write priv file
        with open( path, "w" ) as dp:
            dp.write( newp )

        return True

    # Returns true if this user has privlage to preform this operation
    # Oper: Read = 0, Write = 1, Execute = 2
    def path_priv( self, path, user, oper ):
        # Check if we're accessing a file or a directory
        if os.path.isdir( path ):
            # Locate the directorie's priv file
            file = path + "/.directory.priv"
        elif os.path.isfile( path ):
            # Update path
            path = os.path.dirname( path )
            # Get a path to the this file's .filename.priv partner
            file = path + "/." + os.path.basename( path ) + ".priv"
        else:
            # Invalid path
            raise PhreaknetOSError( "No such file or directory" )
        # Make sure this directory actualy contains a priv file
        if not os.path.isfile( file ): return False
        # Store the privs for this directory
        privs = ""
        # Load the privs
        with open( file ) as dp:
            privs = dp.readline( ).strip( )

        # Split privs
        privs = privs.split( )

        # Get all groups this user is in
        groups = self.get_groups( user )

        # Is this user the owner and a group member?
        if ( user == privs[1] and priv[2] in groups
            # Check owner privs
            and privs[0][oper] == "-"
            # Check group privs
            and privs[0][3 + oper] == "-"
            # Check other privs
            and privs[0][6 + oper] == "-" ): return False
        # Is this user just the owner
        elif ( user == privs[1]
            # Check owner privs
            and privs[0][oper] == "-"
            # Check other privs
            and privs[0][6 + oper] == "-" ): return False
        # Is this user just a member of this path's group?
        elif ( priv[2] in self.get_groups( user )
            # Check group privs
            and privs[0][oper] == "-"
            # Check other privs
            and privs[0][6 + oper] == "-" ): return False
        # User is not the owner or a member, just check other privs
        elif priv[0][6 + oper] == "-": return False

        # This user does have permission
        return True

    # Dump the contents of a file to a string
    def read_file( self, file, user ):
        # Make sure we have permission to access this file
        if not self.path_priv( file, user, 0 ): raise PhreaknetOSError( "Permission denied" )
        # Cannot read directories
        if self.path.isdir( "dir/" + self.hostid + file ): raise PhreaknetOSError( "Is a directory" )

        # Open the file
        with open( "dir/" + self.hostid + file ) as fd:
            # Return the contents
            return fd.read( )

    # Dump the contents of a file to an array of strings
    def read_lines( self, file, user ):
        # Output variable
        lines = []
        # Get the data
        data = self.read_file( file, user )
        # Convert data to an array
        for l in s.splitlines( ):
            # Strip any whitespace and append
            lines.append( l.strip( ) )

        return lines

    # Write the contents of data to a file
    # Data must either be a string or an array of strings
    def write_file( self, file, user, data, append=False ):
        # Set the default file mode
        mode = "w"
        # Check if we're in append mode
        if append: mode = "a"
        # Concatinate arrays of strings
        if not isinstance( data, str ): data = "\n".join( data )
        # Make sure we have permission to access this file
        if not self.path_priv( file, user, 0 ): raise PhreaknetOSError( "Permission denied" )
        # Cannot read directories
        if self.path.isdir( "dir/" + self.hostid + file ): raise PhreaknetOSError( "Is a directory" )
        # Open the file
        with open( "dir/" + self.hostid + file, mode ) as fd:
            # Write the data
            fd.write( data )

    # Append data to a file
    def append_file( self, file, user, data ):
        # Call the write function with append mode
        return self.write_file( file, user, data, True )

    # List all the groups this user is in
    # Group file format:
    # groupName:x:groupID:user0,user1,user2
    # root:x:0:root,architect,underground
    def get_groups( self, user ):
        # Get the group file
        glines = self.read_lines( "/sys/group", user )
        # Stores all groups the user is in
        groups = []
        # Iterate through the group file
        for gln in glines:
            # Split the data
            gr = gln.split( ":" )
            # Check if this user is a member of the group
            if user in gr[3].split( "," ):
                # Append group to the list of groups
                groups.append( gr )

        return group

    # Returns true if this user has an account here
    # Passwd file format:
    # username:x:userID:groupID:fingerInfo:homeDir:commandShell
    # architect:x:1021:1020:PhreakNET Dev:/usr/architect:/bin/shell
    def check_user( self, user ):
        # Read the password file
        plines = self.read_lines( "/sys/passwd", user )
        # Iterate through each user
        for acct in plines:
            # Splite each line on the dividing char
            acct = acct.split( ":" )
            # Check if thie is the right account
            if acct[0] == user: return True
        # Account not found
        return False

    # Check if this password matches this username
    # Returns false if this user does not exist
    # Returns false if this user does not have an account
    # Returns false if the password does not match
    def check_pass( self, username, password ):
        # Find the account that matches this username
        acct = Account.find_account( username )
        # Check that this account exists
        if acct is None: return False
        # Check that this user has an account here
        if not self.check_user( username ): return False
        # Check that this is the correct password
        return acct.check_pass( password )

# This is a generic error that is displayed to the user
# The first arg must be a string to be displayed
def PhreaknetOSError( Exception ): pass
