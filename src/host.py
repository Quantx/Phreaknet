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
import shutil
import binascii

host_progs = [
    "shell",
    "ps",
    "ls",
    "kill",
    "ssh",
    "porthack",
    "hostname",
    "cat",
    "more",
    "mkdir",
    "rm",
    "adduser",
    "deluser",
    "addgroup",
    "delgroup"
]

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

    # Generate a new unique ID
    @staticmethod
    def new_id( ):
        # Loop until we get an unused ID
        while True:
            # Generate a random 16 digit string
            id = "".join([random.choice(string.ascii_letters + string.digits) for n in range(16)])
            # Make sure the ID is unused
            for h in Host.hosts:
                if h.hostid == id:
                    break
            else:
                return id

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
        self.hostid = Host.new_id( )

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

        # Build the .inode files                           owner, group, other = perms    owner group
        with open( "dir/." + self.hostid + ".inode",     "w" ) as fd: fd.write( "r-xr-xr-x root root" )
        with open( "dir/" + self.hostid + "/.sys.inode", "w" ) as fd: fd.write( "rwxr-xr-x root root" )
        with open( "dir/" + self.hostid + "/.bin.inode", "w" ) as fd: fd.write( "rwxr-xr-x root root" )
        with open( "dir/" + self.hostid + "/.log.inode", "w" ) as fd: fd.write( "rwxrwxr-x root root" )
        with open( "dir/" + self.hostid + "/.usr.inode", "w" ) as fd: fd.write( "rwxrwxr-x root root" )

        # Build the passwd file
        with open( "dir/" + self.hostid + "/sys/passwd", "w" ) as fd: fd.write( "root:x:0:0:root:,,,:/usr/root:/bin/shell\n" )
        with open( "dir/" + self.hostid + "/sys/.passwd.inode", "w" ) as fd: fd.write( "rw-r--r-- root root" )
        # Build the group file
        with open( "dir/" + self.hostid + "/sys/group", "w" ) as fd: fd.write( "root:x:0:\nsudo:x:1:\n" )
        with open( "dir/" + self.hostid + "/sys/.group.inode", "w" ) as fd: fd.write( "rw-r--r-- root root" )

        # Build the user directory for the root account
        os.makedirs( "dir/" + self.hostid + "/usr/root" )
        with open( "dir/" + self.hostid + "/usr/.root.inode", "w" ) as fd: fd.write( "rwx------ root root" )

        # Import all the base progs into /bin
        self.import_progs( host_progs, "/bin" )

        ### Process table ###
        # Stores all the processes running on this host
        self.ptbl = []
        # Stores the next pid to assign
        self.npid = 0
        # Stores the maximum number of processes this host can run
        self.mpid = 65335

        # Stores the next userID to assign
        self.nuid = 1000
        # Stores the next groupID to assign
        self.ngid = 1000

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

    # Import programs to a directory
    # list (strings) | progs ... a list of program names
    # string         | path .... the dir to place them in
    def import_progs( self, progs, path ):
        # Fix the path
        path = self.respath( path )
        # Make sure path is a directory
        if not os.path.isdir( path ): return
        # Loop through every program
        for prg in progs:
            # Build the path to the program
            fn = "dat/progs/" + prg.lower()
            # Make sure this is a valid executable
            if os.path.isfile( fn ):
                # Copy the file
                shutil.copy2( fn, path )
                # Build the inode for this file
                with open( path + "/." + prg.lower() + ".inode", "w" ) as fd:
                    fd.write( "rwxr-xr-x root root" )

    # Relay input to the respective PID
    # Returns if the process is still running
    def stdin( self, pid, data, forward=True ):
        # Fetch the program
        prog = self.get_pid( pid )
        # Check if this program exists
        if prog is not None:
            # Program exists, send the data
            prog.stdin( data, forward )
            return True
        # Program doesn't exist
        return False

    # Relay output to the respective PID
    def stdout( self, target, data, forward=False ):
        # Resolve the destination host from the IP
        dhost = self.resolve( target[0] )
        if dhost is not None:
            # Transmit the data
            return dhost.stdin( target[1], data, forward )
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
            if self.check_tty( self.ntty ): continue

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
            # Check if the current PID is free
            for p in self.ptbl:
                # Break if PID in use
                if self.npid == p.pid: break
            else:
                # PID is free, exit loop
                break

            # Increment self.npid
            self.npid += 1
            # Make sure self.npid isn't greater then self.ntty
            if self.npid >= self.mpid: self.npid = 1
        else:
            # ptbl is full cant start
            return None

        # Pass this host's IP and the new PID
        proc.host = self
        proc.pid = self.npid

        # Increment self.npid for next time
        self.npid += 1
        # Make sure self.npid isn't greater then self.ntty
        if self.npid >= self.mpid: self.npid = 1

        # Append program to our ptbl
        self.ptbl.append( proc )
        # Program started, return the tuple
        return ( self.ip, proc.pid )

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
    # integer | pid .... the process ID to kill
    # string  | user ... the user preforming the operation
    def kill( self, pid, user ):
        for p in self.ptbl:
            if p.pid == pid:
                # Are we allowed to modify this process?
                if ( user == "root" or user == p.user
                or p.group in self.get_groups( user ) ):
                    # Kill the process
                    p.func = p.kill
                    # Kill the child process
                    if p.destin is not None:
                        # Get the host that the child is running on
                        dhost = self.resolve( p.destin[0] )
                        if dhost is not None:
                            # Run the kill command on the child's PID
                            dhost.kill( p.destin[1], user )
                    return True
                # We found the right PID, we can break now
                break
        return False

    # Update all aspects of this host
    def update( self ):
        # Calculate how many threads to update
        cpu = 8
        # Update processes
        i = 0
        while i < cpu:
            # Abort if offline or nothing to update
            if not self.ptbl: return
            # Fetch next process
            proc = self.ptbl[0]
            # Increment process counter
            i += 1
            # Make sure process isn't attached
            if proc.destin is None:
                # Store time at start of execution
                extime = time.time( )
                try:
                    # Execute process
                    proc.func = proc.func( )
                # Catch any ingame errors
                except PhreaknetException as e:
                    # Print the error
                    proc.error( e.args[0] )
                    # Fatal error, naturally
                    proc.func = proc.kill
                # Calculate processor time
                proc.ptime += time.time( ) - extime

                # Add running processes to the end of the queue
                # Processes with a TTY set to None were created in error
                if proc.func is not None or proc.tty is None:
                    # Rotate the list
                    self.ptbl.append( self.ptbl.pop( 0 ) )
                else:
                    # Remove the dead program if we're still online
                    self.ptbl.pop( 0 )
            else:
                # This process isn't actively running, rotate the list
                self.ptbl.append( self.ptbl.pop( 0 ) )

    # Startup this host
    def startup( self, safemode=False ):
        # Can't startup if we're already online
        if not self.online:
            # Mark this host as online
            self.online = True
            # Reset npid and ntty
            self.npid = 0
            self.ntty = 64
            # Start the systemx (operating system) process
            self.start( Systemx( ) )
            # Configure safe mode
            self.safemode = safemode
            # Reset the active timer
            self.alive = time.time( )

            return True

        return False

    # Shutdown this host
    def shutdown( self, reboot=False ):
        # Can't shutdown if we're already offline
        if self.online:
            # Mark this host as offline
            self.online = False
            # Terminate all processes
            for prc in self.ptbl: self.kill( prc.pid, "root" )

            return True

        return False

    # Convert in game paths to actual system paths
    def respath( self, path ):
        if not path.startswith( "dir/" + self.hostid ):
            path = "dir/" + self.hostid + path
        return os.path.normpath( path )

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
        # Fix the path
        path = self.respath( path )
        # Are we allowed to edit this directory
        if not self.path_priv( path, user, 1 ): return False
        # Get the correct inode file
        if os.path.isdir( path ):
            path += "/.inode"
        elif os.path.isfile( path ):
            path = os.path.dirname( path ) + "/.inode"
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

        # Write indoe file
        with open( path, "w" ) as dp:
            dp.write( newp )

        return True

    # Get the path to the inode data for a file
    def get_inode( self, path ):
        # Fix the path
        path = self.respath( path )
        # Return the path to the inode
        return os.path.dirname( path ) + "/." + os.path.basename( path ) + ".inode"

    # Get the inode data for any file on this host
    # Returns a list of the following
    # [ "rwxrwxrwx", "owner", "group" ]
    def get_priv( self, path ):
        # Fix the path
        path = self.respath( path )

        # Is this a valid path?
        if not os.path.exists( path ):
            raise PhreaknetOSError( "No such file or directory" )

        # Get the inode file
        file = self.get_inode( path )

        # Make sure this directory actualy contains a inode file
        if not os.path.isfile( file ):
            raise PhreaknetOSError( "Permission denied" )

        # Load the privs
        with open( file ) as dp:
            # Format and return the list
            return dp.readline( ).strip( ).split( )

    # Returns true if this user has privlage to preform this operation
    # Oper: Read = 0, Write = 1, Execute = 2
    def path_priv( self, path, user, oper ):
        # Fix the path
        path = self.respath( path )

        # Get the privs
        privs = self.get_priv( path )

        # root can do whatever the hell he wants (prevents infinite recursion)
        if user == "root": return True

        # Get all groups this user is in
        groups = self.get_groups( user )

        # Is this user the owner and a group member?
        if user == privs[1] and privs[2] in groups:
            # Check owner privs
            if ( privs[0][oper] == "-"
            # Check group privs
            and  privs[0][3 + oper] == "-"
            # Check other privs
            and  privs[0][6 + oper] == "-" ): return False
        # Is this user just the owner
        elif user == privs[1]:
            # Check owner privs
            if ( privs[0][oper] == "-"
            # Check other privs
            and  privs[0][6 + oper] == "-" ): return False
        # Is this user just a member of this path's group?
        elif privs[2] in self.get_groups( user ):
            # Check group privs
            if ( privs[0][oper] == "-"
            # Check other privs
            and  privs[0][6 + oper] == "-" ): return False
        # User is not the owner or a member, just check other privs
        else:
            if privs[0][6 + oper] == "-": return False

        # This user does have permission
        return True

    # Returns a tuple containing two lists, files and directories
    def list_dir( self, path, user ):
        # Correct the path
        path = self.respath( path )
        # Make sure we can read this directory
        if not self.path_priv( path, user, 0 ):
            raise PhreaknetOSError( "Permission denied" )
        # Verify this is a directory
        if not os.path.isdir( path ):
            raise PhreaknetOSError( "Cannot list contents of file" )

        # Walk the path and get the contents of this dir
        _, dnames, fnames = next( os.walk(path) )
        # Only return files that we are allowed to view
        fnames[:] = [fn for fn in fnames if os.path.isfile( path + "/." + fn + ".inode" )]
        # Only return directorys that we are allowed to view
        dnames[:] = [dn for dn in dnames if os.path.isfile( path + "/." + dn + ".inode" )]
        # Return the results
        return ( dnames, fnames )

    # Attempt to execute a file, returns the class to be instantiated
    # string | path ... path to file
    # string | user ... user preforming the operation
    def exec_file( self, path, user ):
        # Fix the path
        path = self.respath( path )
        # Make sure we have permission to execute the file
        if not self.path_priv( path, user, 2 ):
            raise PhreaknetOSError( "Permission denied" )
        # Cannot execute directories
        if os.path.isdir( path ):
            raise PhreaknetOSError( "Is a directory" )
        # Find the corresponding program
        prg = Program.find_prog( os.path.basename( path ) )
        # Make sure this is the actual executible
        if prg is None or prg.checksum != md5_check( path ):
            raise PhreaknetOSError( "Segmentation fault" )
        # Return the class
        return prg

    # Dump the contents of a file to a string
    def read_file( self, path, user ):
        # Fix the path
        path = self.respath( path )
        # Make sure we have permission to access this file
        if not self.path_priv( path, user, 0 ):
            raise PhreaknetOSError( "Permission denied" )
        # Cannot read directories
        if os.path.isdir( path ):
            raise PhreaknetOSError( "Is a directory" )

        # Open the file
        with open( path ) as fd:
            # Store the contents
            return fd.read( )

    # Dump the contents of a file to an array of strings
    def read_lines( self, path, user ):
        # Output variable
        lines = []
        # Get the data
        data = self.read_file( path, user )
        # Convert data to an array
        for ln in data.splitlines( ):
            # Strip any whitespace and append
            lines.append( ln.strip( ) )

        return lines

    # Write the contents of data to a file
    # Data must either be a string or an array of strings
    def write_file( self, path, user, data, append=False ):
        # Build file path
        path = self.respath( path )
        # Set the default file mode
        mode = "w"
        # Check if we're in append mode
        if append: mode = "a"
        # Concatinate arrays of strings
        if not isinstance( data, str ): data = "\n".join( data ) + "\n"
        # Make sure we have permission to access this file
        if not self.path_priv( path, user, 1 ):
            raise PhreaknetOSError( "Permission denied" )
        # Make sure this is in fact a file
        if not os.path.isfile( path ):
            raise PhreaknetOSError( "Is a directory" )
        # Open the file
        with open( path, mode ) as fd:
            # Write the data
            fd.write( data )

    # Append data to a file
    def append_file( self, path, user, data ):
        # Call the write function with append mode
        return self.write_file( path, user, data, True )

    # Make a directory
    def make_dir( self, path, user ):
        # Fix the path
        path = self.respath( path )
        # Confirm that we can edit the parent directory
        if not self.path_priv( os.path.dirname( path ), user, 1 ):
            raise PhreaknetOSError( "Permission denied" )
        # Catch file exist errors
        try:
            # Create the actual directory
            os.mkdir( path )
            # Build the inode file with default privs
            with open( self.get_inode( path ), "w" ) as fd:
                fd.write( "rwxrwxr-x " + user + " " + user )
        except FileExistsError:
            # The directory already exists
            raise PhreaknetOSError( "File exists" )

    # Delete an object from the filesystem
    # string  | path ... the object to delete
    # string  | user ... the user preforming the action
    # integer | dirs ... can we delete dirs? 0=NO, 1=Only_Empty, 2=Recursive
    def remove_file( self, path, user, dirs=0 ):
        # Fix the path
        path = self.respath( path )
        # Make sure we have permission to delete (write)
        if not self.path_priv( path, user, 1 ):
            raise PhreaknetOSError( "Permission denied" )
        # Catch any OSErros
        try:
            # Which deletion method are we using?
            if dirs == 2:
                # Delete the directory and it's contents
                shutil.rmtree( path )
            elif dirs == 1:
                # Delete the directory
                os.rmdir( path )
            else:
                # Delete the file
                os.remove( path )
            # Delete the inode data
            os.remove( self.get_inode( path ) )
        except OSError as e:
            # Reformat the error as a PhreaknetOSError
            raise PhreaknetOSError( e.strerror )

    # Delete a folder (and its contents)
    def remove_dir( self, path, user, recur=False ):
        opt = 1
        if recur: opt = 2
        return self.remove_file( path, user, opt )

    # List all users on the system or in a specific group
    # string (optional) | group ... the group to get users from
    def get_users( self, group="" ):
        users = []
        # Are we searching a group?
        if group:
            # Get the group file, must be done as root to avoid infinite recursion
            glines = self.read_lines( "/sys/group", "root" )
            # Iterate through groups to find the right one
            for gln in glines:
                # Split the data
                gr = gln.split( ":" )
                # Check if this is the right group
                if group == gr[0]:
                    # This is faster than just appending
                    users = gr[3].split( "," )
                    # Correct for empty list
                    if not users[0]: users = []
                    # We're done here
                    break
        # Are we searching the whole system?
        else:
            # Get the passwd file, must be done as root to avoid infinite recursion
            plines = self.read_lines( "/sys/passwd", "root" )
            # Iterate through all the users
            for pln in plines:
                # Split the data
                pr = pln.split( ":" )
                # Add the user
                users.append( pr[0] )
        # Return the list
        return users

    # List all the groups this user is in or list all groups on the system
    # Group file format:
    # groupName:x:groupID:user0,user1,user2
    # root:x:0:root,architect,underground
    # string (optional) | user ... the user to check for
    def get_groups( self, user="" ):
        # Get the group file, must be done as root to avoid infinite recursion
        glines = self.read_lines( "/sys/group", "root" )
        # Stores all groups the user is in
        groups = []
        # Are we're just checking for this user
        if user:
            # Get the passwd file, must be done as root to avoid infinite recursion
            plines = self.read_lines( "/sys/passwd", "root" )
            # Store the primary group
            prim = ""
            # Get this user's primary group
            for pln in plines:
                # Split the data
                pr = pln.split( ":" )
                # Is this the correct user?
                if user == pr[0]: prim = pr[3]
            # Iterate through the group file
            for gln in glines:
                # Split the data
                gr = gln.split( ":" )
                # Check if this user is a member of the group
                if prim == gr[2] or user in gr[3].split( "," ):
                    # Append group to the list of groups
                    groups.append( gr[0] )
        # We're just listing off all the groups?
        else:
            # Iterate through all the groups
            for gln in glines:
                # Split the data
                gr = gln.split( ":" )
                # Get the name of the group
                groups.append( gr[0] )
        # Return the list of groups
        return groups

    # Returns true if this user has an account here
    # Passwd file format:
    # username:x:userID:groupID:fingerName,fingerMail,fingerStatus,fingerPlag:homeDir:shellDir
    # architect:x:1021:1020:John Doe,test@123.123.123.123,PhreakNET Dev,Neat plan bro:/usr/architect:/bin/shell
    # string or Account | cuser ... The user to check
    # string or Account | user .... The user preforming the check
    def check_user( self, cuser, user ):
        # Read the password file
        plines = self.read_lines( "/sys/passwd", user )
        # Iterate through each user
        for acct in plines:
            # Splite each line on the dividing char
            acct = acct.split( ":" )
            # Check if thie is the right account
            if acct[0] == cuser: return True
        # Account not found
        return False

    # Check if this password matches this username
    # Returns false if this user does not exist
    # Returns false if this user does not have an account
    # Returns false if the password does not match
    # string | cuser ...... The user to check
    # string | password ... The password to check
    # string | user ....... The user preforming the check
    def check_pass( self, cuser, password, user ):
        # Find the account that matches this username
        acct = Account.find_account( cuser )
        # Check that this account exists
        if acct is None: return False
        # Check that this user has an account here
        if not self.check_user( cuser, user ): return False
        # Check that this is the correct password
        return acct.check_pass( password )

    # string | nuser ... user to add to the system
    # string | user .... the user preforming this operation
    # Returns true if successfull
    def add_user( self, nuser, user ):
        # Make sure this account doesn't already exist
        if self.check_user( nuser, user ): return False
        # Make sure this account even exists
        if isinstance( nuser, Account ):
            # We were given an account, so we know it must exist
            nuser = nuser.username
        elif Account.find_account( nuser ) is None:
            # Make sure this account exists
            return False
        # Build the new user's passwd file line
        paswd = "%s:x:%s:%s:,,,:/usr/%s:/bin/shell\n" % (nuser, self.nuid, self.ngid, nuser)
        # Try to build the group file
        if not self.add_group( nuser, user ): return False
        # Create the user
        self.append_file( "/sys/passwd", user, paswd )
        # Increment the new userID
        self.nuid += 1
        # Make this user's home directory
        os.makedirs( "dir/" + self.hostid + "/usr/" + nuser )
        with open( "dir/" + self.hostid + "/usr/." + nuser + ".inode", "w" ) as fd: fd.write( "rwx------ " + nuser + " " + nuser )
        # Return success
        return True

    # Add a new group to the system
    # string | ngroup ... group to add to the system
    # string | user ..... user preforming the operation
    def add_group( self, ngroup, user ):
        # Make sure this group doesn't already exist
        if ngroup in self.get_groups( ): return False
        # Build the new group file line
        group = "%s:x:%s:\n" % (ngroup, self.ngid)
        # Create the group
        self.append_file( "/sys/group", user, group )
        # Increment the new groupID
        self.ngid += 1
        # Return success
        return True

    # Remove a user from the system (if they're not logged in)
    # string | nuser ... user to delete from the system
    # string | user .... user preforming the operation
    def del_user( self, nuser, user ):
        # Make sure this user has an account
        if not self.check_user( nuser, user ): return False
        # Make sure this user isn't logged in
        for prc in self.ptbl:
            # Is this a background process or not?
            if prc.user == nuser and prc.tty >= 0:
                raise PhreaknetOSError( "user is currently logged in" )
        # Start by deleting this user's group
        self.del_group( nuser, user )
        # We're good, let's terminate this account
        users = self.read_lines( "/sys/passwd", user )
        # Strip this user from both lists
        users[:] = [us for us in users if not us.startswith( nuser )]
        # Re-write the file
        self.write_file( "/sys/passwd", user, users )
        # Return success
        return True

    # Delete a group from the system
    # string | ngroup ... the group to delete
    # string | user ..... the user preforming the operation
    def del_group( self, ngroup, user ):
        # We're good, lets remove this group
        groups = self.read_lines( "/sys/group", user )
        # Strip this user from the groups
        groups[:] = [gr for gr in groups if not gr.startswith( ngroup )]
        # Re-write the file
        self.write_file( "/sys/group", user, groups )

    # Join a group
    # string | nuser ... the user joining the group
    # string | group ... the group to join
    # string | user .... the user preforming the operation
    def join_group( self, nuser, group, user ):
        # Make sure this user exists
        if not self.check_user( nuser, user ): return False
        # Get all the users currently in this group
        ugrp = self.get_users( group )
        # Are we the first in this group?
        first = ","
        if not ugrp:
            first = ""
        # Make sure this user isn't already in this group
        elif nuser in ugrp: return False
        # Read the group file
        groups = self.read_lines( "/sys/group", user )
        # Find our group
        for i, gr in enumerate( groups ):
            # Find the group with our name
            if gr.split( ":" )[0] == group:
                # Append us to this group
                groups[i] = gr + first + nuser
                # We're done here
                break
        else:
            # No group with our name was found
            return False
        # Re-write the file
        self.write_file( "/sys/group", user, groups )
        # Return success
        return True


    # Leave a group
    # string | nuser ... the user leaving the group
    # string | group ... the group to leave
    # string | user .... the user preforming the operation
    def leave_group( self, nuser, group, user ):
        # Read the group file
        groups = self.read_lines( "/sys/group", user )
        # Find our group
        for i, gln in enumerate( groups ):
            # Split the data
            gr = gln.split( ":" )
            # Check if this is our group
            if group != gr[0]: continue
            # Remove ourselves from this group
            gr[3] = gr[3].replace( "," + nuser, "" )
            # Do a second pass incase we're the first member
            gr[3] = gr[3].replace( nuser, "" )
            # Rebuild and replace
            groups[i] = ":".join( gr )
        # Re-write the file
        self.write_file( "/sys/group", user, groups )
        # Return success
        return True

# This program is basically the operating system for a Host. It is alw$
# first, cannot be run by a user and when killed will shutdown the hos$
# You can use this program's eventloop to run background OS level oper$
class Systemx( Program ):

    def __init__( self ):
        # No need for params, since this program is never run by a rea$
        super( ).__init__( "root", "/", -1, (80, 24), None, [] )

    def run( self ):
        return self.run

    def kill( self ):
        # Operating system was killed, shutdown the host
        self.host.shutdown( )
        # Make sure to call the parent function
        return super( ).kill( )
