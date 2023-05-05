# DESCRIPTION: This script reads the entire Fits AR Dataset files that are 
#             downloaded and stored in folders titled with AR numbers and parses
#              out data that is not ideal based on : 
#                  Number of NaN's in the image data, 
#                  Logitude of AR centroid, 
#                  Latitude of AR centroid
#              We also pre-pend the NOAA AR number to the front of each file name
#              The data can then be split into N number of classes using a 
#              user-defined function for classification, We allow flare size, 
#              and time window to be selected for class outputs
# Created on Fri Mar  8 10:16:37 2019
#
# References:
# [1] <Put reference to dataset paper here>
#
# Copyright 2022 Ty Vincent, Laura Boucheron
# This file is part of AR-flares
# 
# AR-flares is free software: you can redistribute it and/or modify it under 
# the terms of the GNU General Public License as published by the Free Software 
# Foundation, either version 3 of the License, or (at your option) any later 
# version.
#
# AR-flares is distributed in the hope that it will be useful, but WITHOUT ANY 
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR 
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with 
# AR-flares. If not, see <https://www.gnu.org/licenses/>. 

import os
import os.path
import imageio
import numpy as np
import shutil
import glob
import pdb
from datetime import datetime
from datetime import timedelta
from astropy.io import fits

########################################################################
####################### SET UP CONFIG DICTIONARY #######################
########################################################################

cfg = {
       'classification': 
           {'flareTime': 24,  # flare time range to classify as flare
           'flareSize': 'C1.0'}, # String with minimum flare size 
       'nans'         : 0,    # number of nans allowed in images 
       'lon'          : 60,   # Longitude of AR centroid in degrees
       'lat'          : 60,   # Latitude of AR centroid in degrees
       'newDataDirectory' : '/mnt/solar_flares/AR_Dataset/Lat60_Lon60_Nans0/', # String for new directory path with trailing /
       'dataDirectory': '/mnt/solar_flares/AR_Dataset/active_regions/', # Path to fits data in NOAA AR number folders with trailing /
       'srsDirectory' : '/mnt/solar_flares/AR_Dataset/SRS/', # Path to SRS data with trailing /
       'eventDirectory': '/mnt/solar_flares/AR_Dataset/Events/', # Path to Events data with trailing / 
       'labelFilePath': '/mnt/solar_flares/AR_Dataset/C1.0_24hr_Labels.txt' # Path to label file
       }
print(cfg)

########################################################################
#################### BEGIN FUNCTION DEFINITION #########################
########################################################################

def latLonSeparation(cfg):

    LatLonFileArray = [] # list to store filenames that don't satisfy lat/lon
    num_latlonFiles = 0 # counter for files that don't satisfy lat/lon

    # Loop through the SRS list of folders containing text files
    for srsFolder in sorted(os.listdir(cfg['srsDirectory'])): 
        # Loop through each text file in the folders
        for srsText in sorted(os.listdir(cfg['srsDirectory'] + srsFolder)):
            date = srsText.split('S')[0] # grab date from filename
            print(date)
            
            # catch for wierd case where a . ends up infront of the date (no 
            # clue why it shows up)
            try:
                int(date)
            except:
                date = date.split('.')[1]
            
            with open((cfg['srsDirectory']+srsFolder+'/'+srsText),'r') as f:
                lines = f.readlines()
                for index, line in enumerate(lines):
                    # IA will be in the section header after the AR data we 
                    # care about
                    if "IA" in line:
                        break
                    # Nmbr will be in the section header we care about
                    elif 'Nmbr' in line:
                        i = 1
                        while 'IA' not in lines[index + i] and \
                              'None' not in lines[index + i]:
                            # Split the lines by spaces to find the latitude 
                            # and longitude of the centroid of the active region
                            a = lines[index + i].split(' ')
                            NoaaNum = a[0]
                            lon = a[1]
                            if 'W' in lon:
                                # latitude is left of the Lon direction
                                lat = lon.split('W')[0] 
                                lon = lon.split('W')[1]
                            elif 'E' in lon:
                                lat = lon.split('E')[0]
                                lon = lon.split('E')[1]
                            if 'N' in lat:
                                lat = lat.split('N')[1]
                            elif 'S' in lat:
                                lat = lat.split('S')[1]
                            
                            # Compare to configured value
                            if (int(lon) >= int(cfg["lon"])) or \
                               (int(lat) >= int(cfg["lat"])):

                                LatLonFileArray.append(NoaaNum+'_'+\
                                                       'hmi.M_720s.'+date)
                                num_latlonFiles = num_latlonFiles + 1
                            i = i+1
    print('Total days of files flagged for lat/lon: ' + str(num_latlonFiles))
    with open('lat'+str(cfg['lat'])+'_lon'+str(cfg['lon'])+'_files.txt',\
              'w') as f:
        for item in LatLonFileArray:
            f.write('%s\n' % item)
    return LatLonFileArray

