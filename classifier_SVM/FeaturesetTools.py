#-------------------------------------------------------------------------------
# FeaturesetTools.py
#
# Helper functions for feature extraction. 
#
#  - Relies on FunctionsP3.py
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


# Import Libraries and tools
import numpy as np
import FunctionsP3
import copy
import csv
import os

def concatVals(image):
    """
    For each image returns, in order:
        GRADIENT FEATURES:
            Gradient mean, Gradient std, Gradient median, Gradient min, 
            Gradient skewness, Gradient kurtosis
        NEUTRAL LINE FEATURES:
            NL length, NL number of fragments, NL gradient-weighted length, NL
            curvature mean, NL curvature std, NL curvature median, NL
            curvature min, NL curvature max, NL bending energy mean, NL bending
            energy std, NL bending energy median, NL bending energy min, NL
            bending energy max
        WAVELET FEATURES:
            Wavelet Energy L1, Wavelet Energy L2, Wavelet Energy L3, Wavelet
            Energy L4, Wavelet Energy L5
        FLUX FEATURES:
            Total postive flux, Total negative flux, Total signed flux, Total
            unsigned flux
    """
    
    # Generate fetures
    G   = FunctionsP3.Gradfeat(image)
    NL  = FunctionsP3.NLfeat(image)
    wav = FunctionsP3.wavel(image)
    F   = FunctionsP3.fluxValues(image)
    
    # Concatenate and return results
    return np.concatenate((G,NL,wav,F))

def equalizeTrainData(trainData,limit=None):
    """
    Function equalizes the data provided and outputs the result and the max 
    and min for each category equalized.
    """
    
    # Make sure the original data is left untouched
    Data = copy.deepcopy(trainData)
    
    # Set limit
    if limit is None:
        limit = len(Data[0])
    
    # Find Data Limits
    dataLength = len(Data)
    
    # Create object to hold the equalization factors/weights
    eqFactors = np.zeros([limit,2])
    
    # For each Feature...
    for i in range(limit):
        
        # If it is a feature, and not a label
        if isinstance(Data[0][i],float):
            featureValues = np.zeros(dataLength)
            
            # Figure out the min
            for j in range(dataLength):
                featureValues[j] = Data[j][i] * 1.0
            eqFactors[i,0] = np.amin(featureValues)
             
            # Offset based on that min and find the new max
            for j in range(dataLength):
                Data[j][i] = Data[j][i] - eqFactors[i,0]
                featureValues[j] = Data[j][i] * 1.0
            eqFactors[i,1] = np.amax(featureValues)
            
            # Equalize
            if eqFactors[i,1] != 0:
                for j in range(dataLength):
                    Data[j][i] = Data[j][i] / eqFactors[i,1]
                    
        # Otherwise, make sure that the eqFactor doesn't affect other processes
        else:
            eqFactors[i,1] = 1
    
    # Return the equalized data and the equalization factors/weights
    return Data, eqFactors

def equalizeNewData(newData,eqFactors):
    """
    Function equalizes the data provided using a 2D np.array of weights that 
    serve as the minimum value and adjusted maximum value.
    """
    
    # Make sure the original data is left untouched
    Data = copy.deepcopy(newData)
    
    #ensure data is an array
    try:
        len(Data)
    except:
        Data = [Data]
    
    # Equalize
    for i in range(len(eqFactors)):
        for j in range(len(Data)):
            if isinstance(Data[j][i],float):
                Data[j][i] = float(Data[j][i]) - eqFactors[i,0] # Shift by min
                if eqFactors[i,1] != 0:
                    Data[j][i] = float(Data[j][i]) / float(eqFactors[i,1]) # Scale based on max
    
    # Return the equalized data
    return Data

def listAllAR(masterFile):
    """
    Function generates and returns a list of all of the active regions in a 
    featureset
    """
    
    # Read masterFile
    with open(masterFile)as f:
        csvData = csv.reader(f,delimiter = ',')
        features = []
        for datum in csvData:
            features.append(datum)
        
    # Generate list of active regions
    ARList = []
    i = True
    for feature in features:
        # Find name of Active Region
        name = feature[-1].split('_h')[0]
        name = int(float(name)) # for some reason you can't go from string to int
        
        # Check to see if name already exists
        if i:
            ARList.append(int(name))
            i = False
        elif int(ARList[-1]) != name:
            ARList.append(int(name))
    
    # Return Results
    return ARList

