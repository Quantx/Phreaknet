#!/usr/bin/env python3

####################################
# Architect & Underground (c) 2017 #
#                                  #
# Handles imports and dependancies #
####################################

#####                            #####
###    IMPORT INIT IN ALL FILES    ###
#####                            #####

global cur_client;
cur_client = None
global cur_host;
cur_host = None

from formating import *
from exceptions import *
from account import *
from software import *
from worldmap import *
from host import *
from hacksoft import *
from companies import *
from phreaknet import *
# Networking should be last
from networking import *
