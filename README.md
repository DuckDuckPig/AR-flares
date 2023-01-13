# AR-flares
This github repository contains codes related to solar flare prediction using SDO HMI active regions.  This code is related to the data described in the Dryad repository at `<insert link here>` and in the paper `<insert link here>`.

This repository contains code related to general manipulation of the SDO HMI dataset (`<insert link here.`) and the use of that for two machine learning problems for flare prediction: 1) a classical machine learning problem using extracted features of magnetic complexity and a support vector machine (SVM) classifier and 2) a deep learning problem using transfer learning on the VGG network.

Requirements: [requirements.yml](requirements.yml)  
 - This environment file specifies all packages necessary for implementation of the SVM classification code, the VGG classification code, and the general code as described below.  Some packages may not be necessary for some code (e.g., tensorflow is not necessary for the SVM classification but is necessary for the VGG classification).
 - This environment file does NOT specify the `selenium` package which is needed by the `JSOC_driver.py` file.  Please see notes below about the fragility of the `JSOC_driver.py` code.

## SVM Classification
Code for the SVM classifier is included in the `classifier_SVM/` folder.  This code can operate on `.fits` files or `.png` files. 

![SVM classifier flowchart](/images/SVM_classifier_flowchart.png?raw=true "SVM Classifier Flowchart")

 - `Buid_Featureset.py`: Main code to extract 29 magnetic complexity features from HMI magnetograms.  This code is implemented using the python multiprocessing package, but can be modified for serial implementation.
   - Edit the lines under `## User Definitions` to specify paths and other parameters.  
   - Outputs a "FeatureFile" in `csv` format with the complexity features, labels (regression and classification), and filename.  The "FeatureFile" for the preconfigured reduced resolution dataset `Lat60_Lon60_Nans0_C1.0_24hr_png_224_features.csv` is available on Dryad at `<insert link here>` and for the full resolution dataset `Lat60_Lon60_Nans0_C1.0_24hr_features.csv` is available on Dryad at `<insert link here>`.
   - Relies on `FeaturesetTools.py`.  
   - Requires the "AR Dataset": the "Flare_Labels" file (`C1.0_24hr_224_png_Labels.txt` or `C1.0_24hr_Labels.txt`, available on Dryad at `<insert link here>` (reduced resolution `png` files) or `<insert link here>` (full resolution `fits` files)) and the corresponding "SDO HMI AR Images" available on Dryad at `<insert link here>` (reduced resolution `png` files) or `<insert link here>` (full resolution `fits` files)).  
 - `FeaturesetTools.py`: Helper functions for feature extraction.  
   - Relies on `FunctionsP3.py`.
 - `FunctionsP3.py`: Functions to extract magnetic complexity features.
 - `AR_Classifier.py`: Main code for the SVM classifier.  
   - Edit the lines under `## User Definitions` to specify paths and other parameters.  
   - Outputs three `csv` "FeatureFiles" with train, test, and validation data (i.e., the magnetic complexity features, filename, and label); a `txt` file "WeightFile" used for equalization of features, a `txt` file "Performance" wih classifier statistics, and a `pickle` file "Model" with the trained model. 
   - Relies on `FeaturesetTools.py`.  
   - Requires the "FeatureFile" output by `Build_Featureset.py` (`Lat60_Lon60_Nans0_C1.0_24hr_png_224_features.csv` (reduced resolution, available on Dryad at `<insert link here>`) or `Lat60_Lon60_Nans0_C1.0_24hr_features.csv` (full resolution, available on Dryad at `<insert link here>`)) and the "DataSplits" (lists of test and val active regions) `List_of_AR_in_Test_Data_by_AR.csv`, `List_of_AR_in_Train_data_by_AR.csv`, and `List_of_AR_in_Validation_data_by_AR.csv` available on Dryad (`<insert link here>` (reduced resolution) or `<insert link here>` (full resolution)).  Note--if the list of test and val active regions are not available, the code will randomly select 10% of active regions for the test and val sets; this will not result in the split as the files available on Dryad.
 
## VGG Classification
Code for the transfer learning of VGG is included in the `classifier_VGG/` folder.  This code can operate on `.fits` files or `.png` files.

![VGG classifier flowchart](/images/VGG_classifier_flowchart.png?raw=true "VGG Classifier Flowchart")

