#!/usr/bin/env python3

####################################
# Architect & Underground (c) 2017 #
#                                  #
# General purpose system programs  #
####################################

# NOTE: All latitude and longitudes are in DEGREES

from init import *

import math
import random
import csv

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
        # Draw an X on the Host
        self.drawString( self.getXY( self.host.geoloc["location"] ), "X" )
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
                        self.setLine( lpnt, fpnt )
                    # Set new first point
                    fpnt = pnt
                else:
                    # Plot the line
                    self.setLine( lpnt, pnt )
                # Set new last point
                lpnt = pnt
            # Finish last polyon
            self.setLine( lpnt, fpnt )

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

    # Top left cell is (0, 0)
    # Draw a string on the screen at position
    def drawString( self, pts, str ):
        # Move cursor to position and print text
        self.printl( ansi_move( pts[1], pts[0] ) + str )


    # Set a pixel
    def setPix( self, pts ):
        # Normalize
        x = round( pts[0] )
        y = round( ( self.size[1] * 2 ) - pts[1] )
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
    def setLine( self, pta, ptb ):
        # Orient everything
        xa = ( pta[0] - self.wm_xmin ) / self.wm_xskw
        ya = ( pta[1] - self.wm_ymin ) / self.wm_yskw
        xb = ( ptb[0] - self.wm_xmin ) / self.wm_xskw
        yb = ( ptb[1] - self.wm_ymin ) / self.wm_yskw
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
                self.setPix( ( xa, iy ) )
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
                self.setPix( ( ix, iy ) )
                # Increment x
                ix += 1

    # Get the corresponding (x, y) coords on the screen of a set lat and lon
    # pts = ( latitude, longitude )
    def getXY( self, pts ):
        # Calculate the x-coordinate
        x = ( pts[1] + 180 ) / 360 * self.size[0]
        # Calculate the y-coordinate
        y = ( 180 - ( pts[0] + 90 ) ) / 180 * self.size[1]
        # Return the rounded xy coords
        return ( round(x), round(y) )

    # Clean up the screen
    def kill( self ):
        # Reset cursor on death
        self.printl( ansi_move( self.size[1], 0 ) )
        # Call our parent function
        super( ).kill( )

# Get the distance between two ( latitude, longitudes ) in kilometers
def getGeoDist( pta, ptb ):
    # Python uses radians, not degrees for sin and cos
    lata = math.radians( pta[0] )
    lona = math.radians( pta[1] )
    latb = math.radians( ptb[0] )
    lonb = math.radians( ptb[1] )
    # Get the delta lat and lon
    dlat = latb - lata
    dlon = lonb - lona
    # First part
    tmp = math.sin(dlat / 2)**2 + math.cos(lata)
    # Second part
    tmp *= math.cos(latb) * math.sin(dlon / 2)**2
    # 12746 is the diameter of the earth in kilometers
    return 12746 * math.atan2(math.sqrt(tmp), math.sqrt(1 - tmp))

# Convert kilometers to miles
def getMiles( km ):
    # A mile is 1.6 times longer then a kilometer
    return 1.6 * km

# Get the dict from a row in longer list
def getCity( city ):
    # Build and return the dictionary
    return {
        # Country code for this city
        "country": city[0],
        # Name of the city in standard ASCII
        "name": city[1],
        # Non-ASCII name of the city (we can't print this so its not used)
#       "realname": city[2],
        # Region (state) code for this city
        "region": city[3],
        # Population
        "population": city[4],
        # Location (latitude, longitude)
        "location": ( float( city[5] ), float( city[6] ) )
    }

# Returns a dict containing info regarding a city
# string  | name ........... the exact name of the city to search for
# boolean | includeMinor ... whether to include cities without population sizes
def getCityName( name, includeMinor=False ):
    # Read the cities data file
    with open( "dat/worldcitiespop.txt" ) as fd:
        # Iterate over each entry
        for fline in fd:
            # Split the data on commas
            city = fline.strip( ).split( "," )
            # Check if the plaintext name matches
            if city[1].lower( ) == name.lower( ) and ( city[4] or includeMinor ):
                # Build and return the dictionary
                return getCity( city )
        # City not found
        return None

# Get a random city with a population greater than size
# Major City: size=3 :          population > 15,000
# Avg.  City: size=2 : 15,000 > population >  5,000
# Small City: size=1 :  5,000 > population >  1,000
#       Town: size=0 :  1,000 > population
def getCityRandom( size=0 ):
    # Make sure a correct size was given
    if size < 0 or size > 3: raise IndexError( "invalid city size" )
    # List of population sizes
    psize = [ 0, 1000, 5000, 15000, 999999999 ]
    # Store all the valid cities
    clist = []
    # Read the cities data file
    with open( "dat/worldcitiespop.txt" ) as fd:
        # Iterate through each city
        for fline in fd:
            # Split on commas
            city = fline.strip( ).split( "," )
            # Check if this city has enough people
            if ( city[4] and float( city[4] ) > psize[size]
            and float( city[4] ) < psize[size + 1] ):
                # Add this city to the list
                clist.append( getCity( city ) )
    # Get a random element
    i = random.randint( 0, len( clist ) - 1 )
    # Return that element
    return clist[i]