# END latLonSeparation FUNCTION
###############################################################################

def nanSeparation(latLonFileArray,cfg):
    
    nanFileArray = [] # list to store filenames that don't satisfy NaN check
    num_nanFiles = 0 # counter for files that don't satisfy NaN check
    # loop over all directories in dataset
    for direc in sorted(os.listdir(cfg['dataDirectory'])):
        i = 0 # counter for files per NOAA AR that don't satisfy NaN check
        print('Processing AR '+direc)
        # grab number of NOAA AR files for status update later
        num_files = len(glob.glob(cfg['dataDirectory']+direc+'/*.fits'))
        # loop over all files in NOAA AR directory
        for fit in sorted(glob.glob(cfg['dataDirectory']+direc+'/*.fits')):
            baseFit = os.path.basename(fit)
            baseFit = direc+'_'+baseFit.split('_')[0] + '_'+ baseFit.split('_')[1]
            if baseFit not in latLonFileArray:
                # open file and fix fits errors
                hdulist = fits.open(fit)
                hdulist.verify('silentfix')
                # grab fits image    
                fitsIm = hdulist[1].data
                # count number of NaNs in image
                numNan = np.isnan(fitsIm).sum()
                # if NaNs exceeds specified number, add filename to list
                if numNan > cfg['nans']:
                    num_nanFiles=num_nanFiles+1
                    i = i+1
                    nanFileArray.append(fit)
        # print status
        print(str(i)+'/'+str(num_files)+' NaN Files Flagged in this AR') 
                    
    print('')
    print('Total Number of NaN Files Flagged: ' + str(num_nanFiles))
    print('')
    # save NaN files for faster subsequent processing
    with open('nans'+str(cfg['nans'])+'_files.txt','w') as f:
        for item in nanFileArray:
            # write out as expected NOAA_filename
            f.write('%s_%s\n' % (item.split('/')[-2], item.split('/')[-1]))
    return nanFileArray
    
# END nanSeparation FUNCTION
###############################################################################
    
def createDataset(nanFileArray, latLonFileArray, cfg ):
    f_files = open('files_lat'+str(cfg['lat'])+'_lon'+str(cfg['lon'])+'_nans'+str(cfg['nans'])+'.txt','w')

    num_filesCopied = 0 # counter for total files copied
    num_filesAlreadyThere = 0 # counter for files already there and not copied
    if not os.path.exists(cfg["newDataDirectory"]):
        os.mkdir(cfg["newDataDirectory"])                

    print("*****Copying Valid Data*****")
    # Loop over AR folders
    for direc in sorted(os.listdir(cfg["dataDirectory"])):
    
        print("*********************" + str(direc)+ "**********************")
        i = 0
        j = 0
        # Loop over fits files in folders
        num_files = len(glob.glob(cfg['dataDirectory']+direc+'/*.fits'))
        # ignore last file in AR since from just after midnight last day
        for f in sorted(glob.glob(cfg['dataDirectory']+direc+'/*.fits'))[:-1]:
            fit = os.path.basename(f)
            
            # Prepend NOAA number
            newFit = str(direc) + '_' + str(fit)
                
            # parse out only NOAA_hmi.M_720s.YYMMDD for checking against 
            # Lat/Lon
            dayFit = direc+'_'+fit.split('_')[0] + '_'+ fit.split('_')[1]
                
            # Check that the file isn't one of our NaN or Lat/Lon files    
            if (newFit not in nanFileArray) and (dayFit not in latLonFileArray):
                if not os.path.exists(cfg["newDataDirectory"]+direc):
                    os.mkdir(cfg['newDataDirectory']+direc)
                if not os.path.exists(cfg["newDataDirectory"]+direc+'/'+newFit):
                    shutil.copy(cfg["dataDirectory"]+direc+'/'+fit,\
                                cfg["newDataDirectory"]+'/'+direc+'/'+newFit)
                    num_filesCopied = num_filesCopied + 1
                    i = i+1
                    f_files.write(newFit+'\n')
                else:
                    num_filesAlreadyThere = num_filesAlreadyThere + 1
                    j = j+1
                    f_files.write(newFit+'\n')
            else:
                pass
        print('    Copied '+str(i)+'/'+str(num_files)+' files and '+\
              str(j)+' files were already there')
    f_files.close()            
    print('')
    print('Copied '+str(num_filesCopied)+' total files')
    print('Left '+str(num_filesAlreadyThere)+' files already there')
    print('')
    
# END createDataset FUNCTION
###############################################################################