def listEntries(masterFile,ARList):
    """
    Given a list of active regions and the filenmae of a featureset, this
    function generates a list of the indexes that corrispond to those regions
    """
    
    # Read masterFile
    with open(masterFile) as f:
        csvData = csv.reader(f,delimiter = ',')
        features = []
        for datum in csvData:
            features.append(datum)
    
    # Generate list of indexes
    IndexList = []
    for i in range(len(features)):
        # Find name of active region
        name = features[i][-1].split('_h')[0]
        name = int(float(name)) #int(str) doesn't work
        
        # check to see if name is included in ARList
        for entry in ARList:
            if name == entry:
                IndexList.append(i)
                
    # Return Results
    return IndexList

def createARBasedSets(masterFile,trainData,testData,valadationData,weightData,
                      testARList,valadationARList,limit=None,
                      weightDataExists=True,testArListExists=True,
                      valadationARListExists=True,testSize=10,
                      valadationSize=10):
    """
    Generate Training, Test and Valadation sets devided by Active Region.
    
    Function take a master document that consists of all features for the full
    dataset and parces out 10% of the active regions (unlesss otherwise
    specified) in it to form a test set, and 10% of the acive regions 
    (unless otherwise specified) in it to form a valadation set.
    The remaining data, which is now free of those regions, becomes a training 
    set for the training of an SVM classifier or regressor. The data is also 
    scaled to the range of 0 to 1. The list of active regions used to create 
    the test set and the valadation set, and the weights used for scaling the 
    full feature set are also saved.
    
    Parameters
    ----------
    masterFile : str
        Path and name of file that contains the full dataset
    trainData : str
        Path and name that will be giving to the Training Set
    testData : str
        Path and name that will be given to the Test Set
    valadationData : str
        Path and name that will be given to the Valadation Set
    weightData : str
        Path and name of file that does or will contain the weights used for 
        equalizng the data in the masterFile
    testARList : str
        Path and name of file that does or will contain the list of Active
        Regions that make up the test set
    valadationARList : str
        Path and name of file that does or will contain tthe list of Active
        Regions that make up the valadation set
    limit : int
        Number of entries in each feature that will be equalized. This here to 
        ensure that the label and entry names at the end of the file are not
        equlized by accident. 
        
        Default Value = None
    weightDataExists : bool
        Set to False if the file pointed to by weightData already exists and 
        you wish to overwrite it with new values, instead of using it to 
        equalize this data. 
        
        Defalut Value = True (if weightData exists, use file for equzliation)
    testArListExists : bool
        Set to False if the file pointed to by testRows already exists and 
        you wish to overwrite it with new values instead of using it to build
        or rebulid your Test Set from the masterFile. 
        
        Default Value = True (if testRows exist, use file to recreate the Test
        Set from masterFile)testRows
    valadationARListExists : bool
        Set to false if the file pointed to by test valadationRows exists and 
        you wish to overwrite it with new values instead of using it to build
        or rebuild your Valadation set from the masterFile.
        
        Default Value = True (if valadationRows rexist, use file to recreate
        the Valadation Set from masterFile)
        
        Note:
            To ensure that the valadation set and test set do not share any
            entries, this varible is overwritten to False if testRows does not 
            esist or testRowsExist is set to False
    testSize : float
        Percentage of Active Regions that will be used to create the Test Set
        
        Default Value = 10%
    valadationSize : Float
        Percentage of Active Regions taht will be used to create the Valadation
        Set
        
        Default Value = 10%
    """
    
    # Generate list of active regions in Test Set
    if testArListExists and os.path.exists(testARList):
        testARListData = np.genfromtxt(testARList, dtype = int)
    else:
        print('Creating a new test data split!!!')
        if testSize >= 1:
            testSize = testSize / 100.
        ARListData = listAllAR(masterFile)
        testSize = np.ceil(testSize * len(ARListData))
        testRows = np.random.choice(len(ARListData),int(testSize),replace = False)
        testARListData = np.array(ARListData)[testRows]
        # Save list for next time
        np.savetxt(testARList, testARListData, delimiter = ',', fmt = '%i')
        # Ensure valadation data will not overlap
        valadationARListExists = False
    
    # Generate list of active regions in Valadation Set
    if valadationARListExists and os.path.exists(valadationARList):
        valadationARListData = np.genfromtxt(valadationARList, dtype = int)
    else:
        print('Creating a new validation data split!!!')
        if valadationSize >= 1:
            valadationSize = valadationSize / 100.
        ARListData = listAllAR(masterFile)
        valadationSize = np.ceil(valadationSize * len(ARListData))
        # Make sure that nothing in the testSet ends up in the ValadationSet
        Prob = 1./(len(ARListData) - len(testARListData))
        Prob = np.ones(len(ARListData)) * Prob
        for i in range(len(ARListData)):
            for j in range(len(testARListData)):
                if ARListData[i] == testARListData[j]:
                    Prob[i] = 0
        # Generate Data
        valadationRows = np.random.choice(len(ARListData), int(valadationSize),
                                          replace = False, p = Prob)
        valadationARListData = np.array(ARListData)[valadationRows]
        # Save list for next time
        np.savetxt(valadationARList,valadationARListData,delimiter = ',', fmt = '%i')        
        
    # Use AR Lists to create test and Valadation Rows
    testRows = listEntries(masterFile,testARListData)
    valRows  = listEntries(masterFile,valadationARListData)
    allRows  = np.concatenate([testRows,valRows])
    
    # Get features
    fullFeatureset = np.genfromtxt(masterFile,delimiter = ',', dtype = None,encoding=None)
    
    # Equlize Features
    if weightDataExists and os.path.exists(weightData):
        weights = np.genfromtxt(weightData,delimiter = ',', dtype = None)
        fullFeatureset = equalizeNewData(fullFeatureset,weights)
    else:
        fullFeatureset, weights = equalizeTrainData(fullFeatureset,limit = limit)
        # Save list for next time
        np.savetxt(weightData, weights, delimiter = ',', fmt = '%s')
    
    # Make test_set, valadation_set and train_set
    test_set  = fullFeatureset[testRows]
    val_set   = fullFeatureset[valRows]
    train_set = np.delete(fullFeatureset,allRows,axis = 0)
    
    # Save test_set and train_set
    writeMe(train_set,trainData,correctName=True)
    writeMe(test_set,testData,correctName=True)
    writeMe(val_set,valadationData,correctName=True)
    
