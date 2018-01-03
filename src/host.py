#!/usr/bin/env python3

####################################
# Architect & Underground (c) 2017 #
#                                  #
# Virtual, in game, hosts          #
####################################

from init import *
from random import randint

class Host:

    hosts = []

    # Resolve an IP address
    @staticmethod
    def resolve( ip ):
        # Eliminate a few bad IPs quickly
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
    def request( ):
        # Loop until we get an unused IP
        while True:
            # Generate a random IPv4 compatible IP
            ip = ".".join(str(randint(1, 254)) for _ in range(4))
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
        # Get all files in the hst/ directory
        hsts = next( os.walk( 'hst' ) )[2];
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
        self.ip = Host.request( )
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

        ### Process table ###
        # Stores all the processes running on this host
        self.ptbl = []
        # Stores the next pid to assign
        self.npid = 0

        # Add this host to the master host array
        Host.hosts.append( self )

    # Serialize this host and save it to disk
    def save( self ):
        with open( 'hst/%s.hst' + self.hostname, 'wb+' ) as f:
            pickle.dump( self, f )

    # Relay input to the respective PID
    # Returns if the process is still running
    def stdin( self, pid, data ):
        for p in self.ptbl:
            if p.pid == pid:
                 p.stdin( data )
                 return True
        return False

    # Relay output to the respective PID
    def stdout( self, pid, data ):
        for p in self.ptbl:
            if p.pid == pid:
                 p.stdout( data )

    # Get a reference for the following PID
    # Returns None if no PID is found
    def get_pid( self, pid ):
        for p in self.ptbl:
            if p.pid == pid:
                 return p
        return None

    # Return next available PID
    # Returns less then 0 if all PIDs are taken
    def get_npid( self ):
        # If no PID was found within 65535 attempts then self.ptbl is full
        for _ in range( 65535 ):
            # Increment self.npid from last time
            self.npid += 1
            # Make sure self.npid isn't greater then the highest PID
            if self.npid >= 65335:
                self.npid = 1

            for p in self.ptbl:
                # Break if PID in use
                if self.npid == p.pid: break
            else:
                # PID is free, return it
                return self.npid
        # Full, return negative
        return -1;

    # Start a new process or program on the host
    # Usage:
    # <Process> | proc ... process to start
    #
    # Returns:
    # True if the process was started
    # False if the PID was taken
    def start( self, proc ):
        # Validate that the requested PID is free
        for p in self.ptbl:
            if p.pid == proc.pid:
                return False

        # Safe to start program
        self.ptbl.append( proc )
        return True

    # Kill a process running on this host
    # Returns if sucessful or not
    def kill( self, pid ):
        for p in self.ptbl:
            if p.pid == pid:
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
            proc = self.ptbl.pop( )
            # Make sure process isn't attached
            if proc.destin is not None: continue
            # Execute process
            proc.func = proc.func( self )
            # Increment cycle counter
            i += 1
            # Add running processes to the end of the queue
            if proc.func is not None:
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