def createEventList(cfg):
    fwrite = open('eventList.txt','w')
    event_dirs = sorted(glob.glob(cfg['eventDirectory']+'/*'))
    for event_dir in event_dirs:
        event_files = sorted(glob.glob(event_dir+'/*.txt'))
        for event_file in event_files:
            with open(event_file,'r') as f:
                for line in f:
                    if ':Date:' in line:
                        date = (line.split(':Date: ')[1]).rstrip()
                    if 'XRA' in line:
                        peakTime = line[18:22]
                        noaaNum = line[-5:].rstrip()
                        flare = line[58:62].rstrip()
                        if noaaNum=='' or date=='' or flare=='':
                            pass
                        else:
                            fwrite.write(date+','+peakTime+','+noaaNum+','+\
                                         flare+'\n')
                                
    fwrite.close()

# END createEventList FUNCTION
###############################################################################

def createLabelCsv( filesMoved, cfg ):
    flareFiles = []
    flareSizes = []
    
    if os.path.exists(cfg['classification']['flareSize']+'_'+\
                      str(cfg['classification']['flareTime'])+\
                      'hr_flareFiles.txt'):
        print('Using existing file list for '+
              cfg['classification']['flareSize']+', '+\
              str(cfg['classification']['flareTime'])+' hour flares')
        print('To generate a new file list, delete existing file '+\
              cfg['classification']['flareSize']+'_'+\
              str(cfg['classification']['flareTime'])+'hr_flareFiles.txt')
        print('')
        with open(cfg['classification']['flareSize']+'_'+\
                 str(cfg['classification']['flareTime'])+\
                 'hr_flareFiles.txt','r') as f:
            for line in f:
                line = line.rstrip()
                flareFiles.append(line.split(',')[0])
                flareSizes.append(line.split(',')[1])
    else: 
        with open('eventList.txt','r') as f: # eventList contains all flares
            for line in f: # loop over all events
                line = line.split(',') # split current line by commas
                # only flares of class greater than or equal to specified flare 
                # class and flare sizes greater than or equal to specified 
                # flare size should be considered
                if line[3][0]>=cfg['classification']['flareSize'][0] and \
                   line[3][1:]>=cfg['classification']['flareSize'][1:]:
                    noaa = line[2] # strip off NOAA AR from current line
                    eventTime = line[1] # strip off time from current line
                    flareDate = line[0].split(' ') # split date to year, month, day
                
                    if len(eventTime)!=4:
                        print('Skipping ill-formed event time '+eventTime+\
                              ' from line '+str(line))
                    elif '/' in eventTime:
                        print('Skipping ill-formed event time '+eventTime+\
                              ' from line '+str(line))
                    else:
                        hours = eventTime[0] + eventTime[1] # strip off hours
                        mins = eventTime[2] + eventTime[3] # strip off minutes

                        # define datetime object associated with peak flare time
                        FlareDateTime = datetime(year=int(flareDate[0]),\
                                        month=int(flareDate[1]),\
                                        day=int(flareDate[2]),\
                                        hour=int(hours), minute=int(mins),\
                                        second=0) 
                
                        # time window over which to consider flaring
                        tdelta = timedelta(hours=cfg['classification']['flareTime']) 
    
                        # check for existence of files in NOAA directory
                        if os.path.exists(cfg['newDataDirectory']+noaa):
                            # loop over contents of current NOAA AR directory
                            for fitsF in sorted(os.listdir(cfg['newDataDirectory']+noaa)): 
                                try: 
                                    # strip off date-time string from fits file
                                    fitsTime_str = fitsF.split('.')[2] 
                                    # define datetime object associated with 
                                    # fits file time
                                    fitsTime = datetime(year=int(fitsTime_str[0:4]),\
                                               month = int(fitsTime_str[4:6]),\
                                               day = int(fitsTime_str[6:8]),\
                                               hour=int(fitsTime_str[9:11]),\
                                               minute=int(fitsTime_str[11:13]),\
                                               second=0) 
                                    # check if fits file time is within 24 
                                    # hours previous of peak flare time
                                    if FlareDateTime-fitsTime<tdelta and \
                                       FlareDateTime>fitsTime: 
                                        # check if file has already been 
                                        # assigned label of flare
                                        if fitsF not in flareFiles: 
                                            # append new filename to list  
                                            flareFiles.append(fitsF) 
                                            # append flare size to list
                                            flareSizes.append(line[3].rstrip())
                                        elif fitsF in flareFiles:
                                            # compare previous flare size to
                                            # current flare size and keep 
                                            # larger of the two
                                            previous_size = flareSizes[flareFiles.index(fitsF)]
                                            current_size = line[3].rstrip()
                                            if current_size[0]>previous_size[0] or (current_size[0]>=previous_size[0] and current_size[1:]>previous_size[1:]):
                                                flareSizes[flareFiles.index(fitsF)] = current_size
                                                #print('replacing '+previous_size+' with '+current_size+' due to size difference')
                                except:
                                    pass
                            # print status
                            print('NOAA AR '+noaa+\
                                  ', Total number of flare files: '+\
                                  str(len(flareFiles)))
        # write out flare files for quicker usage later
        with open(cfg['classification']['flareSize']+'_'+\
                  str(cfg['classification']['flareTime'])+'hr_flareFiles.txt',\
                  'w') as f:
            for item in range(len(flareFiles)):
                f.write(flareFiles[item]+','+flareSizes[item]+'\n')

    # write out flare files to specified label file
    with open(cfg["labelFilePath"],'w') as f:
        for item in range(len(flareFiles)):
            f.write(flareFiles[item]+','+flareSizes[item]+'\n')
    
    # write out non-flare files to specified label file 
    f = open(cfg["labelFilePath"],'a')
    num_notflareFiles_total = 0
    num_notflareFiles = 0
    # loop over all AR directories
    noaas = sorted(glob.glob(cfg['newDataDirectory']+'*'))
    for noaa in noaas:
        # loop over all fits files in AR directory
        num_notflareFiles = 0
        fitsFiles = sorted(glob.glob(noaa+'/*.fits'))
        for fitsFile in fitsFiles:
            fit = os.path.basename(fitsFile)
            # check if current fits file already included in flareFiles 
            if not fit in flareFiles:
                num_notflareFiles = num_notflareFiles+1
                num_notflareFiles_total = num_notflareFiles_total+1
                # write out fits file with label of '0'
                f.write(fit+',0\n')
                # print status
        print('AR '+noaa.split('/')[-1]+': '+\
              str(num_notflareFiles)+' non-flare files '+\
              str(num_notflareFiles_total)+' non-flare files total')
    f.close()

