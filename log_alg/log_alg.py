
import numpy as np

from scipy.misc import imread, imsave
from scipy.misc import imresize

from skimage import img_as_ubyte
from skimage.draw import circle_perimeter
from skimage.filters import threshold_otsu as global_otsu
from scipy.ndimage.morphology import binary_dilation, binary_erosion
from skimage.feature import blob_log

def image_hsv_value(image_file):
    '''Converts image to grayscale'''

    pic_source = img_as_ubyte(imread(image_file))

    if pic_source.ndim == 3:
        pic_gray = np.max(pic_source,2)
    else:
        pic_gray = pic_source

    return pic_gray


def binarize(grayscale_image):
    '''Binarize 8-bit grayscale image'''

    thres = global_otsu(grayscale_image)

    return grayscale_image < thres


def label_colonies(gray, min_foci_radius = 50, max_foci_radius = 200, \
        overlap=0, log_thres = 0.04, scale = 4):
    '''Label colonies on the image'''

    binary = (1 - binarize(gray))*255.

    min_sigma = ((min_foci_radius/3.)*2)/scale
    max_sigma = ((max_foci_radius/3.)*2)/scale
#    num_sigma = np.floor(max_sigma - min_sigma).astype(int)/10 + 1
    num_sigma = 10

    if scale != 1:
        new_shape = np.floor(np.array(gray.shape)/np.float(scale)).astype(np.int)
#        print new_shape, min_sigma, max_sigma
        small_im  = imresize(binary, new_shape)
    else:
        small_im = binary

    blobs_log = blob_log(small_im, min_sigma=min_sigma, max_sigma=max_sigma,\
            num_sigma=num_sigma, threshold=log_thres, overlap = overlap/100.)

    markers_num = blobs_log.shape[0]

    blobs_log = np.floor(blobs_log*np.float(scale)).astype(np.int)

    markers_fin = circle_markers(blobs_log, gray.shape)

    circles = np.copy(gray)
    circles[markers_fin] = 255

    return [markers_num, circles, blobs_log]
#    return [markers_num, r, b]



def circle_markers(blobs, pic_shape):
    '''Return array with circles around foci found'''

    markers_rad = np.zeros(pic_shape, dtype = np.bool)

    x_max, y_max = pic_shape

    for blob in blobs:

        x, y, r = blob

        r = r*2

        rr, cc = circle_perimeter(x, y, np.round(r).astype(int))
        rr_new, cc_new = [], []

        for x_c,y_c in zip(rr,cc):

            if (x_c >= 0) and (x_c < x_max) and (y_c >= 0) and (y_c < y_max):
                rr_new.append(x_c)
                cc_new.append(y_c)

        markers_rad[rr_new, cc_new] = True

    selem = np.array([0,1,0,1,1,1,0,1,0], dtype=bool).reshape((3,3))

    for i in range(4):
        markers_rad = binary_dilation(markers_rad, selem)

    return markers_rad


