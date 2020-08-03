"""
This program loops through the Solar Region Summaries (SRS) to determine
dates an active region (AR) is visible on disk.  The SRS are assumed to be
downloaded to the specified base_directory variable set at the beginning of
this code.  The SRS are downloaded as one .txt file per day.  We used Part I
data in the SRS which detail those ARs with associated sunspot structure.
For each NOAA AR appearing in SRS Part I, we store the NOAA AR number, the
date the AR first appears in the SRS, and accumulate the total number of days
the same AR appears in the SRS.  We store these data in a comma separated
text file ARList.txt where each line is of the format NNN,YYYMMDD,X, where
NNNN is the four digit NOAA AR number, YYYYMMDD is the initial date of 
appearance, and X is an integer number of days.  
"""
import os
import glob

base_directory = '/mnt/solar_flares/AR_Dataset'

SRS_dirs = sorted(glob.glob(base_directory+'/SRS/*')) #list of SRS directories

srsArr = [] # to keep track of ARs

# Loop through the list of folders containing text files
for SRS_dir in SRS_dirs: 
    SRS_files = sorted(glob.glob(SRS_dir+'/*'))
    
    # Loop through each text file in the folders
    for SRS_file in SRS_files:
        date = os.path.basename(SRS_file).split('S')[0] # strip off date string
        #noaaNum = ''
        
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

                        
fwrite = open(base_directory+'/ARList.txt','w+')

for line in srsArr:
    fwrite.write(str(line[0]) + ',' + str(line[1]) + ',' + str(line[2]) + '\n')
   
fwrite.close()
