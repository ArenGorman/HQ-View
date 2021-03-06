#!/bin/python
#TODO: use multithreading/multiprocessing for getting jobs

import xmlrpclib
import sys
from datetime import datetime
from PyQt4 import QtCore, QtGui
from multiprocessing import cpu_count
#import sip

class jobsTable(QtCore.QAbstractTableModel):
    def __init__(self, server, finished, parent=None):
        #super(jobsTable,self).__init__()
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.server = server
        self.finished = finished
        self.cols = 0
        self.rows = 0
        self.children = []
        self.arraydata = self.getJobs()
        #Headers
        if finished:
            self.headerdata = ['Id','Name','Status','Time submitted','Submitted by','Completion time']
        else:
            self.headerdata = ['Id','Name','Priority','Status','Progress','Time submitted','Submitted by','Elapsed time','ETA']

    def refresh(self):
        self.arraydata = self.getJobs()

    def getJobs(self):
        #This function sets class' property "arraydata" to represent data for the table
        if self.finished:
            self.arraydata = self.getFinishedJobs()

        else:
            self.arraydata = self.getRunningJobs()
        return self.arraydata

    def getFinishedJobs(self):
        if self.finished==False:
            return
        print "getting Finished jobs"
        fin_jobs_ids = self.server.getFinishedRootJobIds()
        fin_jobs = self.server.getJobs(fin_jobs_ids)
        array = []
        for i,item in enumerate(fin_jobs):
            array.append([])
            array[i].append(item['id']) #ID 0
            array[i].append(item['name']) #Name 1
            array[i].append(item['status']) #Status 2
            array[i].append(item['queueTime'].value) #Time submitted, str format 3 
            array[i].append("Submitted By") # Submitted by 4
            #TODO: find API function that returns "submitted by" 5
            if type(item['startTime'])!=type(None) and type(item['endTime'])!=type(None): #check if both timestamps exist
                array[i].append(self.spentTime(item['startTime'],item['endTime'])) #Completion time 6(5)
            else:
                array[i].append(None)
            if log: print "Id:"+str(array[i][0])+" Name:"+str(array[i][1])
        if array!=[]:
            self.cols = len(array[0])
            self.rows = len(array)
        return array #returns only necessary list of values
        #return fin_jobs #returns the whole dictionary
            
    def getRunningJobs(self):
        if self.finished==True:
            return
        print "getting Uninished jobs"
        run_jobs_ids = self.server.getUnfinishedRootJobIds()
        run_jobs = self.server.getJobs(run_jobs_ids)
        array = []
        for i,item in enumerate(run_jobs):
            array.append([])
            array[i].append(item['id']) #ID 0
            array[i].append(item['name']) #Name 1
            array[i].append(item['priority']) #Priority 2
            array[i].append(item['status']) #Status 3
            array[i].append(round(item['progress']*100)) #Progress 4
            array[i].append(item['queueTime'].value) #Submission time 5
            array[i].append("Submitted By")
            if type(item['startTime'])!=type(None) and type(self.server.getServerTime())!=type(None): #checks if both timestamps exist
                array[i].append(self.spentTime(item['startTime'],self.server.getServerTime())) #Elapsed time 7
            else:
                array[i].append(None)
            if type(item['ETA'])!=type(None): #ETA
                array[i].append(str(round(float(item['ETA']/60),2)) + " min")
            if log: print "Id:"+str(array[i][1])+" Name:"+str(array[i][0])
        if array!=[]:
            self.cols = len(array[0])
            self.rows = len(array)
        return array #returns only necessary list of values
        #return run_jobs #returns the whole dictionary

    def getChildren(self,parentId):
        children_ids = self.server.getJob(parentId)['children']
        children_jobs = self.server.getJobs(children_ids)
        array = []
        for i,item in enumerate(children_jobs):
            array.append([])
            array[i].append(item['id'])
            array[i].append(item['name'])
            array[i].append(item['id'])

    def spentTime(self,in_time,out_time, string=True): 
        #This function computes spent time by subtraction of startTime from endTime or ServerTime
        if string:
            return str(datetime.strptime(str(out_time), "%Y%m%dT%H:%M:%S")-datetime.strptime(str(in_time), "%Y%m%dT%H:%M:%S"))
        else:
            return datetime.strptime(str(out_time), "%Y%m%dT%H:%M:%S")-datetime.strptime(str(in_time), "%Y%m%dT%H:%M:%S")


    #Qt sevice functions
    def rowCount(self, parent):
        return self.rows

    def columnCount(self, parent):
        return self.cols

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self.headerdata[col])
        if orientation == QtCore.Qt.Vertical and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(col+1)
        return QtCore.QVariant()   

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return QtCore.QVariant()
        elif role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()
        return QtCore.QVariant(self.arraydata[index.row()][index.column()])

def center_window(obj):
    qr = obj.frameGeometry()
    cp = QtGui.QDesktopWidget().availableGeometry().center()
    qr.moveCenter(cp)
    obj.move(qr.topLeft())

def childrenWindow(parentId):
    childWindow = QtGui.QDialog(parent=None)
    childWindow.__init__()
    childWindow.setGeometry(0,0,1400,1200)
    
    childWindow.setWindowTitle("Children")
    childWindow.show()
    center_window(childWindow)
    print "Child window"
    return childWindow

def main():
    #Connect to the server, aborting function if it's not availible
    server_adress = "http://proxy:algous@92.63.64.132:5002"
    #server_adress = "http://fx25:5002/"
    try:
        hq_server = xmlrpclib.ServerProxy(server_adress)
        print "Server is reachable: " + str(hq_server.ping())
    except:
        print "Unable to connect to HQueue server." #TODO: add GUI implementation
        return
    #Run app and GUI
    app = QtGui.QApplication(sys.argv)
    mainWindow = QtGui.QWidget(parent=None)
    mainWindow.__init__()
    mainWindow.setWindowTitle('HQueue Python')
    mainWindow.setWindowIcon(QtGui.QIcon("/studio/tools/icons/hou.png"))
    mainWindow.setGeometry(0,0,1400,1200)
    center_window(mainWindow)



    #Tableviews
    table_unfin=QtGui.QTableView()
    table_fin=QtGui.QTableView()

    #Creating instances: Running and Finished
    modelFin = jobsTable(hq_server, True, mainWindow)
    modelRun = jobsTable(hq_server, False, mainWindow)

    #Linking instances to tableviews
    table_fin.setModel(modelFin)
    table_unfin.setModel(modelRun)
    table_fin.setMinimumSize(900, 500)
    table_fin.resizeColumnsToContents()
    table_fin.resizeRowsToContents()
    table_unfin.resizeColumnsToContents()
    table_unfin.resizeRowsToContents()

    layout = QtGui.QVBoxLayout(mainWindow)
    layout.addWidget(QtGui.QLabel("Finished jobs"))
    layout.addWidget(table_fin)
    layout.addWidget(QtGui.QLabel("Unfinished jobs"))
    layout.addWidget(table_unfin)
    
    #Quit btn
    quit_btn = QtGui.QPushButton('Quit', mainWindow)
    quit_btn.clicked.connect(app.quit)
    layout.addWidget(quit_btn)

    mainWindow.setLayout(layout)
    mainWindow.show()
    childrenWindow(19569)
    
    #==========================================================
    #====================FOR TEST PURPOSES=====================



    #==========================================================
    #DONT DELETE THIS:
    sys.exit(app.exec_())

if __name__ == '__main__':
    num_cores = cpu_count()
    log = False #Enables reading jobs log
    main()
