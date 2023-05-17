#-------------------------------------------------------------------------------
# Build_Featureset.py
#
# Main code to extract 29 magnetic complexity features from HMI magnetograms. 
# This code is implemented using the python multiprocessing package, but can be 
# modified for serial implementation.
#             GRADIENT FEATURES
#               Gradient mean
#               Gradient std
#               Gradient median
#               Gradient min
#               Gradient max
#               Gradient skewness	
#               Gradient kurtosis	
#             NEUTRAL LINE FEATURES
#               NL length	
#               NL no. fragments
#               NL gradient-weighted len
#               NL curvature mean
#               NL curvature std
#               NL curvature median
#               NL curvature min
#               NL curvature max
#               NL bending energy mean
#               NL bending energy std
#               NL bending energy median
#               NL bending energy min
#               NL bending energy max
#             WAVELET FEATURES
#               Wavelet Energy L1
#               Wavelet Energy L2
#               Wavelet Energy L3
#               Wavelet Energy L4
#               Wavelet Energy L5
#             FLUX FEATURES
#               Total positive flux
#               Total negative flux
#               Total signed flux
#               Total unsigned flux
#             
#
#  - Edit the lines under ## User Definitions to specify paths and other 
#    parameters.
#  - Outputs a feature file in csv format with the complexity features, labels 
#    (regression and classification), and filename.
#     - The feature file for the preconfigured reduced resolution dataset 
#       Lat60_Lon60_Nans0_C1.0_24hr_png_224_features.csv is available on Dryad 
#       at <insert link here> and for the full resolution dataset 
#       Lat60_Lon60_Nans0_C1.0_24hr_features.csv is available on Dryad at 
#       <insert link here>. It is recommended that you save the feature file in 
#       the classifier_SVM/ directory (i.e., the same directory as the SVM 
#       code), although subsequent code will allow you to specify the path to 
#       those files.
#  - Relies on FeaturesetTools.py.
#  - Requires the AR Dataset:
#     - The flare labesl file (C1.0_24hr_224_png_Labels.txt or 
#       C1.0_24hr_Labels.txt, available on Dryad at <insert link here> (reduced 
#       resolution png files) or <insert link here> (full resolution fits 
#       files). It is recommended that you save the flare labels file in the 
#       base AR-flares/ directory, although subsequent code will allow you to 
#       specify the path to those files.
#     - The corresponding SDO HMI AR Images available on Dryad at <insert link 
#       here> (reduced resolution png files) or <insert link here> (full 
#       resolution fits files). The location of the SDO HMI AR Images will be 
#       specified by the user in subsequent code. You may save those data in 
#       the base AR-flares/ directory or any other location.
# 
# Modified Nov 6 2020 by lboucher to use multiprocessing
# Modified Sep 23 2022 by lboucher to output both regression labels and 
#                                  classification labels
#
# References:
# [1] A. Al-Ghraibah, L. E. Boucheron, and R. T. J. McAteer, "An automated
#     approach to ranking photospheric proxies of magnetic energy buildup,"
#     Astronomy & Astrophysics, vol. 579, p. A64, 2015.
# [2] L. E. Boucheron, T. Vincent, J. A. Grajeda, and E. Wuest, "Solar Active 
#     Region Magnetogram Image Dataset for Studies of Space Weather," arXiv 
#     preprint arXiv:2305.09492, 2023.
#
# Copyright 2022 Laura Boucheron, Jeremy Grajeda, Ellery Wuest
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
