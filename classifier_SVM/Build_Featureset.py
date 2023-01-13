#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DESCRIPTION: This Script builds the following featureset for each Magnetogram 
             in the specified folder:
             
             GRADIENT FEATURES
               Gradient mean
               Gradient std
               Gradient median
               Gradient min
               Gradient max
               Gradient skewness	
               Gradient kurtosis	
             NEUTRAL LINE FEATURES
               NL length	
               NL no. fragments
               NL gradient-weighted len
               NL curvature mean
               NL curvature std
               NL curvature median
               NL curvature min
               NL curvature max
               NL bending energy mean
               NL bending energy std
               NL bending energy median
               NL bending energy min
               NL bending energy max
             WAVELET FEATURES
               Wavelet Energy L1
               Wavelet Energy L2
               Wavelet Energy L3
               Wavelet Energy L4
               Wavelet Energy L5
             FLUX FEATURES
               Total positive flux
               Total negative flux
               Total signed flux
               Total unsigned flux
             
             These features are listed in a .csv file, followed by whether or
             or not the AR that this Magnetogram corresponds to flared in the
             specified timeframe found in the labels file and the name of the 
             image.
               
Created on Thu Jun  6 08:34:54 2019

@author: jgra


Modified Nov 6 2020 by lboucher to use multiprocessing
Modified Sep 23 2022 by lboucher to output both regression labels and classification labels
"""

import os
import glob
import csv
import numpy as np
from astropy.io import fits
import FeaturesetTools 
import imageio
from multiprocessing import Pool, Manager
from functools import partial

## User Definitions
# Modify the following to reflect the location of the label file (available with the dataset on Dryad)
labelFile = '/mnt/solar_flares/AR_Dataset/C1.0_24hr_Labels.txt' # label file
# Modify the following to reflect the base directory of the dataset
datasetDir = '/mnt/solar_flares/AR_Dataset/Lat60_Lon60_Nans0/' # dataset directory location
# Specify the desired output location an filename
outFile = 'Lat60_Lon60_Nans0_C1.0_24hr_features.csv' # output file
# Specify whether the dataset is fits or png
file_extension = 'fits' # fits or png
## End User Definitions

def extract_features(Labels,filename):
    # open image
    if file_extension=='fits':
        with fits.open(filename) as Img:
            Img.verify('silentfix')
            Img = Img[1].data
    elif file_extension=='png':
        Img = imageio.imread(filename).astype(float)
        Img = Img-128 # offset so that zero flux is at zero

            
    # Inform User
    print('Building entry for '+os.path.basename(filename))
                   
    # Extract Features
    features = FeaturesetTools.concatVals(Img)

    if os.path.basename(filename) in Labels:
        if Labels[os.path.basename(filename)]=='0':
            label = '0,'+Labels[os.path.basename(filename)]
        else:
            label = '1,'+Labels[os.path.basename(filename)]
    else:
        label = 'NaN'

    return features,label

if __name__=='__main__':
    p = Pool(40)
    
    # Load labelFile
    #inform User
    print('Loading', os.path.basename(labelFile))
    # The format of each entry in the labelFile must be:
    # Filename, Flare Type, *any other data you want*\n
    # Load Label File
    with open(labelFile) as f:
        csvData = csv.reader(f,delimiter = ',')
        Labels = dict(csvData)
    Labels = Manager().dict(Labels)

    # Find all data files
    print('Finding image files (this may take a while)')
    filenames = sorted(glob.glob(datasetDir+'/*/*.'+file_extension))
    fnums = range(len(filenames))

    # Fill filenames_base
    filenames_base = list()
    for filename in filenames:
        filenames_base.append(os.path.basename(filename))

    # extract features
    print('Extracting features')
    feature_matrix,label_vector = zip(*p.map(partial(extract_features,Labels),filenames))

    # Create Outfile 
    # Inform User
    print ('Creating',outFile)
    #outFile = outFile+'_sr'+str(sr)+'x'+str(sr)+'.csv' 
    np.savetxt(outFile,np.hstack((np.asarray(feature_matrix),\
               np.expand_dims(np.asarray(label_vector),1),\
               np.expand_dims(np.asarray(filenames_base),1))),\
               delimiter=',',fmt='%s')
#Inform User
print('Process Complete')
