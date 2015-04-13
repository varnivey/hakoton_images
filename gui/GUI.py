#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) Grigoriy A. Armeev, 2015
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as·
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License v2 for more details.

# Cheers, Satary.
#

import sys,os,time
from PyQt4 import QtGui, QtCore
from table_widget import TableWidget
from image_widget import ImageWidget
from file_source_widget import FileSourceWidget

from scipy.misc import imread, imsave

sys.path.append("../structure")
from PlateExp import PlateExp

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s
    
class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.initUI()
        self.show()
        self.showingreznum = 1
    
    def initUI(self):
        '''
        Setting up Interface
        '''
        mainWidget = QtGui.QSplitter(QtCore.Qt.Horizontal)
        mainWidget.setSizes([1,3])
        
        self.fileMenu=FileSourceWidget(self)

        mainWidget.addWidget(self.fileMenu)
        

        tabs = QtGui.QTabWidget(self)
    
        images=QtGui.QWidget(self)
        imagesLayout=QtGui.QVBoxLayout(images)
        tabs.addTab(images,"Images")

        self.preview=ImageWidget(self)  
        imagesLayout.addWidget(self.preview)
        
        self.result=ImageWidget(self)  
        imagesLayout.addWidget(self.result)
        
       
        self.tableWidget=TableWidget(self)
        tabs.addTab(self.tableWidget,"Results")
        mainWidget.addWidget(tabs)
        
        controlWidget=QtGui.QWidget(self)
        controlLayout=QtGui.QVBoxLayout(controlWidget)
        controlLayout.setAlignment(QtCore.Qt.AlignTop)
        
        self.runButton=QtGui.QPushButton('Run calc')
        controlLayout.addWidget(self.runButton)     
        
        self.pbar = QtGui.QProgressBar(self) 
        controlLayout.addWidget(self.pbar)    
        
        mainWidget.addWidget(controlWidget)
        self.setCentralWidget(mainWidget)
        self.setWindowTitle('-PASTENAME-GUI')   
        
        self.assignConnections()
        
        
    def assignConnections(self):
        '''
        Assigning connections
        '''
        self.connect(self.fileMenu,QtCore.SIGNAL("updatePreviewImage"),self.open_image_file)
        
        self.connect(self.preview,QtCore.SIGNAL("imageWigetPressed"),self.previewClicked)
        self.connect(self.preview,QtCore.SIGNAL("imageWigetHovered"),self.previewHovered)
        
        self.connect(self.result,QtCore.SIGNAL("imageWigetPressed"),self.resultClicked)
        self.connect(self.result,QtCore.SIGNAL("imageWigetHovered"),self.resultHovered)
        
        self.runButton.clicked.connect(self.run_calculations)
    
    def previewClicked(self, coord, path):
        print "preview Clicked",coord, path
    
    def previewHovered(self, coord, path):
        print "preview Hovered",coord, path
         
    def resultClicked(self, coord, path):
        print "result Clicked, changing preview",coord, path
        
        # temporary (or not) solution for showing different plates per path:
        if self.showingreznum == 1:
            self.showingreznum = 2
        else:
            self.showingreznum = 1
            
        self.open_image_file(self.preview.currentPath)
         
    def resultHovered(self, coord, path):
        print "result Hovered",coord, path 
        
    def open_image_file(self,path):
        self.preview.setImage(path)
        rezpath = os.path.splitext(path)[0] + '_calcrezpreview_' + str(self.showingreznum) + os.path.splitext(path)[1]
        
        if (os.path.exists(rezpath) and os.path.isfile(rezpath)):
            self.result.setImage(rezpath)
        
    def open_image_calcrez(self,path):
        pass
        #self.preview.setImage(path)
        #self.result.setImage(path)
        
    def enable_runButton(self):
        self.runButton.setEnabled(True)
    
    def run_calculations(self):
        '''
        Running calculation in separate thread
        '''
        #Disable runButton
        self.runButton.setEnabled(False)
        #Setting up thread and worker
        self.workThread = QtCore.QThread()
        self.worker = Calculator(self.fileMenu.getSelectedPaths())
        self.worker.moveToThread(self.workThread)
        #connect signal for thread finish
        self.worker.finished.connect(self.workThread.quit)
        self.worker.finished.connect(self.enable_runButton)
        #connect signal for table update
        self.worker.signal_update_table.connect(self.update_table)
        #connect signal for status update 
        self.worker.signal_update_pbar.connect(self.updateProgressBar)
        #connect signal of started thread for running calculations
        self.workThread.started.connect(self.worker.run)
        #Run Forest! Run!
        self.workThread.start()
        
    def update_table(self,dictionary):
        self.tableWidget.buildFromDict(dictionary)
        
    def updateProgressBar(self,value):
        self.pbar.setValue(value)
        
