
# coding: utf-8

# In[2]:

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

# In[3]:


def fluxValues(magnetogram):
    #compute sum of positive and negative values,
    #then evaluate a signed and unsigned sum.
    posSum = np.sum(magnetogram[magnetogram>0])
    negSum = np.sum(magnetogram[magnetogram<0])
    signSum = posSum + negSum
    unsignSum = posSum-negSum
    
    return posSum,negSum, signSum, unsignSum


# In[4]:


def gradient(image):
    #use sobel operators to find the gradient
    sobelx = [[-1,0,1],[-2,0,2],[-1,0,1]]
    sobely = [[1,2,1],[0,0,0],[-1,-2,-1]]
    
    gx = convolve2d(image,sobelx,mode='same')
    gy = convolve2d(image,sobely,mode='same')
    
    M = (gx**2 + gy**2)**(1./2)
    
    return M


# In[5]:


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


# In[6]:


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


# In[9]:


def extractNL(image):
    avg10 = (1. / 100)*np.ones([10,10])
    avgim = convolve2d(image,avg10,mode='same')
    out = measure.find_contours(avgim,level = 0)
    return out


# In[10]:


def NLmaskgen(contours,image):
    mask = np.zeros((image.shape))
    for n,contour in enumerate(contours):
        #print(n,contour)
        for i in range(len(contour)):
            y = int(round(contour[i,1]))
            x = int(round(contour[i,0]))
            mask[x,y] = 1.
    return mask


# In[11]:


def findTGWNL(image):
    m = 0.2*np.amax(np.absolute(image))
    width = image.shape[0]
    height = image.shape[1]
    out = np.zeros([height,width])
    out[abs(image)>=m] = 1
    
    return out


# In[12]:


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


# In[13]:


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


# In[14]:


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

