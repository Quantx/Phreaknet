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


# Dict of ISO3166 2-letter country codes, alphabetized by country name
country_codes = {
    'AF': 'AFGHANISTAN', 'AX': 'ALAND ISLANDS', 'AL': 'ALBANIA', 'DZ': 'ALGERIA', 'AS': 'AMERICAN SAMOA', 'AD': 'ANDORRA', 'AO': 'ANGOLA', 'AI': 'ANGUILLA', 'AQ': 'ANTARCTICA', 'AG': 'ANTIGUA AND BARBUDA', 'AR': 'ARGENTINA', 'AM': 'ARMENIA', 'AW': 'ARUBA', 'AU': 'AUSTRALIA', 'AT': 'AUSTRIA', 'AZ': 'AZERBAIJAN',
    'BS': 'BAHAMAS', 'BH': 'BAHRAIN', 'BD': 'BANGLADESH', 'BB': 'BARBADOS', 'BY': 'BELARUS', 'BE': 'BELGIUM', 'BZ': 'BELIZE', 'BJ': 'BENIN', 'BM': 'BERMUDA', 'BT': 'BHUTAN', 'BO': 'BOLIVIA, PLURINATIONAL STATE OF', 'BQ': 'BONAIRE, SINT EUSTATIUS AND SABA', 'BA': 'BOSNIA AND HERZEGOVINA', 'BW': 'BOTSWANA', 'BV': 'BOUVET ISLAND', 'BR': 'BRAZIL', 'IO': 'BRITISH INDIAN OCEAN TERRITORY', 'BN': 'BRUNEI DARUSSALAM', 'BG': 'BULGARIA', 'BF': 'BURKINA FASO', 'BI': 'BURUNDI',
    'KH': 'CAMBODIA', 'CM': 'CAMEROON', 'CA': 'CANADA', 'CV': 'CAPE VERDE', 'KY': 'CAYMAN ISLANDS', 'CF': 'CENTRAL AFRICAN REPUBLIC', 'TD': 'CHAD', 'CL': 'CHILE', 'CN': 'CHINA', 'CX': 'CHRISTMAS ISLAND', 'CC': 'COCOS (KEELING) ISLANDS', 'CO': 'COLOMBIA', 'KM': 'COMOROS', 'CG': 'CONGO', 'CD': 'CONGO, THE DEMOCRATIC REPUBLIC OF THE', 'CK': 'COOK ISLANDS', 'CR': 'COSTA RICA', 'CI': 'COTE D\'IVOIRE', 'HR': 'CROATIA', 'CU': 'CUBA', 'CW': 'CURACAO', 'CY': 'CYPRUS', 'CZ': 'CZECH REPUBLIC',
    'DK': 'DENMARK', 'DJ': 'DJIBOUTI', 'DM': 'DOMINICA', 'DO': 'DOMINICAN REPUBLIC',
    'EC': 'ECUADOR', 'EG': 'EGYPT', 'SV': 'EL SALVADOR', 'GQ': 'EQUATORIAL GUINEA', 'ER': 'ERITREA', 'EE': 'ESTONIA', 'ET': 'ETHIOPIA',
    'FK': 'FALKLAND ISLANDS (MALVINAS)', 'FO': 'FAROE ISLANDS', 'FJ': 'FIJI', 'FI': 'FINLAND', 'FR': 'FRANCE', 'GF': 'FRENCH GUIANA', 'PF': 'FRENCH POLYNESIA', 'TF': 'FRENCH SOUTHERN TERRITORIES',
    'GA': 'GABON', 'GM': 'GAMBIA', 'GE': 'GEORGIA', 'DE': 'GERMANY', 'GH': 'GHANA', 'GI': 'GIBRALTAR', 'GR': 'GREECE', 'GL': 'GREENLAND', 'GD': 'GRENADA', 'GP': 'GUADELOUPE', 'GU': 'GUAM', 'GT': 'GUATEMALA', 'GG': 'GUERNSEY', 'GN': 'GUINEA', 'GW': 'GUINEA-BISSAU', 'GY': 'GUYANA',
    'HT': 'HAITI', 'HM': 'HEARD ISLAND AND MCDONALD ISLANDS', 'VA': 'HOLY SEE (VATICAN CITY STATE)', 'HN': 'HONDURAS', 'HK': 'HONG KONG', 'HU': 'HUNGARY',
    'IS': 'ICELAND', 'IN': 'INDIA', 'ID': 'INDONESIA', 'IR': 'IRAN, ISLAMIC REPUBLIC OF', 'IQ': 'IRAQ', 'IE': 'IRELAND', 'IM': 'ISLE OF MAN', 'IL': 'ISRAEL', 'IT': 'ITALY',
    'JM': 'JAMAICA', 'JP': 'JAPAN', 'JE': 'JERSEY', 'JO': 'JORDAN',
    'KZ': 'KAZAKHSTAN', 'KE': 'KENYA', 'KI': 'KIRIBATI', 'KP': 'KOREA, DEMOCRATIC PEOPLE\'S REPUBLIC OF', 'KR': 'KOREA, REPUBLIC OF', 'KW': 'KUWAIT', 'KG': 'KYRGYZSTAN',
    'LA': 'LAO PEOPLE\'S DEMOCRATIC REPUBLIC', 'LV': 'LATVIA', 'LB': 'LEBANON', 'LS': 'LESOTHO', 'LR': 'LIBERIA', 'LY': 'LIBYAN ARAB JAMAHIRIYA', 'LI': 'LIECHTENSTEIN', 'LT': 'LITHUANIA', 'LU': 'LUXEMBOURG',
    'MO': 'MACAO', 'MK': 'MACEDONIA, THE FORMER YUGOSLAV REPUBLIC OF', 'MG': 'MADAGASCAR', 'MW': 'MALAWI', 'MY': 'MALAYSIA', 'MV': 'MALDIVES', 'ML': 'MALI', 'MT': 'MALTA', 'MH': 'MARSHALL ISLANDS', 'MQ': 'MARTINIQUE', 'MR': 'MAURITANIA', 'MU': 'MAURITIUS', 'YT': 'MAYOTTE', 'MX': 'MEXICO', 'FM': 'MICRONESIA, FEDERATED STATES OF', 'MD': 'MOLDOVA, REPUBLIC OF', 'MC': 'MONACO', 'MN': 'MONGOLIA', 'ME': 'MONTENEGRO', 'MS': 'MONTSERRAT', 'MA': 'MOROCCO', 'MZ': 'MOZAMBIQUE', 'MM': 'MYANMAR',
    'NA': 'NAMIBIA', 'NR': 'NAURU', 'NP': 'NEPAL', 'NL': 'NETHERLANDS', 'NC': 'NEW CALEDONIA', 'NZ': 'NEW ZEALAND', 'NI': 'NICARAGUA', 'NE': 'NIGER', 'NG': 'NIGERIA', 'NU': 'NIUE', 'NF': 'NORFOLK ISLAND', 'MP': 'NORTHERN MARIANA ISLANDS', 'NO': 'NORWAY',
    'OM': 'OMAN',
    'PK': 'PAKISTAN', 'PW': 'PALAU', 'PS': 'PALESTINIAN TERRITORY, OCCUPIED', 'PA': 'PANAMA', 'PG': 'PAPUA NEW GUINEA', 'PY': 'PARAGUAY', 'PE': 'PERU', 'PH': 'PHILIPPINES', 'PN': 'PITCAIRN', 'PL': 'POLAND', 'PT': 'PORTUGAL', 'PR': 'PUERTO RICO',
    'QA': 'QATAR',
    'RE': 'REUNION', 'RO': 'ROMANIA', 'RU': 'RUSSIAN FEDERATION', 'RW': 'RWANDA',
    'BL': 'SAINT BARTHELEMY', 'SH': 'SAINT HELENA, ASCENSION AND TRISTAN DA CUNHA', 'KN': 'SAINT KITTS AND NEVIS', 'LC': 'SAINT LUCIA', 'MF': 'SAINT MARTIN (FRENCH PART)', 'PM': 'SAINT PIERRE AND MIQUELON', 'VC': 'SAINT VINCENT AND THE GRENADINES', 'WS': 'SAMOA', 'SM': 'SAN MARINO', 'ST': 'SAO TOME AND PRINCIPE', 'SA': 'SAUDI ARABIA', 'SN': 'SENEGAL', 'RS': 'SERBIA', 'SC': 'SEYCHELLES', 'SL': 'SIERRA LEONE', 'SG': 'SINGAPORE', 'SX': 'SINT MAARTEN (DUTCH PART)', 'SK': 'SLOVAKIA', 'SI': 'SLOVENIA', 'SB': 'SOLOMON ISLANDS', 'SO': 'SOMALIA', 'ZA': 'SOUTH AFRICA', 'GS': 'SOUTH GEORGIA AND THE SOUTH SANDWICH ISLANDS', 'SS': 'SOUTH SUDAN', 'ES': 'SPAIN', 'LK': 'SRI LANKA', 'SD': 'SUDAN', 'SR': 'SURINAME', 'SJ': 'SVALBARD AND JAN MAYEN', 'SZ': 'SWAZILAND', 'SE': 'SWEDEN', 'CH': 'SWITZERLAND', 'SY': 'SYRIAN ARAB REPUBLIC',
    'TW': 'TAIWAN, PROVINCE OF CHINA', 'TJ': 'TAJIKISTAN', 'TZ': 'TANZANIA, UNITED REPUBLIC OF', 'TH': 'THAILAND', 'TL': 'TIMOR-LESTE', 'TG': 'TOGO', 'TK': 'TOKELAU', 'TO': 'TONGA', 'TT': 'TRINIDAD AND TOBAGO', 'TN': 'TUNISIA', 'TR': 'TURKEY', 'TM': 'TURKMENISTAN', 'TC': 'TURKS AND CAICOS ISLANDS', 'TV': 'TUVALU',
    'UG': 'UGANDA', 'UA': 'UKRAINE', 'AE': 'UNITED ARAB EMIRATES', 'GB': 'UNITED KINGDOM', 'US': 'UNITED STATES', 'UM': 'UNITED STATES MINOR OUTLYING ISLANDS', 'UY': 'URUGUAY', 'UZ': 'UZBEKISTAN',
    'VU': 'VANUATU', 'VE': 'VENEZUELA, BOLIVARIAN REPUBLIC OF', 'VN': 'VIET NAM', 'VG': 'VIRGIN ISLANDS, BRITISH', 'VI': 'VIRGIN ISLANDS, U.S.',
    'WF': 'WALLIS AND FUTUNA', 'EH': 'WESTERN SAHARA',
    'YE': 'YEMEN',
    'ZM': 'ZAMBIA', 'ZW': 'ZIMBABWE',
}

