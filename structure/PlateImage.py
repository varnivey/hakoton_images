
import numpy as np
#import matplotlib.pyplot as plt
from skimage.morphology import watershed

from Colony import Colony

import sys

sys.path.append('../tutorial/scikit')
sys.path.append('../sample_images')
sys.path.append('../log_alg')

from image_funcs import *
import find_colonies
import log_alg

class PlateImage():
    def __init__(self, image, algo=2 ):
        self.image = image
        self.colonies = None
        self.isCalc = None
        self.image_mask = None
        self.count = None
        self.pr_count = None
        self.algo = algo

    def algo1_segm(self):
        # read image from file
        plate = self.image

        # create initial binary mask
        bin_plate = find_colonies.binarize_image(plate)

        # incorporate separated cells in large colonies
        bin_col_plate = find_colonies.incorporate_cells(bin_plate)

        # divide groups of colonies into separate ones
        colonies_mask = find_colonies.image_segmentation(bin_col_plate)

        # filter false objects from mask
        colonies_masked_clean = find_colonies.mask_cleaning(colonies_mask)
        # plt.imshow(colorize(colonies_masked_clean))
    
        # divide colonies into different objects
        # may be not necessary operation
        self.algo1_divide_colonies(colonies_masked_clean)
    
    def algo2_segm(self):
    
        green = self.image[:,:,1]
        prepimg = 255 - green
        self.count, pic_with_circles, coords = log_alg.label_colonies(prepimg) # TODO tweak parameters
        
        blobmask = log_alg.circle_markers(coords, prepimg.shape)
        blobmask = fill_holes(blobmask)
        
        circent_markers = np.zeros(prepimg.shape, dtype = np.integer)
        
        i = 1
        for point in coords:
            circent_markers[point[0]][point[1]] = i
            i += 1
        
        blobmask = watershed(blobmask, circent_markers, mask=blobmask) # TODO could divide better?
                
        
        # === DEBUG ===
        #plt.ion() 
        #plt.imshow(colorize(blobmask))
        # =============
        self.algo1_divide_colonies(blobmask, coords)
    
    def calc(self):
        if self.isCalc != None:
            return self.isCalc

        self.__init__(self.image)
        
        omega = 0.
        
        if self.algo == 1:
            self.algo1_segm()
        else:
            self.algo2_segm()
            
        assert self.colonies != None, "ERROR!"
        
        self.pr_count = 0.
        for i in self.colonies:
            omega += i.getScore()
            self.pr_count += 1.
        
        assert (self.count == int(self.pr_count)), "ERROR!"

        self.isCalc = omega / self.pr_count
        return self.isCalc

    def algo1_divide_colonies(self, labelled_image, geometry=[]):
       self.colonies = []

       self.image_mask = labelled_image

       ctr = -1 # colony geometry index, starting from zero
       for colony in np.unique(labelled_image):
       
           if ctr == -1: # no background needed here!
               ctr += 1
               continue
               
           colony_part = np.zeros(labelled_image.shape)
           #colony_part = plate_image  # mask colonies on input image
           colony_part[labelled_image != colony] = 0

           if (len(geometry)>0): # it was provided
               colony = Colony(colony_part, self.image, geometry[ctr])
           else:
               colony = Colony(colony_part, self.image)
               
           self.colonies.append(colony)
           ctr+=1
       
