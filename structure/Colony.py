class Colony():
    def __init__(self, mask, image):
        self.mask = mask
        self.image = image
        self.score = None
        
    def getScore(self):
        if self.score == None:
            self.score = self.calcScore()
        return self.score
        
    def calcScore(self):
        return 2. #TODO
        
        