Code:
 - `Build_dataframes.py`: Code to generate files that can be read in as dataframes for the keras dataloaders.  
   - Edit the lines under `## User Definitions` to specify paths and other parameters.  
   - Outputs "Dataframes" in `csv` format with filename and classification label in the format expected for a tensorflow dataloader.  The "Dataframes" for the preconfigured reduced resolution dataset `Test_Data_by_AR_png_224.csv`, `Train_Data_by_AR_png_224.csv`, and `Validation_Data_by_AR_png_224.csv` are available on Dryad at `<insert link here>` and for the full resolution dataset `Test_Data_by_AR.csv`, `Train_Data_by_AR.csv`, and `Validation_Data_by_AR.csv` are available on Dryad at `<insert link here>`.
   - Requires the the "Flare_Labels" file from the "AR Dataset" (`C1.0_24hr_224_png_Labels.txt` or `C1.0_24hr_Labels.txt`, available on Dryad at `<insert link here>` (reduced resolution `png` files) or `<insert link here>` (full resolution `fits` files)) and the "DataSplits" (lists of test and val active regions) `List_of_AR_in_Test_Data_by_AR.csv`, `List_of_AR_in_Train_data_by_AR.csv`, and `List_of_AR_in_Validation_data_by_AR.csv` available on Dryad (`<insert link here>` (reduced resolution) or `<insert link here>` (full resolution)).   
 - `transfer_learning.ipynb`: jupyter notebook to perform transfer learning with the VGG16 architecture.
   - Comments throughout the notebook indicate paths and other paramters that can be specified.
   - Displays "Performance" within the notebook and outputs and `hdf5` files "Model" with the trained model for each epoch (can be configured to only output the final or best model with appropriate options in the tensorflow `model.fit` call.
   - Requires the the "Dataframe" files as output by `Build_dataframes.py`.  Additionally, The "Dataframes" for the preconfigured reduced resolution dataset `Test_Data_by_AR_png_224.csv`, `Train_Data_by_AR_png_224.csv`, and `Validation_Data_by_AR_png_224.csv` are available on Dryad at `<insert link here>` and for the full resolution dataset `Test_Data_by_AR.csv`, `Train_Data_by_AR.csv`, and `Validation_Data_by_AR.csv` are available on Dryad at `<insert link here>`.  Requires the "SDO HMI AR Images" corresponding to the files in the "Dataframes" available on Dryad at `<insert link here>` (reduced resolution `png` files) or `<insert link here>` (full resolution `fits` files)).  

## General code
General code for wrangling the dataset for use in classification are included in the `general_code/` folder.  If you are using the preconfigured dataset available at `<insert link here>`, you do not need to use any of this general code.  If you wish to download and/or generate a customized dataset, e.g., with different flare size or prediction window parameters, you will need to use some of this code.

![Dataset flowchart](/images/dataset_flowchart.png?raw=true "Dataset Flowchart")

Code:
 - `SRS_Parse.py`: Code to parse the Spece Weather Prediction Center (SWPC) Solar Region Summaries (SRS) to generate information used to download magnetogram images of all active regions appearing on disk within the timespan of the data.   
   - Edit the lines `## User Definitions` to specify paths and other parameters.  
   - Outputs a `txt` file "ARList" containing a list of all active regions present during the dataset timespan along with the starting date of appearance and number of days of existence.  This file is used by the `JSOC_Driver.py` code to download magnetograms.  The `ARList.txt` file for the timespan 2010-2018 is available on Dryad at `<insert link here>` or `<insert link here>`.
   - Requires the Solar Region Summaries (SRS)" directory structure available on Dryad at `<insert link here>` or `<insert link here>`.   This code assumes that you have downloaded the `SRS/` directory from `<insert link here>`.  
 - `JSOC_Driver.py`: Code to automate the interaction with the JSOC LookData webpage (<insert link here) to download magnetograms.  *NOTE--this code is extremely fragile and will break with browser driver changes and changes to the underlying html code used for the JSOC webpage.  This code is provided as is as a reference for those who may wish to modify the code for their purposes.  There is no guarantee that the code provided will currently work.*  This code will assume the presence of the `ARList.txt` file (see notes for `SRS_Parse.py` above).
   - Edit the lines under `# User define variables:` to specify paths and other parameters.  
   - Downloads and stores the "SDO HMI AR Images" associated with the "ARList" file.
   - Relies on the `selenium` package (not included in the requirements file above) and a driver appropriate for the browser (e.g., `geckodriver` for firefox).
   - Requires the "ARList" file output by `SRS_Parse.py` or available on Dryad at `<insert link here>` or `<insert link here>`.
 - `customize_dataset.py`: Code to generate a customized dataset based on flare size, flare prediction window, latitude, longitude, and number of NaNs.  This code assumes that you have downloaded all magnetogram images within the timespan of interest for the dataset.  This code will use an existing `eventList.txt` file or generate one for you if it does not exist; generation of an `eventList.txt` file assumes the existence of the `Events/` directory structure available for download at `<insert link here>`. You can download the `eventList.txt` file for the 2010-2018 timespan at `<insert link here>`.  This code will assume the existence of the `SRS/` directory structures as available for download at `<insert link here>`.  This code will copy the magnetogram images that satisfy the given parameters to a user-specified directory and generate a label file mapping those magnetograms to their flaring behavior.  
   - Edit the lines...
   - Outputs...
   - Relies on...
   - Requires...
