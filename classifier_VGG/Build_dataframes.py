"""
DESCRIPTION: This script builds the keras dataframe files for the train, validation, and test sets from the
             base label file.

Created on Thu Jan 12 10:19:43 2023

@author: lboucher
"""

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
