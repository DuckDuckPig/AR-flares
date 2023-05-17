# Created on Tue Feb  6 12:45:19 2018
#
# Script for interacting with the JSOC_ExportData webpage and downloading AR cutouts
#
# User should configure: executable path for firefox web browser driver 
# (geckodriver) on line 71
#
# References:
# [1] L. E. Boucheron, T. Vincent, J. A. Grajeda, and E. Wuest, "Solar Active 
#     Region Magnetogram Image Dataset for Studies of Space Weather," arXiv 
#     preprint arXiv:2305.09492, 2023.
#
# Copyright 2022 Ty Vincent, Laura Boucheron
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

from __future__ import division, print_function
import os
import os.path
import time
import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import glob
import pdb

# User defined variables:
geckodriver_path = './geckodriver' # path to firefox browser driver
user_email = 'youremail@youremail.com' # your email
ARList_path = './' # directory in which ARList.txt is stored
store_path = '/mnt/store/active_regions' # directory in which to store downloaded data; will create a directory for each AR underneath the specified directory

# super_get Function is "supposed to" stop the window from sending alerts, 
# It only seems to work sometimes though.
def super_get(browser, url):
    browser.get(url)
    browser.execute_script("window.alert = function() {};")
    
# Main function of the program, takes in:
# a noaa number for the downloading AR
# the date in yyyymmdd format and converts it to datetime
# The download directory as a full path
# And the number of days in the future you want to get as an integer
def download_fits(noaaNum, date, direc, future):
    
    # DEALS WITH DATE_TIME ISSUES
    # _________________________________________________________________________
    a = list(date)
    year = a[0] + a[1] + a[2] + a[3]
    month = a[4] + a[5]
    day = a[6] + a[7]
    date = datetime.date(int(year),int(month),int(day))
    
    date_time = date.strftime("%Y.%m.%d") + '_' + '00:00:00' + '_TAI'
    
    # Past_date is a misleading name, it should be future date but it was a 
    # relic that I left
    past_date = date + datetime.timedelta(days=int(future))
    
    # Format the date and time to YYYY.mm.dd
    future_date_time = past_date.strftime("%Y.%m.%d") + '_' + '00:00:00' + '_TAI'
    #print(past_date_time)
    # _________________________________________________________________________
    
    # CHANGE DOWNLOAD DIR
    # The profile for a chrome directory is commented below firefox, either 
    # will work but some of the alert tools may not work with chrome
    # _________________________________________________________________________
    profile = webdriver.FirefoxProfile()
    profile.set_preference("browser.download.folderList", 2)
    profile.set_preference("browser.download.manager.showWhenStarting", False)
    profile.set_preference("browser.download.dir", direc)
    
    # The following line is important, it sets the mime-type so that firefox 
    # will not ask you "are you sure?" every time
    # application/x-tar is the mime-type of a tar file
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/x-tar")

    browser = webdriver.Firefox(firefox_profile=profile, executable_path=geckodriver_path)
    
    super_get(browser, 'http://jsoc.stanford.edu/ajax/exportdata.html')
    
    #chrome_options = webdriver.ChromeOptions()
    #prefs = {'download.default_directory' : direc}
    #chrome_options.add_experimental_option('prefs', prefs)
    #browser = webdriver.Chrome(chrome_options=chrome_options)
    #time.sleep(1)
    
    # _________________________________________________________________________
    # time.sleep() is an incredibly important command, if the browser moves 
    # too quickly it can get into strange states and cause errors
    time.sleep(5)

    elem = browser.find_element_by_name('ds')  # Find the Record set box and set its value
    # _________________________________________________________________________
    # This line is what sets the insturment and range you are pulling
    elem.send_keys('hmi.M_720s[' + date_time + '-' + future_date_time + ']')
    # _________________________________________________________________________
    
    time.sleep(1)
    
    # Change from url (single fits files) to a tar file
    urlSelect = Select(browser.find_element_by_id('ExportMethod'))
    urlSelect.select_by_visible_text('url-tar')
    
    time.sleep(1)
    
    # Select the processing checkbox
    # NOTE: elem.location_once_scrolled_into_view is very important, 
    # it scrolls the page so that the element is in view, this can cause A LOT 
    # of errors if not present
    elem = browser.find_element_by_id('ProcessingCheckbox')  # Find and set the width pixel value to 600
    elem.location_once_scrolled_into_view
    browser.find_element_by_id('ProcessingCheckbox').click()
        
    # Selects the im_patch option, there are several options however that you 
    # may be interested in
    time.sleep(5)
    browser.find_element_by_id('OptionImPatch').click()

    time.sleep(5)
    # The code is full of try: excepts: to deal with unchecked boxed and alerts
    try:
        elem = browser.find_element_by_id('ImNOAA')
        elem.location_once_scrolled_into_view
        
        # Sometimes the form will not auto fill, these options will reset the 
        # fields and cause the autofill to happen
        browser.find_element_by_id('ImEastLimb').click()
        time.sleep(2)
        browser.find_element_by_id('ImEastLimb').click()
        time.sleep(2)
        
        # Write the NOAA numberto auto fill the center location
        elem.send_keys(Keys.CONTROL + "a")
        elem.send_keys(Keys.DELETE)
        elem.send_keys('1'+noaaNum)
    except:
        # An error here is caused by the ImPatch option not being checked
        browser.find_element_by_id('OptionImPatch').click()
        elem = browser.find_element_by_id('ImNOAA')
        elem.location_once_scrolled_into_view
        
        browser.find_element_by_id('ImEastLimb').click()
        time.sleep(2)
        browser.find_element_by_id('ImEastLimb').click()
        time.sleep(2)
        
        elem.send_keys(Keys.CONTROL + "a")
        elem.send_keys(Keys.DELETE)
        elem.send_keys('1'+noaaNum)
    
    time.sleep(2)
    
    # I noticed sometimes it would fill NOAA number then it would get removed, 
    # so I found it was best to do it twice
    elem = browser.find_element_by_id('ImNOAA')
    elem.location_once_scrolled_into_view
    elem.send_keys(Keys.CONTROL + "a")
    elem.send_keys(Keys.DELETE)
    elem.send_keys('1'+noaaNum)

    time.sleep(5)

    # Set the width and hight of the patch to 600x600
    elem = browser.find_element_by_name('ImWide')  # Find and set the width pixel value to 600
    elem.location_once_scrolled_into_view
    elem.send_keys(Keys.CONTROL + "a")
    elem.send_keys(Keys.DELETE)
    elem.send_keys('600')

    elem = browser.find_element_by_name('ImHigh')  # Find and set the Hight pixel value to 600
    elem.location_once_scrolled_into_view
    elem.send_keys(Keys.CONTROL + "a")
    elem.send_keys(Keys.DELETE)
    elem.send_keys('600')

    time.sleep(5)

    # now go back and change quality keyword--cannot do this earlier as the 
    # auto-filling of the impatch will not work
    elem = browser.find_element_by_name('ds')  # Find the Record set box and set its value
    elem.location_once_scrolled_into_view
    elem.send_keys('[? quality >= 0 ?]') 

    # Fills the notify box out with user's email, whatever email you use needs 
    # to be registered with JSOC
    elem = browser.find_element_by_id('ExportNotify') # Find and fill the notify email text field
    elem.location_once_scrolled_into_view
    elem.send_keys(Keys.CONTROL + "a")
    elem.send_keys(Keys.DELETE)
    elem.send_keys(user_email)

    time.sleep(5)

    # Click the check paremeters button, then click the export button
    elem = browser.find_element_by_id('ExportCheckButton')
    elem.location_once_scrolled_into_view
    time.sleep(1)
    # Sometimes the export notify button will not let you click and throw an 
    # error, if that happens the solution is to just wait a bit
    try:
        browser.find_element_by_id('ExportCheckButton').click()
    except:
        time.sleep(10)
        
    # Click export notify button 2 more times, to ensure everything is working
    time.sleep(5)
    browser.find_element_by_id('ExportCheckButton').click()
    time.sleep(5)
    browser.find_element_by_id('ExportCheckButton').click()
    time.sleep(5)
    
    # Find and click the Export button
    elem = browser.find_element_by_id('ExportButton')
    elem.location_once_scrolled_into_view
    time.sleep(1)
    browser.find_element_by_id('ExportButton').click()
    time.sleep(5)

    # Wait to get the status update (too short and you wont receive it)
    # Sometimes the request number wont autofill, so a manual fill forces its 
    # hand 
    request = browser.find_element_by_id('RequestIdPlace').text
    
    elem = browser.find_element_by_id('StatusRequestID') 
    elem.location_once_scrolled_into_view
    elem.send_keys(Keys.CONTROL + "a")
    elem.send_keys(Keys.DELETE)
    elem.send_keys(request)
    time.sleep(1)
    
    # Click the status button one time to see its message, it normally takes 3 
    # to 4 minuits for an active region to appear
    elem = browser.find_element_by_id('StatusButton')
    elem.location_once_scrolled_into_view
    time.sleep(1)
    browser.find_element_by_id('StatusButton').click()
    time.sleep(2)
    
    # Read the sataus message into a variable
    condition = browser.find_element_by_id('StatusButtonMsg').text
    
    # When the files are ready the status message will read "Please only click 
    # once for status request"
    while('Please only click once for status request' not in condition):
        browser.find_element_by_id('StatusButton').click()
        time.sleep(60)
        condition = browser.find_element_by_id('StatusButtonMsg').text
        # If the status message is empty that means the request failed to export
        if not condition:
            print("******* FAILED *******")
            break

    time.sleep(5)

    # This finds all hi\yper links containing .tar (There should only be 1)
    elems = browser.find_elements_by_partial_link_text('.tar')

    # This is a relic from when I was getting each file manually, but I left it 
    # just in case
    # For each element containing .tar, find its location and click it
    for elem in elems:
        elem.location_once_scrolled_into_view
        elem.click()
    
    # Sometimes the page will alert you about a .tar, this waits for it to 
    # appear and takes care of it
    try:
        WebDriverWait(browser, 3).until(EC.alert_is_present(),'Timed out waiting for Alert.')
        alert = browser.switch_to_alert()
        alert.accept()
    except:
        pass
    time.sleep(5)
    
    #__________________________________________________________________________
    # Wait for the file to be downloaded, tars get an extra .part file so as 
    # long as that is there, you aren't done
    list_of_files =os.listdir(direc+'/')
    print(list_of_files)
    h = 0
    while h == 0:
        time.sleep(2)
        list_of_files =os.listdir(direc+'/')
        print(list_of_files)
        if not any('.part' in s for s in list_of_files):
            h = 1;
        print(list_of_files)
    #__________________________________________________________________________
    
    # Leaving the page for google is the best way to avoid an annoying alert 
    # that you cant deal with
    super_get(browser, "https://www.google.com")
    time.sleep(5)
    try:
        alert = browser.switch_to_alert()
        alert.accept()
    except:
        pass
    time.sleep(5)
    
    # Attempt to close the browser
    browser.close()
    time.sleep(1)
    try:
        alert = browser.switch_to_alert()
        alert.accept()
    except:
        pass

# GET AR'S FROM THE PARSED TXT FILE AND DOWNLOAD EVERY AR FROM JSOC
# I have a text file with data set up like this:
# 2209,20141113,15
# NOAA,yyyymmdd,days 

with open((ARList_path + "/ARList.txt"),'r') as f:
    for line in f:
        #Splits each line into the NOAA Number, date, and future days needed
        a = line.split(',')
        noaaNum = a[0]
        date = a[1]
        future = a[2]
        # Estimate of the number of files
        files = int(future) * 121
        
        # Creates the directory, only if it does not exsist
        if not os.path.exists(store + '/' + noaaNum):
            os.makedirs(store + '/' + noaaNum)
        
        print("\n\nDownloading.....\n" + "NOAA Number: " + noaaNum + "\nDate       : " + date + "\nNumber of days: " + future)
        print("Total Files (estimated): " + str(files))
        
        # Download the files
        download_fits(noaaNum = noaaNum, direc = (store+'/'+noaaNum), date = date, future = future)
print ("\n*********************************************************************\nFinished Downloading files!")
