# -*- coding: utf-8 -*-

'''

Этот файл cодержит последовательность команд, которые необходимо выполнять в
интерактивном режиме. Не пытайтесь его запускать или импортировать: это не
имеет смысла.

'''

import matplotlib.pyplot as plt
import numpy as np
plt.ion()                 # включение интерактивного режима matplotlib
from image_funcs import * # импорт всех функций из файла image_funcs.py
from scipy.misc import imread, imsave

###############################################################################
####  Чтение, запись, визуализация и преобразование в ч/б формат тестового ####
####  рисунка                                                              ####
###############################################################################
nuclei = imread('test_dna.jpg')
nuclei.shape
(1024, 1360, 3)
nuclei = np.max(nuclei, 2)
nuclei.shape
(1024, 1360)
plt.imshow(nuclei)
plt.gray()
imsave('nuclei.jpg', nuclei)
################################################################################


################################################################################
#### Перерастягивание интенсивности пикселей с использованием всего         ####
#### допустимого диапазона значений (от 0 до 255)                           ####
################################################################################
from skimage.exposure import rescale_intensity
rescaled_nuclei = rescale_intensity(nuclei, in_range=(np.min(nuclei),np.max(nuclei)))
plt.imshow(rescaled_nuclei)

new_range = tuple(np.percentile(nuclei,(2,98)))
rescaled_nuclei = rescale_intensity(nuclei, in_range=new_range)
plt.imshow(rescaled_nuclei)
################################################################################


################################################################################
#### Применение фильтров, создание рисунка с повышенной чёткостью границ    ####
################################################################################
from skimage.filter import gaussian_filter
blured = gaussian_filter(nuclei,8)
plt.imshow(blured)

highpass = nuclei - 0.8*blured
sharp = highpass + nuclei
sharp = np.floor(sharp).astype(np.uint8)

fig, ax = plt.subplots(1,2)
plt.gray()
ax[0].imshow(nuclei)
ax[1].imshow(sharp)
################################################################################


################################################################################
#### Бинаризация изображений (белые клетки, чёрный фон)                     ####
################################################################################
# Алгоритм Отсу (первого порядка)
from skimage.filter import threshold_otsu
thres = threshold_otsu(rescaled_nuclei)
binary = rescaled_nuclei > thres
plt.imshow(binary)

# Алгоритм кэнни (второго порядка)
from skimage.filter import canny
edges = canny(sharp, sigma = 1, high_threshold = 35., low_threshold = 14.)
plt.imshow(edges)

# Неудачный способ заливки границ
from scipy.ndimage import binary_fill_holes
binary = binary_fill_holes(edges)
plt.imshow(binary)

# Правильный способ заливки границ
from scipy.ndimage.morphology import binary_dilation, binary_erosion
diamond = np.array([0,1,0,1,1,1,0,1,0], dtype=bool).reshape((3,3))

edges = double_dilation(edges, diamond)
plt.imshow(edges)

binary = fill_holes(edges)
plt.imshow(binary)

binary = double_erosion(binary, diamond)
plt.imshow(binary)
################################################################################


################################################################################
#### Нумерация, сегментация, удаление малых объектов и объектов на границе  ####
#### изображения                                                            ####
################################################################################
from skimage.measure import label
labels = label(binary)
plt.jet()
plt.imshow(colorize(labels))

from skimage.morphology import remove_small_objects
labels = remove_small_objects(labels, 4000)
labels = clear_border(labels)
plt.imshow(labels)

binary = labels != 0
plt.imshow(binary)

from scipy.ndimage import distance_transform_edt
from skimage.feature import peak_local_max
from skimage.morphology import watershed
from image_funcs import colorize

# Неудачный способ сегментации
distance = distance_transform_edt(binary)
local_maxi = peak_local_max(distance, indices=False, labels=binary, min_distance = 10)
markers = label(local_maxi)
plt.imshow(double_dilation(local_maxi,diamond))
labels_ws = watershed(-distance, markers, mask=binary)
plt.imshow(colorize(labels_ws))


# Правильный способ сегментации
distance_blured = gaussian_filter(distance, 8)
local_maxi = peak_local_max(distance_blured, indices=False, labels=binary, min_distance = 10)
markers = label(local_maxi)
labels_ws = watershed(-distance, markers, mask=binary)
plt.imshow(colorize(labels_ws))

# Подсчёт числа клеток
cell_number = np.unique(labels_ws).size - 1
print cell_number
################################################################################


################################################################################
#### Подсчёт интенсивности флуоресценции клеток, найденных ранее,           ####
#### и построение столбчатой диаграммы                                      ####
################################################################################
protein = imread('test_protein.jpg')
protein = np.max(protein,2)
plt.imshow(protein)
prot_int = calc_prot_intensity(labels_ws,protein)
print np.round(prot_int,2)

fig = plt.figure()
ax = fig.add_subplot(111)
n, bins, patches = ax.hist(prot_int, 10, normed=1, facecolor=(0.6,1. ,0.4), alpha=0.75)
ax.set_ylabel('Cell fraction')
ax.set_xlabel('Mean intensity')
################################################################################




