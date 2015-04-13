
import numpy as np
#import matplotlib.pyplot as plt
from skimage.morphology import watershed
import scipy.misc

from Colony import Colony

import sys

sys.path.append('../tutorial/scikit')
sys.path.append('../sample_images')
sys.path.append('../log_alg')


from image_funcs import *
import find_colonies
import log_alg

#Libs for cutPetri
from skimage import data, color
from skimage.transform import hough_circle
from skimage.feature import peak_local_max, canny
from skimage.draw import circle_perimeter
from skimage.util import img_as_ubyte
from skimage.exposure import rescale_intensity
from skimage.filters import canny
from scipy.ndimage import binary_fill_holes
from scipy.ndimage.morphology import binary_dilation, binary_erosion
from image_funcs import clear_border
from PIL import Image


class PlateImage():
    def __init__(self, image, algo=2 ):
        self.image = image
        self.colonies = None
        self.isCalc = None
        self.image_mask = None
        self.count = None
        self.pr_count = None
        self.algo = algo
        self.preview = None

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
        
        #--------------------------------------------------
        # If we want to, we can process this image to include blobmask too. 
        #
        # Since this is not needed for algo 2 colony intensity calculations, 
        # blobmask is NOT calculated so NOT passed further. 
        # Changes to algo2_divide_colonies() needed to include blobmask (if such necessity arises).
        
        if (False):
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
        #---------------------------------------------------
        
        self.algo2_divide_colonies(coords)
    
    def calc(self, data):
        if self.isCalc != None:
            return self.isCalc

        self.__init__(self.image)
        
        omega = 0.
        
        if self.algo == 1:
            self.algo1_segm()
        else:
            self.algo2_segm()
            
        assert self.colonies != None, "ERROR!"
        print "Recognised %d colonies" % len(self.colonies)
        
        self.pr_count = 0.
        for i in self.colonies:
            #omega += i.getScore()
            omega += i.gatherData(data);
            self.pr_count += 1.
        
        assert (self.count == int(self.pr_count)), "ERROR!"

        if self.pr_count != 0:
            self.isCalc = omega / self.pr_count
        else:
            self.isCalc = 0
        return self.isCalc

    def algo1_divide_colonies(self, labelled_image):
       self.colonies = []
       
       rescoeff = 0.1
       gsimage = np.max(self.image,2)
       gsimage = scipy.misc.imresize(gsimage, rescoeff)

       self.image_mask = labelled_image

       ctr = -1 # colony geometry index, starting from zero
       for colony in np.unique(labelled_image):
       
           if ctr == -1: # no background needed here!
               ctr += 1
               continue
               
           colony_part = np.zeros(labelled_image.shape)
           colony_part[labelled_image != colony] = 0

           newcol = Colony(colony_part, self.image, gsimage, rescoeff, 1)
           self.colonies.append(newcol)
           ctr+=1
           
    def algo2_divide_colonies(self, geometries):
       self.colonies = []
       
       rescoeff = 0.1
       gsimage = np.max(self.image,2)
       gsimage = scipy.misc.imresize(gsimage, rescoeff)

       for geom in geometries:
           newcol = Colony(None, self.image, gsimage, rescoeff, 2, geom)
           self.colonies.append(newcol)
           
    
    def circleAllColonies(self, score_min=0.0, score_max=255.0):
      self.preview = self.image
      im_shape = self.preview.shape
      
      for colony in self.colonies:
          colony_score = colony.getScore()
          colony_geom = colony.getGeom()
          circle_image, circle_mask = log_alg.circle_colony(colony_geom, colony_score, im_shape, score_min, score_max)
          
          # add circle to initial image of plate        
          self.preview[circle_mask] = 0
          self.preview += circle_image
          
      return self.preview      
