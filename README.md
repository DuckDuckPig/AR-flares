# AR-flares
This github repository contains codes related to solar flare prediction using SDO HMI active regions.  This code is related to the data described in the Dryad repository at `<insert link here>` and in the paper `<insert link here>`.

This repository contains code related to general manipulation of the SDO HMI dataset (`<insert link here.`) and the use of that for two machine learning problems for flare prediction: 1) a classical machine learning problem using extracted features of magnetic complexity and a support vector machine (SVM) classifier and 2) a deep learning problem using transfer learning on the VGG network.

## General code

## SVM Classification
Code for the SVM classifier is included in the `SVM` folder.  This code can operate on `.fits` files or `.png` files. 

Requires:
 - `os`
 - `glob`
 - `csv`
 - `astropy` (tested with version 4.2.1)
 - `imageio` (tested with version 2.9.0)
 - `multiprocessing` and `functools`
 - `numpy` (tested with version 1.19.2)
 - `copy`
 - `scipy` (tested with version 1.4.1)
 - `pywt` (tested with version 1.1.1)
 - `skimage` (tested with version 0.16.2)
 - `sklearn` (tested with version 0.24.2)
 - `pickle` (tested with 0.7.5)

Code:
 - `BuidMasterFeatureSet_mp.py`: Main code to extract 29 magnetic complexity features from HMI magnetograms.  Edit the lines under `## User Definitions` to specify paths and other parameters.  Outputs a `csv` file with the complexity features, labels (regression and classification), and filename.  Relies on `FeaturesetTools.py`.  Requires the label file (`C1.0_24hr_224_png_Labels.txt` or `C1.0_24hr_Labels.txt`) and the dataset (reduced resolution `png` files `<insert link here>` or the full resolution `fits` files `<insert link here>`).
 - `FeaturesetTools.py`: Helper functions for feature extraction.  Relies on `FunctionsP3.py`.
 - `FunctionsP3.py`: Functions to extract magnetic complexity features.
 - `AR_Classifier_weighted.py`: Main code for the SVM classifier.  Edit the lines under `## User Definitions` to specify paths and other parameters.  Outputs three `csv` files with train, test, and validation data, a weight file for equalization of features, a `txt` file wih classifier statistics, and a `pickle` file with the trained model.  Relies on `FeaturesetTools.py`.  Requires the feature file output by `BuildMasterFeatureSet.py` or available on Dryad (`Lat60_Lon60_Nans0_C1.0_24hr_png_224_features.csv` or `Lat60_Lon60_Nans0_C1.0_24hr_features.csv`) and the list of test and val active regions `List_of_AR_in_Test_Data_by_AR.csv` and `List_of_AR_in_Validation_data_by_AR.csv` available on Dryad.
 
## VGG Classification
