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

from PyQt4 import QtGui,QtCore
import sys, csv
class TableWidget(QtGui.QTableWidget):
    def __init__(self,parent=None):
        super(TableWidget, self).__init__(parent)
# if you want to use parent's methods and be ugly as I do, use parent =)
        self.parent=parent
        self.clip = QtGui.QApplication.clipboard()
        self.horizontalHeader().setMovable(True)
        self.verticalHeader().setMovable(True)
        self.horizontalHeader().setDefaultSectionSize(60)
        self.setMinimumWidth(250)
        self.setMinimumHeight(250)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
       

        self.rowOrder=[]
        self.columnOrder=[]
        self.verticalHeader().sectionMoved.connect( self.getOrders)
        self.horizontalHeader().sectionMoved.connect( self.getOrders)


    def buildFromDict(self,inDict,rowOrder=[],columnOrder=[]):
        self.setRowCount(0)
        self.setColumnCount(0)
        # finding all rows and cols in dict
        newRow = []
        newCol = []
        for row in inDict:
            if not(row in newRow):
                newRow.append(row)
            for col in inDict[row]:
                if not(col in newCol):
                    newCol.append(col)        
        
        # adding new rows and cols in dict
        sortNewRow=[]
        sortNewCol=[]
        for row in inDict:
            if not(row in rowOrder):
                sortNewRow.append(row)
            for col in inDict[row]:
                if not(col in columnOrder):
                    sortNewCol.append(col)
        sortNewRow.sort()
        sortNewCol.sort()
        [rowOrder.append(row) for row in sortNewRow]
        [columnOrder.append(col) for col in sortNewCol]
                    
        # creating ordered list of not empty values            
        visibleRows = []
        visibleCols = []
        for row in rowOrder:
            if row in newRow:
                visibleRows.append(row)
                
        for col in columnOrder:
            if col in newCol:
                visibleCols.append(col)
        #drawin table and asigning row and column names
        rows=[]
        columns=[]
        for row in visibleRows:
            #if row in inDict:
            rows.append(row)
            self.insertRow(self.rowCount())
            self.setVerticalHeaderItem(self.rowCount()-1, QtGui.QTableWidgetItem(row))
            for col in visibleCols:
                #if (col in inDict[row]):
                if (not(col in columns)):
                    columns.append(col)
                    self.insertColumn(self.columnCount())
                    self.setHorizontalHeaderItem(self.columnCount()-1,QtGui.QTableWidgetItem(col))
        #asidning values
        for row in rows:
            for col in columns:
                try:
                    item=QtGui.QTableWidgetItem(str(inDict[row][col]))
                    item.setFlags(QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled)
                    self.setItem(rows.index(row),columns.index(col),item)
                except:
                    pass       
                      
        self.verticalHeader().setDefaultSectionSize(self.verticalHeader().minimumSectionSize())
        self.rowOrder = rowOrder #rows
        self.columnOrder = columnOrder #columns



    def getOrders(self,event=None):
        #try:
        rowNames = [str(self.verticalHeaderItem(i).text()) for i in range(self.rowCount())]
        rowIndx = [self.visualRow(i) for i in range(self.rowCount())]
        rowOrder = [x for (y,x) in sorted(zip(rowIndx,rowNames))]
        for row in self.rowOrder:
            if not(row in rowOrder):
                rowOrder.append(row)
        self.rowOrder = rowOrder
        
        
        colNames = [str(self.horizontalHeaderItem(i).text()) for i in range(self.columnCount())]
        colIndx = [self.visualColumn(i) for i in range(self.columnCount())]
        columnOrder = [x for (y,x) in sorted(zip(colIndx,colNames))]
        for col in self.columnOrder:
            if not(col in columnOrder):
                columnOrder.append(col)
        self.columnOrder = columnOrder

        
    def keyPressEvent(self, e):
        if (e.modifiers() & QtCore.Qt.ControlModifier):        
            if e.key() == QtCore.Qt.Key_C:
                self.copySelectionToClipboard()
        
    def contextMenuEvent(self, pos):
        menu = QtGui.QMenu()
        copyAction = menu.addAction("Copy")
        action = menu.exec_(QtGui.QCursor.pos())
        if action == copyAction:
            self.copySelectionToClipboard()
    
    def handleSave(self,path):
        rowLog = range(self.rowCount())
        rowIndx = [self.visualRow(i) for i in rowLog]
        rowVis = [x for (y,x) in sorted(zip(rowIndx,rowLog))]
        
        colLog = range(self.columnCount())
        colIndx = [self.visualColumn(i) for i in colLog]
        colVis = [x for (y,x) in sorted(zip(colIndx,colLog))]
        
    
        with open(unicode(path), 'wb') as stream:
            writer = csv.writer(stream)
            rowdata = []
            rowdata.append("")
            for column in colVis:
                rowdata.append(unicode(self.horizontalHeaderItem(column).text()).encode('utf8'))
            writer.writerow(rowdata) 
            for row in rowVis:
               
                rowdata = []
                rowdata.append(unicode(self.verticalHeaderItem(row).text()).encode('utf8'))
                for column in colVis:
                    
                    item = self.item(row, column)
                    if item is not None:
                        rowdata.append(
                            unicode(item.text()).encode('utf8'))
                    else:
                        rowdata.append('')
                writer.writerow(rowdata)    
    
    def copySelectionToClipboard(self):
        selected = self.selectedRanges()
        s = ""
        for r in xrange(selected[0].topRow(),selected[0].bottomRow()+1):
            for c in xrange(selected[0].leftColumn(),selected[0].rightColumn()+1):
                try:
                    s += str(self.item(r,c).text()) + "\t"
                except AttributeError:
                    s += "\t"
            s = s[:-1] + "\n" #eliminate last '\t'
            self.clip.setText(s)
            
def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = TableWidget()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()    
