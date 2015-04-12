from PlateImage import *

class PlateExp():
    def __init__(self):
            self.images = []
            self.listPlateImages = []
            self.stat = {}
    
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

