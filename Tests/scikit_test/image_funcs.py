import numpy as np
from skimage.measure import label

from skimage.filter import gaussian_filter, canny
from skimage.morphology import binary_dilation, binary_erosion
from skimage.morphology import remove_small_objects

from scipy.ndimage import distance_transform_edt
from skimage.feature import peak_local_max
from skimage.morphology import watershed

def fill_holes(edges):
    '''Fill holes in binary image'''

    binary = edges.copy()

    labels = label(binary)

    labelcount = np.bincount(labels.ravel())

    bg = np.argmax(labelcount)

    binary[labels != bg] = True

    return binary


def clear_border(labels):
    '''Removes objects which touch the border'''

    borders = np.zeros(labels.shape, np.bool)

    borders[ 0,:] = 1
    borders[-1,:] = 1
    borders[:, 0] = 1
    borders[:,-1] = 1

    at_border = np.unique(labels[borders])

    for obj in at_border:
        labels[labels == obj] = 0

    return labels

def double_dilation(binary, selem):
    '''Returns the result of two sequential binary dilations'''

    for i in (1,2):
        binary = binary_dilation(binary, selem)

    return binary

def double_erosion(binary, selem):
    '''Returns the result of two sequential binary erosions'''

    for i in (1,2):
        binary = binary_erosion(binary, selem)

    return binary

def colorize(labels):
    '''Colorize cells in such a way that neighbour cells have distict colors'''

    label_nums = np.unique(labels)
    new_image = np.zeros_like(labels, dtype=np.float)

    for i in range(label_nums.size):
        if i == 0:
            continue
        new_image[labels == label_nums[i]] = i*0.27

    new_image = (new_image % 1.)*0.7 + 0.3
    new_image[labels == label_nums[0]] = 0.

    return new_image


def get_binary(cells):
    '''Returns binary image with cells'''

    if (len(cells.shape) == 3):
        cells = np.max(cells, 2)

    blured = gaussian_filter(cells,8)
    highpass = cells - 0.8*blured
    sharp = highpass + cells
    sharp = np.floor(sharp).astype(np.uint8)

    diamond = np.array([0,1,0,1,1,1,0,1,0], dtype=bool).reshape((3,3))

    edges = canny(sharp, sigma = 1, high_threshold = 35., low_threshold = 14.)
    edges = double_dilation(edges, diamond)
    binary = fill_holes(edges)
    binary = double_erosion(binary, diamond)

    return binary


def calc_prot_intensity(labels, prot_pic):
    '''Return an array of protein intensities inside cells'''

    result = []

    for label in np.unique(labels):
        if label == 0:
            continue
        prot_values = np.extract(labels == label,prot_pic)
        result.append(np.mean(prot_values))

    return result


def get_labels(binary):
    '''Return image with labeled cells'''

    distance = distance_transform_edt(binary)
    distance_blured = gaussian_filter(distance, 8)
    local_maxi = peak_local_max(distance_blured, indices=False, labels=binary, min_distance = 10)
    markers = label(local_maxi)
    labels = watershed(-distance, markers, mask=binary)
    labels = remove_small_objects(labels, 4000)
    labels = clear_border(labels)
    return labels

def get_cell_number(cells):
    '''Return number of cells in the image given'''

    binary = get_binary(cells)
    labels = get_labels(binary)

    return np.unique(labels).size - 1


