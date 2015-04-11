# -*- coding: utf-8 -*-
"""
Created on Sat Apr 11 20:21:49 2015

@author: yalie
"""

import numpy as np
import matplotlib.pyplot as plt

from scipy.misc import imread

from scipy.ndimage.morphology import binary_dilation, generate_binary_structure
from scipy.ndimage import distance_transform_edt

from skimage.morphology import remove_small_objects, watershed
from skimage.measure import label
from skimage.feature import peak_local_max
from skimage.filter import threshold_otsu

import sys
sys.path.append('/home/yalie/Documents/Genehack/hakoton_images/tutorial/scikit')
from image_funcs import colorize


def binarize_image(plate_image):
    # select most contrast layer
    plate_layer = plate_image[..., 1]
    
    # otsu algorihm for image binarization
    thres = threshold_otsu(plate_layer)
    plate_binary = plate_layer > thres
    
    return plate_binary
    
    
def incorporate_cells(binary_image):    
    # invert input binary image
    inv_image = np.invert(binary_image)
    
    # matrix for binary_dilation
    struct = generate_binary_structure(2, 1)

    # do bunary dilation until the colony number even out
    plate_bin_dil = binary_dilation(inv_image, structure=struct)
    plate_dil_labels = label(plate_bin_dil)
    labels_number = len(np.unique(plate_dil_labels))  # initial number of colonies
    new_labels_number = labels_number - 1  # starting value
    cycle_number = 0  # starting value for dilation cycles
    while True:
        cycle_number += 1
        if cycle_number >= 30:
            break  # defence against infinite cycling
        else:
            if new_labels_number >= labels_number:
                break   # further dilation is useless (in theory)
            else:
                labels_number = new_labels_number
                plate_bin_dil = binary_dilation(plate_bin_dil, structure=struct)
                plate_dil_labels = label(plate_bin_dil)
                new_labels_number = len(np.unique(plate_dil_labels))
                
    return plate_bin_dil
            

def image_segmentation(binary_image):
    # find center of each colony
    distance = distance_transform_edt(binary_image)
    local_maxi = peak_local_max(distance, indices=False, labels=binary_image, min_distance = 10)
    markers = label(local_maxi)
    
    # watershed algorithm of segmentation using found centers
    labels_ws = watershed(-distance, markers, mask=binary_image)
    
    return labels_ws


def mask_cleaning(labelled_image):    
    # remove small objects
    labels_large = remove_small_objects(labelled_image, 5000)
    
    return labels_large    
    

def divige_colonies(labelled_image):
    colonies = []
    
    for colony in np.unique(labelled_image):
        colony_part = np.zeros(labelled_image.shape)
        #colony_part = plate_image  # mask colonies on input image
        colony_part[labelled_image != colony] = 0
        
        colonies.append(colony_part)
    
    return colonies
    

if __name__ == "__main__":
    
    # read image from file
    plate = imread('3_cropped.png')
    
    # create initial binary mask
    bin_plate = binarize_image(plate)
    
    # incorporate separated cells in large colonies
    bin_col_plate = incorporate_cells(bin_plate)
    
    # divide groups of colonies into separate ones
    colonies_mask = image_segmentation(bin_col_plate)

    # filter false objects from mask
    colonies_masked_clean = mask_cleaning(colonies_mask)
    plt.imshow(colorize(colonies_masked_clean))
    
    # divide colonies into different objects
    # may be not necessary operation
    # colony_array = divide_colonies(colonies_masked_clean)

