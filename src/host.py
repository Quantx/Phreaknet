#!/usr/bin/env python3

####################################
# Architect & Underground (c) 2017 #
#                                  #
# Virtual, in game, hosts          #
####################################

from init import *
import os
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

        # Build the filesystem
        self.fileid = "".join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
        # Build the root directory
        os.makedirs( "dir/" + self.fileid )
        # Build the SYS directory
        os.makedirs( "dir/" + self.fileid + "/sys" )
        # Build the BIN directory
        os.makedirs( "dir/" + self.fileid + "/bin" )
        # Build the LOG directory
        os.makedirs( "dir/" + self.fileid + "/log" )
        # Build the USR directory
        os.makedirs( "dir/" + self.fileid + "/usr" )

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
            self.ntty += 1:
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

        # Pass a reference to this host and the new PID
        proc.hpid = ( self, self.npid )

        # Append program to our ptbl
        self.ptbl.append( proc )
        # Program started, return the tuple
        return proc.hpid

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

# Shitty file handling
# Probably need to revise all this
"""
    # Returns true if the specified user has root privlages
    def has_root( self, user ):
        if user == "guest": return False
        if user == "root": return True

        return False

    # Returns true if the specified user is root
    def is_root( self, user ):
        if user == "guest": return False
        if user == "root": return True

    # Check if a user can access this directory
    # op: 0 = Read, 1 = Write, 2 = Exec
    def checkpath( self, path, user, op=0 )
        # Normalize the path
        path = os.path.realpath( path )

        # Calculate the privlages for this user
        privs = 0
        if user != "guest": privs += 1
        if self.is_root( user ): privs += 1

        # Calculate the absolute path of the root directory
        root = os.path.join( os.path.realpath( "dir/" + self.fileid ), "" )
        # No one should be able to access anything outside the root directory
        if os.path.commonprefix([path, root]) != root:
            return False

        # Get a list of files in the directory
        files = next( os.walk( path ) )[2]
        # Only access directories with a priv file
        if "directory.priv" in files:
            with open( "directory.priv" ) as dp:
                # Evaluate the privlages for this files
                return dp.readline( )[privs * 3 + op] != "-"
        else:
            return False

    # Read a file safely
    def readfile( self, path, user ):
        # Sanitize path
        path = os.path.realpath( path )

        # Does the user have privlage to read this file
        if not self.checkpath( path, user, 0 ): return ""

        # Users may not access the directory priv directly
        if path.endswith( "directory.priv" ): return ""

        # Return the file as an array of lines
        with open( path ) as f:
            return f.readlines( )

    # Write a file safely
    def writefile( self, path, data, user ):
        # Sanitize path
        path = os.path.realpath( path )

        # Does the user have privlage to modify this file
        if not self.checkpath( path, user, 1 ): return False

        # Users may not access the directory priv directly
        if path.endswith( "directory.priv" ): return False

        # Create, or overwrite this file
        with open( path, "w" ) as f:
            # Is the data a string or an array
            if type( data ) is str:
                f.write( data )
            else:
                f.writelines( data )

        return True

    # Append data to a file safely
    def appendfile( self, path, data, user ):
        # Sanitize path
        path = os.path.realpath( path )

        # Does the user have privlage to modify this file
        if not self.checkpath( path, user, 1 ): return False

        # Users may not access the directory priv directly
        if path.endswith( "directory.priv" ): return False

        # Create, or append data to this file
        with open( path, "a" ) as f:
            # Is the data a string or an array
            if type( data ) is str:
                f.write( data )
            else:
                f.writelines( data )

        return True

    # Returns a list of all the files in the directory
    def listdir( self, path, user ):
        # Sanitize path
        path = os.path.realpath( path )

        # Does the user have privlage to read this directory
        if not self.checkpath( path, user, 0 ): return ""

        # Get a list of dirs and files
        ( _, dirs, files ) = next( os.walk( path ) )

        # Load the privs for the current directory
        privs = ""
        with open( path + "/directory.priv" ) as f:
            privs = f.readline( )

        # Output list
        out = []

        for fl in files:
            # Unixtime for when the file was last accessed
            last = os.path.getmtime( path + "/" + fl )
            # Get the size of the file in bytes
            size = os.path.getsize( path + "/" + fl )
            # Format the string
            out.append( "-%s %16s %6s %s %s" % ( privs, "guest", size, time.strftime( "%b %d %H:%M" ), fl ) )

        for dl in dirs:
            # Unixtime for when the dir was last accessed
            last = os.path.getmtime( path + "/" + dl )
            # Get the priv for this directory
            with open( path + "/" + dl + "/directory.priv" ) as pf:
                dpriv = pf.readline( )
                # Format the string
                out.append( "d%s %16s %6s %s %s" % ( dpriv, "guest", "4096", time.strftime( "%b %d %H:%M" ), dl ) )

        return out

    # Add a user to the data base
    def adduser( self, user ):
        # Append this user to the passwd file, use a random password for security reasons
        self.appendfile( "dir/" + self.fileid + "/sys/passwd", user + ":" + binascii.hexlify( os.urandom( 32 ) ), "root" )

    def deluser( self, user ):
        # Get a list of users and passwords
        lines = self.readfile( "dir/" + self.fileid + "/sys/passwd", "root" )
        # Remove the specific user from the list
        npswd = [ l for l in lines if l.startswith( user ) ]
        # Write the data to the passwd file
        self.writefile( "dir/" + self.fileid + "/sys/passwd",  npswd, "root" )
"""
