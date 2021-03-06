from PlateImage import *
from skimage.filters import threshold_otsu

class PlateExp():
    def __init__(self):
            self.images = []
            self.listPlateImages = []
            self.usedpaths = []
            self.stat = {}
            self.allexpdata=[]
    
    def addImages(self, images):

        self.images += images
        for i in range(len(images)):
            masks = []
            masks += self.cutPetri(i)
            for j in range(len(masks)):
                plImage = PlateImage(images[i]*masks[j])
                self.listPlateImages.append(plImage)
        
    def calculate(self):
        for curPlate in self.listPlateImages:
            print curPlate.calc(self.allexpdata)
    
    def deleteImages(self):
        self.images = []
        self.listPlateImages = []
    
    def cutPetri(self, number_of_image):
        
        image = self.images[number_of_image]
        
        image = np.max(image, 2)
        
        rescaled_image = rescale_intensity(image, in_range=(np.min(image),np.min(image)+150))

        thres = threshold_otsu(rescaled_image)
        binary = rescaled_image > thres
 
        edges = canny(rescaled_image, sigma = 1, high_threshold = 35., low_threshold = 14.)

        diamond = np.array([0,1,0,1,1,1,0,1,0], dtype=bool).reshape((3,3))

        for i in range(10):
            edges = binary_dilation(edges, diamond)

        for i in range(5):
            edges = binary_erosion(edges, diamond)
            
        edges = remove_small_objects(edges, 4000)
            
        binary = binary_fill_holes(edges)

        binary -= edges
                
        labels = label(binary)

        
        images = []
        label_nums = np.unique(labels)

        for i in range(1, 3):
            new_image = np.zeros_like(labels, dtype=np.bool)
            new_image[labels == label_nums[i]] = 1
            new_image = np.dstack((new_image, new_image, new_image))
            images.append(new_image)
            
        return images

    def genPreviews(self):
    
        maxval = np.max(self.allexpdata)
        minval = np.min(self.allexpdata)
        for plate in self.listPlateImages:
        
            plate.circleAllColonies(minval, maxval)
    