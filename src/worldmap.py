#!/usr/bin/env python3

####################################
# Architect & Underground (c) 2017 #
#                                  #
# General purpose system programs  #
####################################

from init import *

# Import 3rd party dependencies
import shapefile
from bitstring import BitArray

worldmap_file = "dat/maps/ne_110m_land"

# Inherit from this to get map drawing functionality
class Worldmap( Program ):

    def __init__( self, user, work, tty, size, origin, params=[] ):
        # Call parent
        super( ).__init__( user, work, tty, size, origin, params )
        ### Init mapstuff ###
        # The shapefile to store
        self.wm_sf = shapefile.Reader( worldmap_file )
        # The bytearray to use while drawing
        self.wm_bar = None

    def run( self ):
        # Configure the bytearray
        self.wm_bar = BitArray( self.size[0] * self.size[1] )
        print( "SIZE: " + str( self.size[0] * self.size[1] ) )
        # Abort if we cannot read this file
        if self.wm_sf.shapeType != shapefile.POLYGON:
            self.error( "unable to read this map file type" )
            return self.kill
        # Calculate the transforms
        self.wm_xmin = self.wm_sf.bbox[0]
        self.wm_ymin = self.wm_sf.bbox[1]
        # Calculate the skews
        self.wm_xskw = ( self.wm_sf.bbox[2] - self.wm_xmin ) / self.size[0]
        self.wm_yskw = ( self.wm_sf.bbox[3] - self.wm_ymin ) / self.size[1]
        # Loop through all the polygons
        for shp in self.wm_sf.shapes( ):
            # Skip non polygon shapes
            if shp.shapeType != shapefile.POLYGON: continue
            # Previous point
            lpnt = None
            # First point
            fpnt = None
            # Read all the points
            for i, pnt in enumerate( shp.points ):
                # Is this a new part?
                if i in shp.parts:
                    # Finish last part
                    if fpnt is not None:
                        self.setLine( lpnt[0], lpnt[1], fpnt[0], fpnt[1] )
                    # Set new first part
                    fpnt = pnt
                else:
                    # Plot the line
                    self.setLine( lpnt[0], lpnt[1], pnt[0], pnt[1] )
                # Set new last point
                lpnt = pnt
            # Finish last polyon
            self.setLine( lpnt[0], lpnt[1], fpnt[0], fpnt[1] )
        # Draw img for debug
        for y in range( 0, self.size[1] ):
            for x in range( 0, self.size[0] ):
                if self.getPix( x, y ):
                    self.printl( "*" )
                else:
                    self.printl( " " )
            self.println( )
        # We're done here
        return self.kill

    # Set a pixel
    def setPix( self, x, y ):
        # Normalize
        x = int( x )
        y = int( self.size[1] - y )
        # Make sure this is in bounds
        if x > 0 and x < self.size[0] and y > 0 and y < self.size[1]:
            # Flip the bit
            print( "PLOT: %d, %d" % (x, y) )
            self.wm_bar[y * self.size[0] + x] = 1

    # Get a pixel
    def getPix( self, x, y ):
        # Return the bit
        return self.wm_bar[y * self.size[0] + x]

    # Bresenham's line algorithm
    # https://en.wikipedia.org/wiki/Bresenham%27s_line_algorithm
    def setLine( self, xa, ya, xb, yb ):
        # Orient everything
        xa = int( ( xa - self.wm_xmin ) / self.wm_xskw )
        ya = int( ( ya - self.wm_ymin ) / self.wm_yskw )
        xb = int( ( xb - self.wm_xmin ) / self.wm_xskw )
        yb = int( ( yb - self.wm_ymin ) / self.wm_yskw )
        # Calculate Delta X & Y
        dx = xb - xa
        dy = yb - ya
        # This formula doesn't work with vertical lines
        if dx == 0:
            # Draw each pixel of this line
            for iy in range( ya, yb ):
                # Draw the vertical line
                self.setPix( xa, iy )
        else:
            # Calculate the Delta Error
            derr = abs( dy / dx )
            # Starting error
            err = 0
            # Starting y
            iy = ya
            # Iterate through x
            for ix in range( xa, xb ):
                # Plot this point
                self.setPix( ix, iy )
                # Calculate new error
                err += derr
                while err >= 0.5:
                    # Compensate for error
                    if dy >= 0:
                        iy += 1
                    else:
                        iy -= 1
                    err -= 0.1
