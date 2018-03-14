#!/bin/bash

# This program builds a file full of random data and store it in ../dat/progs
# The first parameter should be the program name (lowercase) which should
# match the name of the python class.
# The second parameter should be the number of bytes.

# NOTE: Remember to [git add] the file once it's generated so others can run
# your program.

if [ $# -gt 0 ]; then
    head -c $2 < "/dev/urandom" > "../dat/progs/$1"
else
    echo "usage: ./makeprog.sh <filename> <number of bytes>"
fi
