#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8

import warnings
warnings.simplefilter('ignore')

print '\n\nMatplotlib import:'
try:
    import matplotlib.pyplot as plt
    print 'Done\n'
except:
    print 'WARNING: Matplotlib was not found. Proceeding..\n'

print 'Numpy import:'
import numpy as np
print 'Done\n'


print 'Scikit-image import:'
try:
    import skimage

    svers = skimage.__version__

    if eval(skimage.__version__.split('.')[1]) >= 10:
        print 'Scikit-image version ' + svers + ' was found'
    else:
        print 'WARNING: Outdated scikit-image version ' + svers + ' was found'
        print 'Proceeding..'
    print 'Done\n'

except:
    print 'WARNING: Scikit-image was not found. Proceeding..\n'
    raise


print 'Scipy import: '
import scipy

svers = scipy.__version__

if eval(scipy.__version__.split('.')[1]) >= 13:
    print 'Scipy version ' + svers + ' was found'
else:
    print 'WARNING: Outdated scipy version ' + svers + ' was found'
    print 'Proceeding..'
print 'Done\n'


print 'Starting scikit-image test'

try:

    from image_funcs import *
    from scipy.misc import imread, imsave

    nuclei = imread('test_dna.jpg')
    nuclei = np.max(nuclei, 2)

    from skimage.exposure import rescale_intensity
    rescaled_nuclei = rescale_intensity(nuclei, in_range=(np.min(nuclei),np.max(nuclei)))

    new_range = tuple(np.percentile(nuclei,(2,98)))
    rescaled_nuclei = rescale_intensity(nuclei, in_range=new_range)

    print '+rescale intensity'


    from skimage.filter import gaussian_filter
    blured = gaussian_filter(nuclei,8)

    highpass = nuclei - 0.8*blured
    sharp = highpass + nuclei
    sharp = np.floor(sharp).astype(np.uint8)

    from skimage.filter import canny

    edges_c = canny(sharp, sigma = 1, high_threshold = 35., low_threshold = 14.)
    diamond = np.array([0,1,0,1,1,1,0,1,0], dtype=bool).reshape((3,3))
    edges = double_dilation(edges_c, diamond)
    binary = fill_holes(edges)

    binary = double_erosion(binary, diamond)

    print '+binarization'


    from skimage.measure import label

    labels = label(binary)

    from skimage.morphology import remove_small_objects
    labels = remove_small_objects(labels, 4000)
    labels = clear_border(labels)

    binary = labels != 0

    from scipy.ndimage import distance_transform_edt
    from skimage.feature import peak_local_max
    from skimage.morphology import watershed

    distance = distance_transform_edt(binary)
    distance_blured = gaussian_filter(distance, 8)
    local_maxi = peak_local_max(distance_blured, indices=False, labels=binary, min_distance = 10)
    markers = label(local_maxi)
    labels_ws = watershed(-distance, markers, mask=binary)

    print '+segmentation'

    cell_number = np.unique(labels_ws).size - 1

    if cell_number == 38:
        print '+proper cell count'
        print 'scikit-image test passed\n'
    else:
        raise

except:
    print 'WARNING: scikit-image test failed. Proceeding..\n'


print 'Starting image plot test'

try:
    fig, ax = plt.subplots(2,2)
    fig.set_size_inches(6, 6, forward=True)
#    fig.subplots_adjust(0.05, 0.05, 0.95, 0.95, 0.05, 0.05)

    plt.gray()
    ax[0,0].imshow(rescaled_nuclei)
    ax[0,0].set_title('Rescaled intensity')
    ax[0,1].imshow(edges)
    ax[0,1].set_title('Canny edges')
    ax[1,0].imshow(binary)
    ax[1,0].set_title('Binary nuclei')
    plt.jet()
    ax[1,1].imshow(colorize(labels_ws))
    ax[1,1].set_title('Colorized nuclei')
    plt.jet()

    for a in ax:
        for b in a:
            b.set_xticks(())
            b.set_yticks(())

    plt.show()

    print 'Image plot test passed\n'

except:
    print 'WARNING: Image plot test failed. Proceeding..\n'


print 'Starting scipy test'

try:

    from scipy.optimize import leastsq
    from curve_funcs import *

    x = np.linspace(0,20,20)
    A,B,C,D = 0.5,2.5,8,7.3
    y_true = logistic4(x, A, B, C, D)

    y_meas = y_true + 0.2*np.random.randn(len(x))

    guess = [0, 1, 1, 1]
    plsq = leastsq(residuals, guess, args=(y_meas, x))

    print plsq
    print '+optimize'

    print 'scipy test passed\n'

except:
    '''WARNING: scipy test failed\n'''














