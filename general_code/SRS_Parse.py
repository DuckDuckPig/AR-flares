# This program loops through the Solar Region Summaries (SRS) to determine dates 
# an active region (AR) is visible on disk.  The SRS are assumed to be downloaded 
# to the SRS/ subdirectory underneath the specified SRS_directory variable set 
# at the beginning of this code.  The SRS are downloaded as one .txt file per 
# day.  We used Part I data in the SRS which detail those ARs with associated 
# sunspot structure.  For each NOAA AR appearing in SRS Part I, we store the NOAA 
# AR number, the date the AR first appears in the SRS, and accumulate the total 
# number of days the same AR appears in the SRS.  We store these data in a comma 
# separated text file ARList.txt where each line is of the format NNN,YYYMMDD,X, 
# where NNNN is the four digit NOAA AR number, YYYYMMDD is the initial date of 
# appearance, and X is an integer number of days.  
#
#
# References:
# [1] L. E. Boucheron, T. Vincent, J. A. Grajeda, and E. Wuest, "Solar Active 
#     Region Magnetogram Image Dataset for Studies of Space Weather," arXiv 
#     preprint arXiv:2305.09492, 2023.
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
import glob

## User Definitions
SRS_directory = '/mnt/solar_flares/AR_Dataset/' # directory underneath which the SRS/ directory resides
file_directory = './' # directory into which to write ARList.txt
## End User Definitions

SRS_dirs = sorted(glob.glob(SRS_directory+'/SRS/*')) #list of SRS directories
srsArr = [] # to keep track of ARs

# Loop through the list of folders containing text files
for SRS_dir in SRS_dirs: 
    SRS_files = sorted(glob.glob(SRS_dir+'/*'))
    
    # Loop through each text file in the folders
    for SRS_file in SRS_files:
        date = os.path.basename(SRS_file).split('S')[0] # strip off date string
        
        if (int(date) < 20100501): # only consider ARs on/after 05/01/2010 here
            pass
        else:
            with open(SRS_file,'r') as f:
                lines = f.readlines()
                for index, line in enumerate(lines):
                    if "IA" in line: # have reached section after I.
                        break
                    elif 'Nmbr' in line: # first line of section I.
                        i = 1 # line counter
                        while 'IA' not in lines[index + i] and 'None' not in lines[index + i]: # end of section indicators

                            a = lines[index + i].split(' ')
                        
                            NoaaNum = a[0] # pull off NOAA number
                            flag = False # if NOAA number seen before
                        
                            for item in srsArr: # check if NOAA seen yet
                                if item[0] == NoaaNum:
                                    flag = True
                                    ind = srsArr.index(item)
                                
                            if flag == True: # update for seen NOAA
                                srsArr[ind][2] = srsArr[ind][2] + 1
                            
                            else: # start for new NOAA
                                srsArr.append([NoaaNum,date,1])
                            
                            i = i + 1 # increment line counter

                        
fwrite = open(file_directory+'/ARList.txt','w+')

for line in srsArr:
    fwrite.write(str(line[0]) + ',' + str(line[1]) + ',' + str(line[2]) + '\n')
   
fwrite.close()
