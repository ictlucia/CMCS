[Default]FObject:FSTIR_EuroDollar
""" Compiled: 2021-11-26 10:40:36 """

#__src_file__ = "extensions/futures_maintenance/FSTIR_EuroDollar.py"
#----------------------------------------------------------------------------
#    (c) Copyright 2021 FIS Front Arena. All rights reserved.
#----------------------------------------------------------------------------
#
#Euro dollar definition
#
#This file is stored as a python extension but is not python based
#
#The file format is
#
# <key> = <value>
#
#Spaces inside key and value are kept, surrounding spaces are stripped.
#The format also recognizes # as start of a remark
#

#
#The names here are the internal GUI field names
# Each entry will set a variable in the GUI parameter
#

PageDefBase = SOFR Futures
ISIN ID = 
Strip Length= 2y
Rolling Period=3m
Expiry Day Rule=3rdWednesday
Reference Day= 0d
Quote Type = 100-rate
# You can specify the reference instrument if needed
# or if only one instrument exits in a pagelits that will be selected
Reference Instrument = Cash Flow FutureDefault


LogLevel = Info
#LogEnabled = 1
