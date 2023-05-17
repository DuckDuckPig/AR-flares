#-------------------------------------------------------------------------------
# AR_Classifier.py
#
# Main code for the SVM classifier.
#
#    - Edit the lines under ## User Definitions to specify paths and other 
#      parameters.
#    - Outputs three csv feature files with train, test, and validation data 
#      (i.e., the magnetic complexity features, filename, and label); a txt file 
#      weight file used for equalization of features, a txt file performance" 
#      wih classifier statistics, and a pickle file model with the trained model.
#     - Relies on FeaturesetTools.py.
#     - Requires the feature file output by Build_Featureset.py and the data
#       splits (lists of test and val active regions) available on Dryad 
#       (details below)
#       - The feature file for the preconfigured reduced resolution dataset 
#         Lat60_Lon60_Nans0_C1.0_24hr_png_224_features.csv is available on Dryad 
#         at <insert link here> and for the full resolution dataset 
#         Lat60_Lon60_Nans0_C1.0_24hr_features.csv is available on Dryad at 
#         <insert link here>. It is recommended that you save the feature file
#         in the same classifier_SVM/ directory (i.e., the same directory as the 
#         SVM code), although subsequent code will allow you to specify the path 
#         to those files.
#       - The data splits (lists of test and val active regions) 
#         List_of_AR_in_Test_Data_by_AR.csv, List_of_AR_in_Train_data_by_AR.csv, 
#         and List_of_AR_in_Validation_data_by_AR.csv are available on Dryad 
#         (<insert link here> (reduced resolution) or <insert link here> (full 
#         resolution). It is recommended that you save the data splits files in 
#         the base AR-flares/ directory, although subsequent code will allow you 
#         to specify the path to those files.
#       - Note--if the data splits are not available to the code, the code will 
#         randomly select 10% of active regions for the test and val sets; this 
#         will not result in the same split as the files available on Dryad.
#
# References:
# [1] L. E. Boucheron, T. Vincent, J. A. Grajeda, and E. Wuest, "Solar Active 
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

# Import Libraries and Tools
import os
import csv
import FeaturesetTools
import numpy as np
import sklearn.svm
import pickle

# Key Varibles

## User Definitions
# Modify the following to define locations of input and output files
Folder = './' # folder in which to save results with trailing /
class_type = 'linear' # 'linear' or 'rbf' kernel for SVM classifier
suffix = '' # optional suffix for saving different models, leave as '' for no suffix
classFile  = 'Lat60_Lon60_Nans0_C1.0_24hr'+suffix+'_features.csv' # file containing extracted features
trainDataName  = Folder+'Train_Data_by_AR'+suffix+'.csv' # file with train data, will be read in if exists or created if doesn't
testDataName   = Folder+'Test_Data_by_AR'+suffix+'.csv' # file with test data, will be read in if exists or created if doesn't
valDataName    = Folder+'Validation_data_by_AR'+suffix+'.csv' # file with val data, will be read in if exists or created if doesn't
weightData = Folder+'Weight_Lat60_Lon60_Nans0_C1.0_24hr'+suffix+'.txt' #weights used for equalization of features, will be created from analysis of train data if doesn't exist
outfile = Folder+'ARClassifierStats_weighted_trainvaltest_'+class_type+suffix+'.txt' # output file for statistics; will also be used to define the .pickle filename
testARList = '../List_of_AR_in_Test_Data_by_AR.csv' #list of active regions in TestData, will be created by randomly assigning 10% of ARs if does not exist in the location specified
valARList  = '../List_of_AR_in_Validation_data_by_AR.csv' #list of active regions in ValData, will be created by randomly asigning 10% of ARs if does not exist in the location specified
## End User Definitions

# Generate filenames
classFile  = Folder + '/' + classFile
trainDataName  = Folder + '/' + trainDataName
testDataName   = Folder + '/' + testDataName
valDataName    = Folder + '/' + valDataName
testARList = Folder + '/' + testARList
valARList  = Folder + '/' + valARList
weightData = Folder + '/' + weightData

# Generate Files

# Check for files
if not os.path.exists(trainDataName) or not os.path.exists(testDataName) or not os.path.exists(valDataName):
    # Inform User
    print('\n'+os.path.basename(trainDataName),'or',os.path.basename(testDataName),'or',os.path.basename(valDataName), 'not found.')
    print('Resolving Issue')
    
    # Inform User
    print('Creating', os.path.basename(trainDataName),'and',
              os.path.basename(testDataName),'and',
              os.path.basename(valDataName))
    # Create trainData and testData
    FeaturesetTools.createARBasedSets(classFile,trainDataName,testDataName,valDataName,weightData,testARList,valARList)
    
