#!/usr/bin/env python3

####################################
# Architect & Underground (c) 2017 #
#                                  #
# Prune and format raw city data   #
####################################

# Expects city data in the following format
# https://www.maxmind.com/en/free-world-cities-database
# The specific file we're using
# http://download.maxmind.com/download/worldcities/worldcitiespop.txt.gz
# NOTE: Make sure this file is in ascii encoding!
# If 'file -i worldcitiespop.txt' returns 'iso-8859-1' then you need to run:
# iconv -c -f "iso-8859-1" -t "us-ascii" -t "us-ascii" worldcitiespop.txt -o worldcitiespop.out
# This command converts worldcitiespop.txt to ASCII then simply rename the output file

import sys
import time

# Do not load this as a module!
if __name__ != "__main__":
    sys.exit( "Do not load prunecities.py as a module!" )
# Make sure an argument was given
elif len( sys.argv ) != 3:
    sys.exit( "usage: ./prunecities.py <inFile> <outFile>" )

# Stats about how much we changed
total = 0
trunc = 0

starttime = time.time( )

# We're good to go!
with open( sys.argv[1] ) as ifd:
    # Make sure the file is in the correct format
    header = next( ifd ).strip( )
    if header != "Country,City,AccentCity,Region,Population,Latitude,Longitude":
        sys.exit( "Invalid input file header: %s" % header )
    # Open the file to output to
    with open( sys.argv[2], "w" ) as ofd:
        # Iterate through each city
        for cline in ifd:
            # Increment total count
            total += 1
            # Split the data
            city = cline.strip( ).split( "," )
            # Citys with too small of a population should be removed
            if not city[4]:
                # Increment truncate count and continue
                trunc += 1
                continue
            # Remove the 'real' name of the city
            del city[2]
            # Write the city to the output file
            ofd.write( ",".join( city ) + "\n" )

print( "Finished, stats:" )
print( "Processed %s cities" % total )
print( "Truncated %s cities" % trunc )
print( "Operation lasted %s seconds" % ( time.time( ) - starttime ) )
