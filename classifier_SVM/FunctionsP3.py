#-------------------------------------------------------------------------------
# FunctionsP3.py
#
# Functions for extraction of magnetic complexity features from magnetograms.
#
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

from astropy.io import fits
from scipy.signal import *
import numpy as np
from scipy.stats import skew,kurtosis
from scipy import ndimage
import pywt
from skimage import measure

#written Spring 2018,
#Last update: Summer 2019
# lboucher fixed unsignedSum feature 10/20/2021

def fluxValues(magnetogram):
    #compute sum of positive and negative values,
    #then evaluate a signed and unsigned sum.
    posSum = np.sum(magnetogram[magnetogram>0])
    negSum = np.sum(magnetogram[magnetogram<0])
    signSum = posSum + negSum
    unsignSum = posSum-negSum
    
    return posSum,negSum, signSum, unsignSum


def gradient(image):
    #use sobel operators to find the gradient
    sobelx = [[-1,0,1],[-2,0,2],[-1,0,1]]
    sobely = [[1,2,1],[0,0,0],[-1,-2,-1]]
    
    gx = convolve2d(image,sobelx,mode='same')
    gy = convolve2d(image,sobely,mode='same')
    
    M = (gx**2 + gy**2)**(1./2)
    
    return M


def Gradfeat(image):
    #evaluate statistics of the gradient image
    res = gradient(image).flatten()
    men = np.mean(res)
    strd = np.std(res)
    med = np.median(res)
    minim = np.amin(res)
    maxim = np.amax(res)
    skw = skew(res)
    kurt = kurtosis(res)
    return men,strd,med,minim,maxim,skw,kurt


def wavel(image):
    #create wavelet transform array for display
    #can be added to the return statement for 
    #visualization
    wt = pywt.wavedecn(image,'haar',level=5)
    arr, coeff_slices = pywt.coeffs_to_array(wt)
    
    #compute wavelet energy
    LL,L5,L4,L3,L2,L1 = pywt.wavedec2(image,'haar',level=5)
    L1e = np.sum(np.absolute(L1))
    L2e = np.sum(np.absolute(L2))
    L3e = np.sum(np.absolute(L3))
    L4e = np.sum(np.absolute(L4))
    L5e = np.sum(np.absolute(L5))
    
    return L1e,L2e,L3e,L4e,L5e


def extractNL(image):
    avg10 = (1. / 100)*np.ones([10,10])
    avgim = convolve2d(image,avg10,mode='same')
    out = measure.find_contours(avgim,level = 0)
    return out


def NLmaskgen(contours,image):
    mask = np.zeros((image.shape))
    for n,contour in enumerate(contours):
        #print(n,contour)
        for i in range(len(contour)):
            y = int(round(contour[i,1]))
            x = int(round(contour[i,0]))
            mask[x,y] = 1.
    return mask


def findTGWNL(image):
    m = 0.2*np.amax(np.absolute(image))
    width = image.shape[0]
    height = image.shape[1]
    out = np.zeros([height,width])
    out[abs(image)>=m] = 1
    
    return out


def curvature(contour):
    angles = np.zeros([contour.shape[0]])
    yvals = np.around(contour[:,1])
    xvals = np.around(contour[:,0])
    for i in range(contour.shape[0]):
        if i < contour.shape[0]-1:
            n = i+1
        else:
            n = 0
        y = int(yvals[i])
        x = int(xvals[i])
        yn = int(yvals[n])
        xn = int(xvals[n])
        num = yn-y
        den = xn-x
        if den != 0:
            angles[i] = np.arctan(num/den)
        elif num < 0:
            angles[i] = 3*np.pi/2
        else:
            angles[i] = np.pi/2
    return angles


def bendergy(angles):
    fact = 1. / len(angles)
    count = 0.
    for i in range(len(angles)):
        if i < len(angles)-1:
            n = i+1
        else:
            n = 0
        T = angles[i]
        Tn = angles[n]
        count += (T-Tn)**2
        
    BE = count*fact
    return BE


def NLfeat(image):
    grad = gradient(image)
    contours = extractNL(image)
    ma = NLmaskgen(contours,image)
    gwnl = np.zeros([grad.shape[0],grad.shape[1]])
    gwnl = grad*ma
    thresh = findTGWNL(gwnl)
    NLlen = np.sum(thresh)
    
    struct = [[1,1,1],[1,1,1],[1,1,1]]
    lines, numlines = ndimage.label(thresh,struct)
    
    GWNLlen = np.sum(ma)
    Flag = True
    if not contours:
        return 0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.
    else:
        for n,contour in enumerate(contours):
            curve = curvature(contour)
            if Flag:
                angstore = np.zeros([len(curve)])
                angstore = curve
                BEstore = np.zeros([len(contours)])
                Flag = False
            else:
                angstore = np.concatenate((curve,angstore))
            BEstore[n] = bendergy(curve)
    
    return float(NLlen),float(numlines),float(GWNLlen),float(np.mean(angstore)),np.std(angstore),np.median(angstore),np.amin(angstore),np.amax(angstore),np.mean(BEstore),np.std(BEstore),np.median(BEstore),np.amin(BEstore),np.amax(BEstore)