# END createDataset FUNCTION
###############################################################################
    

###############################################################################
######################## END FUNCTION DEFINITION ##############################
###############################################################################

########################################################################
######################### SEPARATE LON AND LAT #########################
########################################################################
print('')
print("*** CHECKING FILES FOR LATITUDES INSIDE " + str(cfg["lat"]) + " AND LONGITUDES INSIDE " + str(cfg["lon"]) + " ***")
if os.path.isfile('lat'+str(cfg['lat'])+'_lon'+str(cfg['lon'])+'_files.txt'):
    print('Using existing file list for Latitude: '+str(cfg['lat'])+\
          ' and Longitude: '+str(cfg['lon']))
    print('To generate a new file list, delete existing file lat'+\
          str(cfg['lat'])+'_lon'+str(cfg['lon'])+'_files.txt')
    print('');
    f = open('lat60_lon60_files.txt','r')
    latLonFileArray = f.read().splitlines()
    f.close()
else:
    latLonFileArray = latLonSeparation(cfg )

########################################################################
########################## SEPARATE NAN FILES ##########################
########################################################################
print('')
print("*** CHECKING FILES FOR MORE THAN " + str(cfg["nans"]) + " NANS ***")
if os.path.exists('nans'+str(cfg['nans'])+'_files.txt'):
    print('Using existing file list for NaNs allowed: '+str(cfg['nans']))
    print('To generate a new file list, delete existing file nans'+\
          str(cfg['nans'])+'_files.txt')
    print('')
    f = open('nans0_files.txt','r')
    nanFileArray = f.read().splitlines()
    f.close()
else:
    nanFileArray = nanSeparation(latLonFileArray,cfg)

########################################################################
########################### COPY GOOD FILES ############################
########################################################################
#print("*** COPY/MOVING DATA TO " + cfg["newDataDirectory"] + " ***")
#createDataset( nanFileArray, latLonFileArray, cfg )

########################################################################
###################### GENERATE CLASSIFICATION CSV #####################
########################################################################
print("*** GENERATING LABEL CSV FILE ***")
if os.path.exists('eventList.txt'):
    print('Using existing event list for creation of flare labels')
    print('To generate a new event list, delete existing file eventList.txt')
    print('')
else:
    createEventList(cfg)
if os.path.exists(cfg['labelFilePath']):
    print('Label file already exists')
    print('To generate a new label file, delete existing file '+\
           cfg['labelFilePath'])
    print('')
else:
    with open('files_lat'+str(cfg['lat'])+'_lon'+str(cfg['lon'])+'_nans'+str(cfg['nans'])+'.txt','r') as f:
        files = f.read().splitlines()
    createLabelCsv( files, cfg )

print("\n\n\n*** DONE ***\n\n\n")
#
# END SCRIPT
################################################################################
