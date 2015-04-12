
import numpy as np

from scipy.misc import imread, imsave
from scipy.misc import imresize
from scipy.ndimage.morphology import binary_dilation, binary_erosion, generate_binary_structure

from skimage import img_as_ubyte
from skimage.color import hsv2rgb
from skimage.draw import circle_perimeter
from skimage.filters import threshold_otsu as global_otsu
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


def circle_colony(colony_geometry, colony_score, image_shape):
    # color of circle
    hue_start, hue_stop = [0.0, 1/3.0]  # from 0 to 120 degrees hue colors
    score_min, score_max = [1.0, 3.0]  # colony scores from 1 till 3
    color_coeff = ((hue_stop - hue_start)/(score_max - score_min))*(colony_score - score_min)
    print(color_coeff)
    
    # create three layers of hsv image (black background) and binary mask
    x_max = image_shape[0]
    y_max = image_shape[1]
    mask_saturation = np.array([[0.0 for i in range(x_max)] for i in range(y_max)])
    mask_light = np.array([[0.0 for i in range(x_max)] for i in range(y_max)])
    mask_hue = np.array([[0.0 for i in range(x_max)] for i in range(y_max)])
    mask_binary = np.array([[False for i in range(x_max)] for i in range(y_max)])
    
    # find circle
    x, y, r = colony_geometry
    r = r*2
    rr, cc = circle_perimeter(x, y, np.round(r).astype(int))
    rr_new, cc_new = [], []
    
    for x_c,y_c in zip(rr,cc):
        if (x_c >= 0) and (x_c < x_max) and (y_c >= 0) and (y_c < y_max):
            rr_new.append(x_c)
            cc_new.append(y_c)
    
    # create binary mask with circle
    mask_binary[rr_new, cc_new] = True
    
    struct = generate_binary_structure(2, 1)
    for i in range(8):
        mask_binary = binary_dilation(mask_binary, struct)
    
    # paint circle in hsv layers
    mask_saturation[mask_binary] = 1.0
    mask_light[mask_binary] = 0.75
    mask_hue[mask_binary] = color_coeff
    
    hsv_image = np.dstack([mask_hue, mask_saturation, mask_light])
    
    rgb_image = img_as_ubyte(hsv2rgb(hsv_image))
    
    return rgb_image, mask_binary