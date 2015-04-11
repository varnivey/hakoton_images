import matplotlib.pyplot as plt
import numpy as np
from image_funcs import *
from scipy.misc import imread, imsave

def grid(image, threshold):


###############################################################################
import scipy.misc
nuclei = imread('3.jpg')
nuclei = scipy.misc.imresize(nuclei, 0.05)
nuclei = np.max(nuclei, 2)
plt.imshow(nuclei)
plt.gray()
imsave('nuclei.jpg', nuclei)
################################################################################

binary = fill_holes(nuclei)
#imsave('nuclei.jpg', binary)


from skimage.exposure import rescale_intensity
rescaled_nuclei = rescale_intensity(nuclei, in_range=(np.min(nuclei),np.max(nuclei)))

new_range = tuple(np.percentile(nuclei,(2,98)))
rescaled_nuclei = rescale_intensity(nuclei, in_range=new_range)

from skimage.filter import gaussian_filter
blured = gaussian_filter(nuclei,8)
plt.imshow(blured)

highpass = nuclei - 0.8*blured
sharp = highpass + nuclei
sharp = np.floor(sharp).astype(np.uint8)

from skimage.filter import threshold_otsu
thres = threshold_otsu(rescaled_nuclei)
binary = rescaled_nuclei > thres


from skimage.filter import canny
edges = canny(sharp, sigma = 1, high_threshold = 35., low_threshold = 14.)

from scipy.ndimage.morphology import binary_dilation, binary_erosion
diamond = np.array([0,1,0,1,1,1,0,1,0], dtype=bool).reshape((3,3))

edges = double_dilation(edges, diamond)

binary = fill_holes(edges)

binary = double_erosion(binary, diamond)

imsave('bin.jpg', binary)
