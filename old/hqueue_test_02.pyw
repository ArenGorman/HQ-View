#!/bin/python
#TODO: use multithreading/multiprocessing for getting jobs

import xmlrpclib
import sys
from datetime import datetime
from PyQt4 import QtCore, QtGui
from multiprocessing import cpu_count

class jobsTable(QtCore.QAbstractTableModel):
    def __init__(self, server, finished=True, parent=None):
        #super(jobsTable,self).__init__()
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.server = server
        self.cols = 0
        self.rows = 0

    def getFinishedJobs(self):
        fin_jobs_ids = []
        fin_jobs = []
        array = []
        for i,item in enumerate(self.server.getFinishedRootJobIds()):
            array.append([])
            fin_jobs_ids.append(item)
            fin_jobs.append(self.server.getJob(fin_jobs_ids[i]))
            array[i].append(fin_jobs[i].items()[18][1]) #ID 0
            array[i].append(fin_jobs[i].items()[19][1]) #Name 1
            array[i].append(fin_jobs[i].items()[17][1]) #Status 2
            array[i].append(str(fin_jobs[i].items()[12][1])) #Time submitted, str format 3 
            array[i].append(str(fin_jobs[i].items()[0][1]))# Submitted by 4
            #TODO: find API function that returns "submitted by" 5
            array[i].append( #Completion time 6(5)
                self.spentTime(
                fin_jobs[i].items()[13][1],
                fin_jobs[i].items()[16][1])
            )
        if array!=[]:
            self.cols = len(array[0])
            self.rows = len(array)
        return array #returns only necessary list of values
        #return fin_jobs #returns the whole dictionary
            
    def getRunningJobs(self):
        run_jobs_ids = []
        run_jobs = []
        array = []
        for i,item in enumerate(self.server.getUnfinishedRootJobIds()):
            array.append([])
            run_jobs_ids.append(item)
            run_jobs.append(self.server.getJob(run_jobs_ids[i]))
            array[i].append(run_jobs[i].items()[19][1]) #ID 0
            array[i].append(run_jobs[i].items()[18][1]) #Name 1
            array[i].append(run_jobs[i].items()[1][1]) #Priority 2
            array[i].append(run_jobs[i].items()[0][1]) #Status 3
            array[i].append(run_jobs[i].items()[15][1]*100) #Progress 4
            array[i].append(str(run_jobs[i].items()[12][1])) #Submission time 5
            #array[i].append(run_jobs[i].items()[19][1]) #Submitted by 6
            array[i].append("SUBMITTED BY")
            array[i].append(
                            self.spentTime(
                            run_jobs[i].items()[13][1],
                            self.server.getServerTime(),
                            )
                ) #Elapsed time 7
        if array!=[]:
            self.cols = len(array[0])
            self.rows = len(array)
        return array #returns only necessary list of values
        #return run_jobs #returns the whole dictionary

    def spentTime(self,in_time,out_time, string=True): 
        #This function computes spent time by subtraction of startTime from endTime or ServerTime
        if string:
            return str(datetime.strptime(str(out_time), "%Y%m%dT%H:%M:%S")-datetime.strptime(str(in_time), "%Y%m%dT%H:%M:%S"))
        else:
            return datetime.strptime(str(out_time), "%Y%m%dT%H:%M:%S")-datetime.strptime(str(in_time), "%Y%m%dT%H:%M:%S")

    def rowCount(self, parent):
        return self.rows

    def columnCount(self, parent):
        return self.cols

    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        elif role != Qt.DisplayRole:
            return QVariant()
        return QVariant(self.arraydata[index.row()][index.column()])

def main():
    #Connect to the server, aborting function if it's not availible
    server_adress = "http://proxy:algous@92.63.64.132:5002"
    #server_adress = "http://fx25:5002/"
    try:
        hq_server = xmlrpclib.ServerProxy(server_adress)
        print "Server is reachable: "+str(hq_server.ping())
    except:
        print "Unable to connect to HQueue server." #TODO: add GUI implementation
        return
    #Run app and GUI
    app = QtGui.QApplication(sys.argv)
    mainWindow = QtGui.QWidget(parent=None)
    mainWindow.__init__()
    mainWindow.setWindowTitle('HQueue Python Graphic Interface')
    mainWindow.setWindowIcon(QtGui.QIcon("/studio/tools/icons/hou.png"))

    #Tableviews
    table_unfin=QtGui.QTableView()
    table_fin=QtGui.QTableView()

    #Creating instances: Running and Finished
    modelFin = jobsTable(hq_server, False, mainWindow)
    modelRun = jobsTable(hq_server, True, mainWindow)

    table_fin.setModel(modelFin)
    table_unfin.setModel(modelRun)

    layout = QtGui.QVBoxLayout(mainWindow)
    layout.addWidget(table_fin)
    layout.addWidget(table_unfin)
    mainWindow.show()

    #==========================================================
    #==========================TEST============================
    #==========================================================

    aa = modelFin.getRunningJobs()
    print aa[0]

if __name__ == '__main__':
    num_cores = cpu_count()
    main()