# Load trainData and testData

# Inform User
print('\nLoading', os.path.basename(trainDataName),'and', 
      os.path.basename(testDataName),'and',
      os.path.basename(valDataName))

# Read and prepare trainData
trainData = np.genfromtxt(trainDataName,delimiter=',',dtype=float,usecols=range(29))
trainLabel = np.genfromtxt(trainDataName,delimiter=',',dtype=int,usecols=29)
trainNames = np.genfromtxt(trainDataName,delimiter=',',dtype=str,usecols=30)

# Read and prpare testData
testData = np.genfromtxt(testDataName,delimiter=',',dtype=float,usecols=range(29))
testLabel = np.genfromtxt(testDataName,delimiter=',',dtype=int,usecols=29)
testNames = np.genfromtxt(testDataName,delimiter=',',dtype=str,usecols=30)

# Read and prpare valData
valData = np.genfromtxt(valDataName,delimiter=',',dtype=float,usecols=range(29))
valLabel = np.genfromtxt(valDataName,delimiter=',',dtype=int,usecols=29)
valNames = np.genfromtxt(valDataName,delimiter=',',dtype=str,usecols=30)

print('Training')
#create and train svm, then use on test data
classifier = sklearn.svm.SVC(kernel = 'linear',gamma='auto',class_weight='balanced')
classifier.fit(trainData,trainLabel)

print('Saving trained model')
modelfile = outfile[:-4]+'_model.pickle'
pickle.dump(classifier,open(modelfile,'wb'))

print('Applying learned classifier to test data')
P = classifier.predict(testData)
C = sklearn.metrics.confusion_matrix(testLabel,P,labels=[1,0])
   
#evaluate various performance metrics
tp = C[0,0]; fn=C[0,1]; fp=C[1,0]; tn=C[1,1];
tpr = float(tp)/(tp+fn)
tnr = float(tn)/(tn+fp)
    
hss = float(2*((tp*tn)-(fn*fp)))/((tp+fn)*(fn+tn) + (tp+fp)*(fp+tn))
tss = tpr - (1. - tnr)
    
# Save Results

# Inform User
print('Saving Results')
# Print Results
with open(outfile, 'w+') as f:
    f.write('Test data performance')
    f.write('\nTPR = ')
    f.write(str(tpr))
    f.write('\nTNR = ')
    f.write(str(tnr))
    f.write('\nHSS = ')
    f.write(str(hss))
    f.write('\nTSS = ')
    f.write(str(tss))

print('Applying learned classifier to validation data')
P = classifier.predict(valData)
C = sklearn.metrics.confusion_matrix(valLabel,P,labels=[1,0])
#evaluate various performance metrics
tp = C[0,0]; fn=C[0,1]; fp=C[1,0]; tn=C[1,1];
tpr = float(tp)/(tp+fn)
tnr = float(tn)/(tn+fp)
    
hss = float(2*((tp*tn)-(fn*fp)))/((tp+fn)*(fn+tn) + (tp+fp)*(fp+tn))
tss = tpr - (1. - tnr)
    
print('Saving Results')
# Print Results
with open(outfile, 'a+') as f:
    f.write('\nValidation data performance')
    f.write('\nTPR = ')
    f.write(str(tpr))
    f.write('\nTNR = ')
    f.write(str(tnr))
    f.write('\nHSS = ')
    f.write(str(hss))
    f.write('\nTSS = ')
    f.write(str(tss))

print('Applying learned classifier to training data')
P = classifier.predict(trainData)
C = sklearn.metrics.confusion_matrix(trainLabel,P,labels=[1,0])
#evaluate various performance metrics
tp = C[0,0]; fn=C[0,1]; fp=C[1,0]; tn=C[1,1];
tpr = float(tp)/(tp+fn)
tnr = float(tn)/(tn+fp)
    
hss = float(2*((tp*tn)-(fn*fp)))/((tp+fn)*(fn+tn) + (tp+fp)*(fp+tn))
tss = tpr - (1. - tnr)
    
print('Saving Results')
# Print Results
with open(outfile, 'a+') as f:
    f.write('\nTraining data performance')
    f.write('\nTPR = ')
    f.write(str(tpr))
    f.write('\nTNR = ')
    f.write(str(tnr))
    f.write('\nHSS = ')
    f.write(str(hss))
    f.write('\nTSS = ')
    f.write(str(tss))
    
# Inform user
print('Process Complete')