def writeMe(data,path,emptyFirst = True, replaceLabel = False,correctName = False):
    """
    Function writes a new featureset using the data provided. This can be used
    to write a new featuerset, add entries to an existing one, or convert a
    featureset designed for a regressor into one built for a classifier. It
    is fully agnostic to the number of features, but assumes that the second
    to last entry is the featureset is the lable.
    """
    
    # Empty outfile
    if emptyFirst:
        with open(path, 'w+') as f:
            f.write('')
    
    # Write Entry, one at a time into file in .csv format
    for datum in data:
        
        #Allow for varible lenght entries
        entryLength = len(datum)
        
        if replaceLabel:
            labelLocation = entryLength - 2
        else:
            labelLocation = entryLength + 2
            
        if correctName:
            nameLocation = entryLength - 1
        else:
            nameLocation = entryLength + 1
        
        #Write actual entry
        with open(path, 'a+') as f:
            for i in range(entryLength):
                if i != labelLocation:
                    if i != nameLocation:
                        f.write(str(datum[i]))
                    else:
                        #f.write(str(datum[i]).split('b\'')[1].split('\'')[0])
                        #print(datum.shape)
                        f.write(str(datum[i]))
                elif datum[i] != 0 and datum[i] != '0':
                    f.write('1')
                else:
                    f.write(datum[i])
                if i < entryLength - 1:
                    f.write(',')
            f.write('\n')
