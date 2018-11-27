#!/bin/bash

# This starts the Phreaknet server on BX9 and binds it to the correct IP
pipenv run ./engine.py "64.13.139.230" $@