# Chars used when drawing the map
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
        self.drawString( self.getXY( self.host.get_location( ) ), "X" )
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
        self.println( ansi_move( self.size[1], 0 ) )
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

# Resolve an ISO country code
def resolveCountry( code ):
    # lower cased capitalized country string
    cstr = country_codes.get( code.upper( ), "unknown" ).lower( )
    # Uppercase first letter of each word and return
    return " ".join( wrd.capitalize( ) for wrd in cstr.split( ) )

# Get the dict from a row in longer list
def getCity( city ):
    # Do we need to split a string?
    if type( city ) is str:
        city = city.strip( ).split( "," )
    # Build and return the dictionary
    return {
        # Country code for this city
        "iso": city[0],
        # The name of this city's country
        "country": resolveCountry( city[0] ),
        # Name of the city in standard ASCII
        "name": city[1],
        # Region (state) code for this city
        "region": city[2],
        # Population
        "population": int( float( city[3] ) ),
        # Location (latitude, longitude)
        "location": ( float( city[4] ), float( city[5] ) )
    }

# Returns a dict containing info regarding a city
# string  | country ... the country code where this city is located
# string  | region .... the region code where this city is located
# string  | cname ..... the exact name of the city to search for
def getCityName( country, region, cname ):
    # Read the cities data file
    with open( "dat/worldcitiespop.txt" ) as fd:
        # Iterate over each entry
        for fline in fd:
            # Split the data on commas
            city = fline.strip( ).split( "," )
            # Check if the plaintext name matches
            if ( city[0].lower( ) == country.lower( )
            and  city[1].lower( ) == cname.lower( )
            and  city[2].lower( ) == region.lower( ) ):
                # Build and return the dictionary
                return getCity( city )
        # City not found
        return None

