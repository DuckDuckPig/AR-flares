#-------------------------------------------------------------------------------
# Build_dataframes.py
#
# Code to generate files that can be read in as dataframes for the tensorflow
# dataloaders.
#
#  - Edit the lines under ## User Definitions to specify paths and other 
#    parameters.
#  - Outputs dataframe files in csv format with filename and classification 
#    label in the format expected for a tensorflow dataloader.
#     - The dataframe files for the preconfigured reduced resolution dataset 
#       Test_Data_by_AR_png_224.csv, Train_Data_by_AR_png_224.csv, and 
#       Validation_Data_by_AR_png_224.csv are available on Dryad at <insert 
#       link here> and for the full resolution dataset Test_Data_by_AR.csv, 
#       Train_Data_by_AR.csv, and Validation_Data_by_AR.csv are available on 
#       Dryad at <insert link here>. It is recommended that you save the 
#       dataframe files in the classifier_VGG/ directory (i.e., the same 
#       directory as the VGG code), although subsequent code will allow you to 
#       specify the path to those files.
#  - Requires the the flare labels file from the AR Dataset and the data splits 
#    (lists of test and val active regions) available on Dryad.
#       - The flare labels file (C1.0_24hr_224_png_Labels.txt or 
#         C1.0_24hr_Labels.txt) are available on Dryad at <insert link here> 
#         (reduced resolution png files) or <insert link here> (full resolution 
#         fits files). It is recommended that you save the flare labels file in 
#         the base AR-flares/ directory, although subsequent code will allow you 
#         to specify the path to those files.
#       - The data splits (lists of test and val active regions) 
#         List_of_AR_in_Test_Data_by_AR.csv, List_of_AR_in_Train_data_by_AR.csv, 
#         and List_of_AR_in_Validation_data_by_AR.csv are available on Dryad 
#         (<insert link here> (reduced resolution) or <insert link here> (full 
#         resolution)). It is recommended that you save the data splits files in 
#         the base AR-flares/ directory, although subsequent code will allow you 
#         to specify the path to those files.
#
# References:
# [1] L. E. Boucheron, T. Vincent, J. A. Grajeda, and E. Wuest, "Solar Active 
#     Region Magnetogram Image Dataset for Studies of Space Weather," arXiv 
#     preprint arXiv:2305.09492, 2023.
#
# Copyright 2022 Laura Boucheron
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

import csv
import numpy as np

## User Definitions
# Modify the following to reflect the location of the label file (available with the dataset on Dryad)
labelFile = '/mnt/solar_flares/AR_Dataset/C1.0_24hr_Labels.txt' # label file
# Modify the following to reflect the location of the list of ARs in test and validation (available with the dataset on Dryad)
testARList = '../List_of_AR_in_Test_Data_by_AR.csv' #list of active regions in TestData
valARList  = '../List_of_AR_in_Validation_data_by_AR.csv' #list of active regions in ValData
# Modify the following to reflect the desired location of the dataframe files output by this code
testdata_file = 'Test_Data_by_AR.csv'
valdata_file = 'Validation_Data_by_AR.csv'
traindata_file = 'Train_Data_by_AR.csv'
## End User Definitions

with open(testARList) as f:
    testARs = np.asarray(list(csv.reader(f,delimiter = ',')))

with open(valARList) as f:
    valARs = np.asarray(list(csv.reader(f,delimiter = ',')))

with open(labelFile) as f:
    Labels = list(csv.reader(f,delimiter = ','))


testdata = ['filename,class']
traindata = ['filename,class']
valdata = ['filename,class']
for label in Labels:
    AR = label[0][:4]
    if AR in testARs:
        if label[1]=='0':
            testdata.append(AR+'/'+label[0]+','+'0')
        else:
            testdata.append(AR+'/'+label[0]+','+'1')
    elif AR in valARs:
        if label[1]=='0':
            valdata.append(AR+'/'+label[0]+','+'0')
        else:
            valdata.append(AR+'/'+label[0]+','+'1')
    else:
        if label[1]=='0':
            traindata.append(AR+'/'+label[0]+','+'0')
        else:
            traindata.append(AR+'/'+label[0]+','+'1')

np.savetxt(testdata_file,testdata,delimiter=',',fmt='%s')
np.savetxt(valdata_file,valdata,delimiter=',',fmt='%s')
np.savetxt(traindata_file,traindata,delimiter=',',fmt='%s')
