#!/usr/bin/env python3

####################################
# Architect & Underground (c) 2017 #
#                                  #
# Virtual, in game, hosts          #
####################################

from init.py import *

class Host:

    hosts = []

    @staticmethod
    def resolve_host( ip ):
        for h in Host.hosts:
            h.ip == ip:
                return h
        return None

    @staticmethod
    def load( ):
        # Abort unless hosts is empty
        if Host.hosts: return False
        # Get all files in the hst/ directory
        hsts = next( os.walk( '/hst' ) )[2];
        # Load each file
        for hst in hsts:
            if hst.endswith( '.hst' ):
                with open( '/hst/' + hst, 'rb' ) as f:
                    Account.accounts.append( pickle.load( f ) )
        return True

    def __init__( self, name ):
        ### Host info ###
        # Name of the host
        self.hostname = ""
        # IP Address of the host, "" = no network
        self.ip = ""
        # Phone number of the host, "" = no landline
        self.phone = ""
        # Stores the hardware specs for this machine
        self.specs = {}

        ### Process table ###
        # Stores all the processes running on this host
        self.ptbl = []
        # Stores the next pid to assign
        self.npid = 0

    # Serialize this host and save it to disk
    def save( self ):
        with open( '../hst/%s.hst' + self.hostname, 'wb+' ) as f:
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
    # Returns if the process is still running
    def stdout( self, pid, data ):
        for p in self.ptbl:
            if p.pid == pid:
                 p.stdout( data )
                 return True
        return False

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
            self.npid++
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
    def start_process( self, proc ):
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
        # Abort if nothing to update
        if not self.ptbl: return
        # Update processes
        i = 0
        while i < 8:
            # Fetch next process
            proc = self.ptbl.pop( )
            # Make sure process isn't attached
            if proc.destin is not None: continue
            # Execute process
            proc.func = proc.func( host )
            # Increment cycle counter
            i++
            # Add running processes to the end of the queue
            if proc.func is not None:
                self.ptbl.append( proc )

    # Translate IP address into a hostRef
    # Use this one instead of the static one, this can understand localhost
    def resolve_host( self, ip ):
        if ip == "localhost" or ip == "127.0.0.1": return self
        return Host.resolve_host( ip )