# Store a count of any, town, small, medium, and large cities
citySizeCount = [ 0, 0, 0, 0, 0 ]
# Populate this list
def makeCitySizeCount( ):
    # Use the global scope citySizeCount list
    global citySizeCount
    # We already ran this
    if citySizeCount[0] > 0: return
    # List of population sizes
    psize = [ 0, 1000, 5000, 15000, 999999999 ]
    # Read the cities data file
    with open( "dat/worldcitiespop.txt" ) as fd:
        # Iterate through each city
        for fline in fd:
            # Split on commas
            city = fline.strip( ).split( "," )
            # Calculate size of city
            csize = int( float( city[3] ) )
            # Add city to any count
            if csize > psize[0] and csize <= psize[4]: citySizeCount[0] += 1
            # Is it a town?
            if csize > psize[0] and csize <= psize[1]: citySizeCount[1] += 1
            # Is it a small city?
            if csize > psize[1] and csize <= psize[2]: citySizeCount[2] += 1
            # Is it a medium city?
            if csize > psize[2] and csize <= psize[3]: citySizeCount[3] += 1
            # Is it a large city?
            if csize > psize[3] and csize <= psize[4]: citySizeCount[4] += 1

# Get a random city with a population greater than size
# Large  City: size =  3 : Infinity >= population > 15,000
# Medium City: size =  2 :   15,000 >= population >  5,000
# Small  City: size =  1 :    5,000 >= population >  1,000
#        Town: size =  0 :    1,000 >= population >      0
#    Any City: size = -1 : Infinity >= population >      0
def getCityRandom( size=-1 ):
    # Make sure a correct size was given
    if size < -1 or size > 3: raise IndexError( "invalid city size" )
    # Add 1 to the size
    size += 1
    # List of population sizes
    psize = [ 0, 1000, 5000, 15000, 999999999 ]
    # Read a random number from the precalculated list
    out = random.randint( 0, citySizeCount[size] - 1 )
    # Read the cities data file
    with open( "dat/worldcitiespop.txt" ) as fd:
        # Iterate through each city
        for fline in fd:
            # Split on commas
            city = fline.strip( ).split( "," )
            # Calculate size of city
            csize = int( float( city[3] ) )
            # Add city to any count
            if size == 0 and csize > psize[0] and csize <= psize[4]: out -= 1
            # Is it a town?
            if size == 1 and csize > psize[0] and csize <= psize[1]: out -= 1
            # Is it a small city?
            if size == 2 and csize > psize[1] and csize <= psize[2]: out -= 1
            # Is it a medium city?
            if size == 3 and csize > psize[2] and csize <= psize[3]: out -= 1
            # Is it a large city?
            if size == 4 and csize > psize[3] and csize <= psize[4]: out -= 1
            # Return the city
            if out <= 0: return getCity( fline )
    raise IndexError( "unable to locate city" )
