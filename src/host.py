#!/usr/bin/env python3

####################################
# Architect & Underground (c) 2017 #
#                                  #
# Virtual, in game, hosts          #
####################################

import init.py

class Host:

    def __init__( self, name ):
        ### Host info ###
        # Name of the host
        self.name = ""
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
        self.npid = 0;

    # Relay input to the respective PID
    # Return if the process is still running
    # Should only be called
    def input( self, pid, data ):
        for p in self.ptbl:
            if p.pid == pid:
                 p.input( data )
                 return 1
        else:
            return 0

    # Return next available PID
    # Returns less then 0 if all PIDs are taken
    def get_pid( self ):
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
            # PID already taked, abort
            if proc.pid == p.pid:
                return False

        # Safe to start program
        self.ptbl.append( proc )
        return True

    # Update all aspects of this host
    def update( self ):
        # Abort if nothing to update
        if not self.ptbl: return
        # Update processes
        for _ in range( 8 ):
            # Fetch next process
            proc = self.ptbl.pop( )
            # Execute process
            proc.func = proc.func( host )
            # Add running processes to the end of the queue
            if proc.func is not None:
                self.ptbl.append( proc )
