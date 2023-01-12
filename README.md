# AR-flares
This github repository contains codes related to solar flare prediction using SDO HMI active regions.  This code is related to the data described in the Dryad repository at `<insert link here>` and in the paper `<insert link here>`.

This repository contains code related to general manipulation of the SDO HMI dataset (`<insert link here.`) and the use of that for two machine learning problems for flare prediction: 1) a classical machine learning problem using extracted features of magnetic complexity and a support vector machine (SVM) classifier and 2) a deep learning problem using transfer learning on the VGG network.

Requirements: `<put .yml file here>`  Note--this environment file specifies all packages necessary for implementation of the SVM classification code, the VGG classification code, and the general code as described below.  Some packages may not be necessary for some code (e.g., tensorflow is not necessary for the SVM classification but is necessary for the VGG classification).

## SVM Classification
Code for the SVM classifier is included in the `classifier_SVM/` folder.  This code can operate on `.fits` files or `.png` files. 
 - `BuidMasterFeatureSet_mp.py`: Main code to extract 29 magnetic complexity features from HMI magnetograms.  This code is implemented using the python multiprocessing package, but can be modified for serial implementation.
   - Edit the lines under `## User Definitions` to specify paths and other parameters.  
   - Outputs a `csv` file with the complexity features, labels (regression and classification), and filename.  
   - Relies on `FeaturesetTools.py`.  
   - Requires the label file (`C1.0_24hr_224_png_Labels.txt` or `C1.0_24hr_Labels.txt`) and the dataset (reduced resolution `png` files `<insert link here>` or the full resolution `fits` files `<insert link here>`).  
 - `FeaturesetTools.py`: Helper functions for feature extraction.  
   - Relies on `FunctionsP3.py`.
 - `FunctionsP3.py`: Functions to extract magnetic complexity features.
 - `AR_Classifier_weighted.py`: Main code for the SVM classifier.  
   - Edit the lines under `## User Definitions` to specify paths and other parameters.  
   - Outputs three `csv` files with train, test, and validation data, a weight file for equalization of features, a `txt` file wih classifier statistics, and a `pickle` file with the trained model.  
   - Relies on `FeaturesetTools.py`.  
   - Requires the feature file output by `BuildMasterFeatureSet.py` or available on Dryad (`Lat60_Lon60_Nans0_C1.0_24hr_png_224_features.csv` or `Lat60_Lon60_Nans0_C1.0_24hr_features.csv`) and the list of test and val active regions `List_of_AR_in_Test_Data_by_AR.csv`, `List_of_AR_in_Train_data_by_AR.csv`, and `List_of_AR_in_Validation_data_by_AR.csv` available on Dryad.  Note--if the list of test and val active regions are not available, the code will randomly select 10% of active regions for the test and val sets; this will not result in the split as the files available on Dryad.
 
## VGG Classification
Code for the transfer learning of VGG is included in the `classifier_VGG/` folder.  This code can operate on `.fits` files or `.png` files.

Requirements: `<put .yml file here>`
 
Code:
 - `Build_keras_dataframe_files.py`: Code to generate files that can be read in as dataframes for the keras dataloaders.  This code assumes that the train, test, and validation data files exist as output from `AR_Classifier_weighted.py`.  This code does a simple parsing of those files and outputs `csv` files with columns `filename, class`.  

## General code
General code for wrangling the dataset for use in classification are included in the `general_code/` folder.  If you are using the preconfigured dataset available at `<insert link here>`, you do not need to use any of this general code.  If you wish to download and/or generate a customized dataset, e.g., with different flare size or prediction window parameters, you will need to use some of this code.
 - `SRS_Parse.py`: Code to parse the Solar Region Summaries and generate the `ARList.txt` file that is used by the `JSOC_Driver.py` code to download magnetograms.  This code assumes that you have downloaded the `SRS/` directory from `<insert link here>`.  Alternatively, you can simply download the `ARList.txt` file from `<insert link here>` if you are using a dataset from the same timespan (2010-2018)
 - `JSOC_Driver.py`: Code to automate the interaction with the JSOC LookData webpage (<insert link here) to download magnetograms.  *NOTE--this code is extremely fragile and will break with browser driver changes and changes to the underlying html code used for the JSOC webpage.  This code is provided as is as a reference for those who may wish to modify the code for their purposes.  There is no guarantee that the code provided will currently work.*  This code will assume the presence of the `ARList.txt` file (see notes for `SRS_Parse.py` above).
 - `generate_dataset.py`: Code to generate a customized dataset based on flare size, flare prediction window, latitude, longitude, and number of NaNs.  This code assumes that you have downloaded all magnetogram images within the timespan of interest for the dataset.  This code will use an existing `eventList.txt` file or generate one for you if it does not exist; generation of an `eventList.txt` file assumes the existence of the `Events/` directory structure available for download at `<insert link here>`. You can download the `eventList.txt` file for the 2010-2018 timespan at `<insert link here>`.  This code will assume the existence of the `SRS/` directory structures as available for download at `<insert link here>`.  This code will copy the magnetogram images that satisfy the given parameters to a user-specified directory and generate a label file mapping those magnetograms to their flaring behavior.  
