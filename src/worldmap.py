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

worldmap_charmap = [ " ", ".", ",", "_", "'", "|", "/", "J",
                     "`", "\\","|", "L", "\"","7", "r", "o" ]

# Inherit from this to get map drawing functionality
class Worldmap( Program ):

    def run( self ):
        # Start the map reader
        self.initmap( "dat/maps/ne_110m_land" )
        # Build the map
        self.buildmap( )
        # Draw the map
        self.drawmap( )
        # Finish
        return self.kill

    def initmap( self, mapfile ):
        # Try to load a shapefile
        try:
            # The shapefile to stroe
            self.wm_sf = shapefile.Reader( mapfile )
        except shapefile.ShapefileException:
            # Shapefile could not be located
            self.wm_sf = None
            return False
        # Make sure the shapefile is a polygon file
        if self.wm_sf.shapeType != shapefile.POLYGON: return False
        # The bytearray to use while drawing
        self.wm_bar = BitArray( self.size[0] * self.size[1] * 4 )
        # The transforms
        self.wm_xmin = self.wm_sf.bbox[0]
        self.wm_ymin = self.wm_sf.bbox[1]
        # The sizes
        self.wm_width  = self.wm_sf.bbox[2] - self.wm_xmin
        self.wm_height = self.wm_sf.bbox[3] - self.wm_ymin
        # Calculate the skews
        self.wm_xskw = self.wm_width / (self.size[0] * 2)
        self.wm_yskw = self.wm_height / (self.size[1] * 2)
        # Return success
        return True

    def buildmap( self ):
        # Make sure theres a file to read
        if self.wm_sf is None: return
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
                    # Set new first point
                    fpnt = pnt
                else:
                    # Plot the line
                    self.setLine( lpnt[0], lpnt[1], pnt[0], pnt[1] )
                # Set new last point
                lpnt = pnt
            # Finish last polyon
            self.setLine( lpnt[0], lpnt[1], fpnt[0], fpnt[1] )

    # Draw the ASCII representation of this map
    def drawmap( self ):
        # Make sure there's something to do
        if self.wm_sf is None: return
        # Iterate through the entire screen
        for y in range( 0, self.size[1] * 2, 2 ):
            aln = ""
            for x in range( 0, self.size[0] * 2, 2 ):
                # Find the character represented by each 2x2 cell
                char  = self.getPix( x, y ) * 8
                char += self.getPix( x + 1, y ) * 4
                char += self.getPix( x, y + 1 ) * 2
                char += self.getPix( x + 1, y + 1 )
                # Add the char to this line
                aln += worldmap_charmap[char]
            # Print this line
            self.println( aln )

    # Set a pixel
    def setPix( self, x, y ):
        # Normalize
        x = round( x )
        y = round( ( self.size[1] * 2 ) - y )
        # Make sure this is in bounds
        if x > 0 and x < self.size[0] * 2 and y > 0 and y < self.size[1] * 2:
            # Flip the bit
            self.wm_bar[y * ( self.size[0] * 2 ) + x] = 1

    # Get a pixel
    def getPix( self, x, y ):
        # Return the bit
        return self.wm_bar[y * ( self.size[0] * 2 ) + x]

    # The line drawing algorithm
    # https://en.wikipedia.org/wiki/Line_drawing_algorithm
    def setLine( self, xa, ya, xb, yb ):
        # Orient everything
        xa = ( xa - self.wm_xmin ) / self.wm_xskw
        ya = ( ya - self.wm_ymin ) / self.wm_yskw
        xb = ( xb - self.wm_xmin ) / self.wm_xskw
        yb = ( yb - self.wm_ymin ) / self.wm_yskw
        # Switch the points if one is less than the other
        if xb < xa:
            tmp = xa
            xa = xb
            xb = tmp
            tmp = ya
            ya = yb
            yb = tmp
        # Calculate Delta X & Y
        dx = xb - xa
        dy = yb - ya
        # This formula doesn't work with vertical lines
        if dx == 0:
            # Starting y
            iy = ya
            # Draw each pixel of this line
            while iy <= yb:
                # Draw the pixel
                self.setPix( xa, iy )
                # Increment y
                iy += 1
        else:
            # Starting x
            ix = xa
            # Draw the line
            while ix <= xb:
                # Calculate the y coord
                iy = yb + dy * ( ix - xb ) / dx
                # Draw the pixel
                self.setPix( ix, iy )
                # Increment x
                ix += 1
