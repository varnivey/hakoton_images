from skimage import data, feature, exposure
from scipy.misc import imread, imsave
from scipy.ndimage.morphology import binary_dilation, binary_erosion
import scipy.misc
import numpy as np

def contrast(image, threshold):
	for i in range(0, image.shape[0]):
		for j in range(0, image.shape[1]):
			if image[i][j] > threshold:
				image[i][j] = 255
			else:
				image[i][j] = 0

img = imread('3_cropped.png')
img = np.max(img, 2)
img = scipy.misc.imresize(img, 0.20)
diamond = np.array([0,1,0,1,1,1,0,1,0], dtype=bool).reshape((3,3))
#img = exposure.equalize_hist(img)  # improves detection
#img = feature.blob_log(img, threshold = 0.3)
#print(img)

from skimage.filter import threshold_otsu
thres = threshold_otsu(img)
print(thres)
contrast(img, thres)
#img = binary_dilation(img, diamond)
#img = binary_erosion(img, diamond)
#img = binary_dilation(img, diamond)
#img = binary_erosion(img, diamond)
#img = binary_dilation(img, diamond)
#img = binary_erosion(img, diamond)
#img = binary_erosion(img, diamond)
#img = binary_erosion(img, diamond)
imsave('nuclei.jpg', img)
