from PlateImage import *

class PlateExp():
    def __init__(self, images):
            self.images = []
            self.images += images
            self.stat = {}
            self.listPlateImages = []
    
    def addImages(self, images):
        for image in images:
            plImage = PlateImage(image)
            self.listPlateImages.append(plImage)
            
            self.images += images
        
    def calculate(self):
        for curPlate in self.listPlateImages:
            print curPlate.calc()
    
    def deleteImages(self):
        self.images = []
        self.listPlateImages = []

    