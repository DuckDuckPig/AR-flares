"""
This program loops over the Event Reports (ER) to determine flare event
information.  The ER are assumed to be downloaded to the Events/ subirectory
underneath the specified base_directory variable set at the beginning of this
code.  The ER are downloaded as one .txt file per day.  We parse the data for
XRA events (corresponding to x-ray events detected by the GOES spacecraft) with
an associated REG# (corresponding to a NOAA AR number).  For those x-ray events
associated with a NOAA AR, we additionally parsed the ER for the peak flare time
Max and flare size Particulars.  We store these data in a comma separated text
file eventList.txt where each line is of the format YYYY MM DD,HHMM,NNNN,CX.X,
where YYYY MM DD is the date, HHMM is the time, NNNN is the four-digit NOAA AR
number, and CX.X is the GOES class (e.g., C1.0 or X10.1).  
"""
import os
import glob

base_directory = '/mnt/solar_flares/AR_Dataset'

Events_dirs = sorted(glob.glob(base_directory+'/Events/*')) #list of Events directories

fwrite = open(base_directory+'eventList.txt','w+')

# Loop through the list of folders containing text files
for Events_dir in Events_dirs:
    Events_files = sorted(glob.glob(Events_dir+'/*'))

    # Loop through each text file in the folders
    for Events_file in Events_files:
        date = ''
        peakTime = ''
        noaaNum = ''
        flare = ''

        with open(Events_file,'r') as f:
            for line in f:

                if ':Date:' in line:
                    if ('2010 01' in line) or ('2010 02' in line) or ('2010 03' in line) or ('2010 04' in line): #start at 05/01/2010 here
                        pass
                    else:
                        date = (line.split(':Date: ')[1]).rstrip() # strip off date
                if 'XRA' in line: # x-ray event
                    a = line.split(' ')
                    peakTime = line[18:22]
                    noaaNum = line[-5:]
                    flare = line[58:62]

                    if noaaNum == '' or date == '' or flare == '':
                        pass
                    else:
                        pass
                        fwrite.write(date + "," + peakTime + "," + noaaNum + "," + flare +",\n")


fwrite.close()