class Calculator(QtCore.QObject,PlateExp): 
    signal_update_table = QtCore.pyqtSignal(dict) 
    signal_update_pbar = QtCore.pyqtSignal(int) 
    finished = QtCore.pyqtSignal()   
     
    def __init__(self,listOfPaths):
        QtCore.QObject.__init__(self)
        PlateExp.__init__(self)
        self.paths=listOfPaths
    
    def run(self):
        print 'started'
        #Add
        imgholder=[]
        self.usedpaths=[]
        print "Loading %d images..." % len(self.paths)
        
        for path in self.paths:
            try:
                img = imread(path)
            except:
                print "Error: Image read failed. Not processing this ( %s )" % path
                continue
                
            imgholder.append(img)
            self.usedpaths.append(path)
            print "Loaded image. ( %s )" % path
        
        self.addImages(imgholder)
        
        for upath in self.usedpaths:
            for i in range(1,3):
                rezpath = os.path.splitext(upath)[0] + '_calcrezpreview_'+ str(i) + os.path.splitext(upath)[1]
                if (os.path.exists(rezpath) and os.path.isfile(rezpath)):
                    print "Removing old result before calculation: " + rezpath
                    os.remove(rezpath)

        #print usedpaths
        print "------------------------------"
        print "Processing %d plates..." % len(self.listPlateImages)
        
        #Calculate
        status=0
        self.signal_update_pbar.emit(status*100/len(self.listPlateImages))
        dictionary = {}
        for curPlate in self.listPlateImages: # requires EXACLY 2 plates per image
        
            rez = curPlate.calc(self.allexpdata)
            #dictionary.update({ os.path.basename(usedpaths[status % 2]) + (" (%i)" % ((status+1) % 2)) : {'Value' : str(rez) } })
            dictionary.update({ os.path.basename(self.usedpaths[status // 2]) + (" (%i)" % ((status % 2) + 1)) : {'Value' : str(rez) } })
            
            status+=1
            self.signal_update_pbar.emit(status*100/len(self.listPlateImages))
        
        print "Done."
        print "Generating previews..."
        
        #-------------------------
        # TODO FIXME fix this, for now showing plate images instead of previews (for testing purposes)
        
        #self.genPreviews() 
        
        for plate in self.listPlateImages:
            plate.preview = plate.image
        #-------------------------
        
        ctr = 0
        for plate in self.listPlateImages:
            rezpath = os.path.splitext(self.usedpaths[ctr // 2])[0] + '_calcrezpreview_' + str((ctr % 2) + 1) + os.path.splitext(self.usedpaths[ctr // 2])[1]
            if plate.preview != None:
                imsave(rezpath, plate.preview)
            ctr += 1
        
        print "Done."
        
        print "DEBUG Colony intensity array:"
        print self.allexpdata
        
        #dictionary={'result':{'Value':str(status)}}
        self.signal_update_table.emit(dictionary)
        self.finished.emit()
        
def main():
    
    app = QtGui.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('icon.png'))
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()    
