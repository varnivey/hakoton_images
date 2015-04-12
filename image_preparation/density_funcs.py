import matplotlib.pyplot as plt
import numpy as np
from image_funcs import *
from scipy.misc import imread, imsave
import scipy.misc

def integrate(img, x, y, r):
	w, h = img.shape
	s = 0.0
	n = 0
	r2 = r**2
	for i in range(-r, r+1):
		for j in range(-r, r+1):
			currX = x + i
			currY = y + j
			if currX >= w or currX < 0 or currY >= h or currY < 0 or (i**2 + j**2) > r2:
				continue
			else:
				s += img[currX][currY]
				n += 1
	if n != 0:
		s /= n
	return s
		
	
def maxDensity(img, x, y, R, r):
	retval = 255.0
	w, h = img.shape
	for i in range(-R, R+1):
		for j in range(-R, R+1):
			currX = x + i
			currY = y + j
			if currX >= w or currX < 0 or currY >= h or currY < 0:
				continue
			else:
				tmp = integrate(img, currX, currY, r)
				if(tmp < retval):
					retval = tmp
	return retval

image = imread("3_cropped.png")
image = np.max(image, 2)
k = 0.3
rad = 10
image = scipy.misc.imresize(image, k)
densities = []
with open('circles_in_3_cropped') as f:
    for line in f: # read rest of lines
	nums = line.split()
	if(len(nums) < 3):
		continue
        densities.append(maxDensity(image, int(int(nums[0]) * k), int(int(nums[1]) * k), int(int(nums[2]) * k), rad))
print(densities)
