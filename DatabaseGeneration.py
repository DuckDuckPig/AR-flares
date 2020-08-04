#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
DESCRIPTION: This script reads the entire Fits AR Database files that are 
             downloaded and stored in folders titled with AR numbers and parses
             out data that is not ideal based on : 
                 Number of NaN's in the image data, 
                 Logitude of AR centroid, 
                 Latitude of AR centroid
             We also pre-pend the NOAA AR number to the front of each file name
             The data can then be split into N number of classes using a 
             user-defined function for classification, We allow flare size, 
             and time window to be selected for class outputs
Created on Fri Mar  8 10:16:37 2019

@author: tvincent
"""
import os
import os.path
import imageio
import numpy as np
import shutil
from datetime import datetime
from datetime import timedelta
from astropy.io import fits

########################################################################
####################### SET UP CONFIG DICTIONARY #######################
########################################################################

cfg = {
       "classification": {"flareTime": 24, # flare time range to classify as flare
                          "flareSize": "C"   # String with minimum flare size only one allowed
                         }, 
       "nans"         : 0,         # number of nans allowed in images 
       "lon"          : 60,        # Longitude in degrees
       "lat"          : 60,        # Latitude of centroid in degrees
       "staticPrepend": "",          # Static string to prepend to file names (i.e. projectData1)
       "staticApend"  : "",          # Static strihng to append to file names (i.e. Created10_2_18)
       "prependNoaa"  : True,        # Flag to prepend noaa AR number to file name
       "newDirectory" : True,        # Flag to duplicate data into new directory, false moves data in path, true creates new data
       "newDataDirectory" : "/home/tvincent/Desktop/Research/Research/active_regions/C_24hr/",    # String for new directory path INCLUDE FINAL /
       "dataDirectory": "/home/tvincent/Desktop/Research/Research/active_regions/1302/", #"/mnt/store/active_regions" # Path to fits data in NOAA AR number folders INCLUDE FINAL /
       "srsDirectory" : "/home/tvincent/Desktop/Research/Research/SRS/",
       "eventList"    : "/mnt/store/AR_Database/eventList.txt",
       "labelFilePath": "/home/tvincent/Desktop/Research/Research/active_regions/c_24hrLabels.txt"
       }
print(cfg)

########################################################################
####################### BEGIN FUNCTION DEFINITION ######################
########################################################################

def nanSeparation( cfg ):
    
    nanFileArray = []
    i = 0
    for direc in os.listdir(cfg["dataDirectory"]):
        print('')
        print('***************************************************************')
        print(direc)
        print('***************************************************************')
        print('')
        os.chdir(cfg["dataDirectory"] +'/'+direc)
        for file in os.listdir(cfg["dataDirectory"]+'/'+direc):
            if ('.fits' in file):
                hdulist = fits.open(file)
                hdulist.verify('silentfix')
                
                fitsIm = hdulist[1].data
                
                numNan = np.isnan(fitsIm).sum()
                if numNan > cfg["nans"]:
                    i=i+1
                    
                    nanFileArray.append(file)
                    
    print('Number of NaN Files Removed: ' + str(i))
    return nanFileArray
    
# END nanSeparation FUNCTION
###############################################################################
    
def latLonSeparation( nanFileArray, cfg ):
    badLatLonFileArray = []
    
    # Loop through the list of folders containing text files
    for srsFolder in os.listdir(cfg["srsDirectory"]): 
        
        # Loop through each text file in the folders
        for srsText in os.listdir(cfg["srsDirectory"] + srsFolder):
            date = srsText.split('S')[0]
            
            # catch for weird case where a . ends up infront of the date (no 
            # clue why it shows up)
            try:
                int(date)
            except:
                date = date.split('.')[1]
            # Good data begins at the beginning of May 2010, so we want to 
            # ignore any data before that date
            if (int(date) < 20100501):
                pass
            else:
            
                with open((cfg["srsDirectory"] + srsFolder + "/" + srsText),'r') as f:
                    lines = f.readlines()
                    for index, line in enumerate(lines):
                        # IA will be in the section header after the AR data we care about
                        if "IA" in line:
                            break
                        # Nmbr will be in the section header we care about
                        elif 'Nmbr' in line:
                            i = 1
                            while 'IA' not in lines[index + i] and 'None' not in lines[index + i]:
                                # Split the lines by spaces to find the latatude and longitude of the centroid of the active region
                                a = lines[index + i].split(' ')
                                NoaaNum = a[0]
                                lon = a[1]
                                if 'W' in lon:
                                    lat = lon.split('W')[0] # latitude is left of the Lon direction
                                    lon = lon.split('W')[1]
                                elif 'E' in lon:
                                    lat = lon.split('E')[0]
                                    lon = lon.split('E')[1]
                                if 'N' in lat:
                                    lat = lat.split('N')[1]
                                elif 'S' in lat:
                                    lat = lat.split('S')[1]
                                
                                # Compare to configured value
                                if (int(lon) >= int(cfg["lon"])) or (int(lat) >= int(cfg["lat"])):

                                    badLatLonFileArray.append(NoaaNum + '-' + 'hmi.M_720s.'+date)
                                # Increment for fun
                                i = i + 1
    print('Number of lat/lon files removed: ' + str(i))
    return badLatLonFileArray

# END nanSeparation FUNCTION
###############################################################################
    
def createDatabase(nanFileArray, badFileArray, cfg ):
    filesMoved = []
    i = 0

    print("*****Moving Valid Data*****")
    # Loop over AR folders
    for direc in os.listdir(cfg["dataDirectory"]):
    
        os.chdir(cfg["dataDirectory"] + direc + '/')
        print("********************" + str(direc)+ "*************************")
        # Loop over fits files in folders
        for fit in os.listdir(cfg["dataDirectory"] + direc + '/'):
            
            # Check for prepend string
            if cfg["prependNoaa"] is True:
                newFit = str(direc) + '-' + str(fit)
            else:
                newFit = fit
                
            badFitChecker = fit.split('_')[0] + '_'+ fit.split('_')[1]
                
            # Check that the file isnt one of our NaN or bad files    
            if (fit not in nanFileArray) and (badFitChecker not in badFileArray) and ('.fits' in fit):
                i = i+1
                hdulist = fits.open(fit)
                hdulist.verify('silentfix')
                if not os.path.exists(cfg["newDataDirectory"]):
                    os.mkdir(cfg["newDataDirectory"])                

                if ( cfg["newDirectory"] ) and ( not os.path.exists(cfg["newDataDirectory"] + str(direc) + '/' + str(fit)) ):
                    shutil.copy( cfg["dataDirectory"] + str(direc) + '/' + str(fit) , cfg["newDataDirectory"] + '/' + newFit )
                        
                elif not os.path.exists(cfg["newDataDirectory"] + str(direc) + '/' + str(fit)):
                    shutil.move( cfg["dataDirectory"] + '/' + str(direc) + '/' + str(fit) , cfg["newDataDirectory"] + '/' + str(direc) + '-' + str(fit) )
                    
                filesMoved.append(newFit)        
            else:
                print(fit + ' ' + 'IS BAD\n')
                
    return filesMoved
    
# END createDatabase FUNCTION
###############################################################################
    

def createLabelCsv( filesMoved, cfg ):
    flareFiles = []
    notFlareFiles = []
    
    with open(cfg["eventList"],'r') as f: # eventList contains all flares
        for line in f: # loop over all events
            a = line.split(",") # split current line by commas
            if ('C' in a[3]) or ('M' in a[3]) or ('X' in a[3]): # only C, M, or X flares
                noaa = a[2] # strip off NOAA AR from current line
                eventTime = a[1] # strip off time from current line
                flareDate0 = a[0] # strip off date from current line
                flareDate = flareDate0.split(" ") # split date into year, month, day
                
                b = list(eventTime) # cast event time as list
                if (not b) or ('/' in b):
                    pass
                else:
                    if len(b) is 5:
                        hours = b[1] + b[2] # strip off hours
                        mins = b[3] + b[4] # strip off minutes
                    elif len(b) is 4:
                        hours = b[0] + b[1] # strip off hours
                        mins = b[2] + b[3] # strip off minutes

                    FlareDateTime = datetime(year = int(flareDate[0]), month = int(flareDate[1]), day = int(flareDate[2]), hour=int(hours), minute=int(mins), second=0) # define datetime object associated with peak flare time
                
                    tdelta = timedelta(hours = cfg["classification"]["flareTime"]) # time window over which to consider flaring
    
                    os.chdir(cfg["newDataDirectory"]) # cd to New Directory
                    for fitsF in os.listdir(cfg["newDataDirectory"]): # loop over all contents of current NOAA AR directory
                        if noaa in fitsF:
                            try: 
                                fitsTime_str = fitsF.split('.')[2] # strip off date-time string from fits file
                                fitsTime = datetime(year = int(fitsTime_str[0:4]), month = int(fitsTime_str[4:6]), day = int(fitsTime_str[6:8]), hour=int(fitsTime_str[9:11]), minute=int(fitsTime_str[11:13]), second=0) # define datetime object associated with fits file time
                                if FlareDateTime-fitsTime<tdelta and FlareDateTime>fitsTime: # fits file time is within 24 hours previous of peak flare time
                                    if (fitsF) not in flareFiles: # check if file has already been assigned label of flare
                                        flareFiles.append(fitsF) # append new filename to list  
                                        
                                elif (fitsF not in notFlareFiles) and (fitsF not in flareFiles):
                                    notFlareFiles.append(fitsF) # append new filename to list
                            except:
                                pass

    with open(cfg["labelFilePath"],'w') as f:
        for item in flareFiles:
            f.write(item + ',' + 'flare\n')
        for item1 in notFlareFiles:
            f.write( item1 + ',' + 'not_flare\n')
    return flareFiles, notFlareFiles
    
# END createLabelCSV FUNCTION
###############################################################################

###############################################################################
##################### END FUNCTION DEFINITION #################################
###############################################################################

########################################################################
########################## SEPERATE NAN FILES ##########################
########################################################################
print("*** CHECKING FILES FOR MORE THAN " + str(cfg["nans"]) + " NANS ***")
nanFileArray = nanSeparation( cfg )

########################################################################
######################### SEPERATE LON AND LAT #########################
########################################################################
print("*** CHECKING FILES FOR LATITUDES INSIDE " + str(cfg["lat"]) + " AND LONGITUDES INSIDE " + str(cfg["lon"]) + " ***")
badFileArray = latLonSeparation( [], cfg )

########################################################################
########################### COPY GOOD FILES ############################
########################################################################
print("*** COPY/MOVING DATA TO " + cfg["newDataDirectory"] + " ***")
filesMoved = createDatabase( nanFileArray, badFileArray, cfg )

########################################################################
###################### GENERATE CLASSIFICATION CSV #####################
########################################################################
print("*** GENERATING LABEL CSV FILE ***")
flareFiles, notFlareFiles = createLableCsv( filesMoved, cfg )
print("\n\n\n*** DONE ***\n\n\n")

# END SCRIPT
###############################################################################
