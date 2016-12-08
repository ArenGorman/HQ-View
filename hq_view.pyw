#!/bin/python
#TODO: use multithreading/multiprocessing for getting jobs

import xmlrpclib
import sys
import operator
import time
from datetime import datetime
from PyQt4 import QtCore, QtGui
from multiprocessing import cpu_count

class worker(QtCore.QThread):
    # testsignal = QtCore.pyqtSignal(object, 'bool')
    def __init__(self, models, children=False, view=None):
        super(self.__class__,self).__init__()
        self.models = models
        self.children = children
        self.view = view

    def __del__(self):
        self.wait()

    def buttonDisabler(self,chk):
        if chk:
            upd_button.setEnabled(True)
            upd_button.setText('Update')
            sb.showMessage("Lists updated")
        else:
            upd_button.setEnabled(False)
            upd_button.setText('Updating')
            sb.showMessage("Updating lists")

    def run(self):
        srv = xmlrpclib.ServerProxy(server_adress)
        if not self.children:
            for i in self.models:
                try:
                    i.update_models()
                except Exception:
                    print "Failed to update"
        else:            
            ix = self.view.selectedIndexes()[0].row()
            parentId = self.models[0].arraydata[ix][0] #Gets Parent's ID
            array = modelChildren.getChildren(parentId)


class jobsTable(QtCore.QAbstractTableModel):
    """
    This class contains two type methods - overrided native PyQt methods and original ones.

    Original methods:
    getFinishedJobs()::list()

    """
    def __init__(self, finished, server=None, children=False, parent=None):
        super(self.__class__,self).__init__()
        # QtCore.QAbstractTableModel.__init__(self, parent)
        self.server = xmlrpclib.ServerProxy(server_adress)
        self.finished = finished
        self.cols = 0
        self.rows = 0
        # self.update_models()
        #Headers
        if children:
            self.headerdata = ['Id','Name','Priority','Status','Progress','Submitted By','Start time','Elapsed time','Completion time', 'Clients']
        elif finished:
            self.headerdata = ['Id','Name','Status','Time submitted','Submitted by','Completion time']
        else:
            self.headerdata = ['Id','Name','Priority','Status','Progress','Time submitted','Submitted by','Elapsed time','ETA']
            

    def getJobs(self):
        #This function returns class' property "arraydata" to represent data for the table
        if self.finished:
            self.arraydata = self.getFinishedJobs()
        else:
            self.arraydata = self.getRunningJobs()
        return self.arraydata

    def getFinishedJobs(self):
        if self.finished==False:
            return
        if log: print "getting Finished jobs"
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
            if item['startTime'] and item['endTime']: #check if both timestamps exist
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
        if log: print "getting Uninished jobs"
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
            if item['startTime'] and self.server.getServerTime(): #checks if both timestamps exist
                array[i].append(self.spentTime(item['startTime'],self.server.getServerTime())) #Elapsed time 6
            else:
                array[i].append(None)
            if item['ETA']: #ETA 7
                array[i].append(str(round(float(item['ETA']/60),2)) + " min")
            if log: print "Id:"+str(array[i][1])+" Name:"+str(array[i][0])
        if array!=[]:
            self.cols = len(array[0])
            self.rows = len(array)
        return array #returns only necessary list of lists of values

    def getChildren(self,parentId):
        children_ids = self.server.getJob(parentId)['children']
        children_jobs = self.server.getJobs(children_ids)

        array = []
        for i,item in enumerate(children_jobs):
            array.append([])
            array[i].append(item['id'])
            array[i].append(item['name'])
            array[i].append(item['priority'])
            array[i].append(item['status'])
            array[i].append(round(item['progress']*100))
            array[i].append("Submitted By")
            if item['startTime']:
                array[i].append(item['startTime'])
            else:
                array[i].append(None)
            if item['startTime'] and self.server.getServerTime(): #checks if both timestamps exist
                array[i].append(self.spentTime(item['startTime'],self.server.getServerTime())) #Elapsed time
            else:
                array[i].append(None)
            if item['startTime'] and item['endTime']: #check if both timestamps exist
                array[i].append(self.spentTime(item['startTime'],item['endTime'])) #Completion time
            else:
                array[i].append(None)
            if item['clients']:
                array[i].append(item['clients'][0]['hostname'])
            else:
                array[i].append(None)
        if array!=[]:
            self.cols = len(array[0])
            self.rows = len(array)
            # print array
        self.arraydata = array
        return array

    def update_models(self):
        # Emitting signals is crucial!
        self.layoutAboutToBeChanged.emit()
        self.arraydata = self.getJobs()
        self.layoutChanged.emit()

    def spentTime(self,in_time,out_time, string=True): 
        # Computes spent time by subtraction of startTime from endTime or ServerTime
        if string:
            return str(datetime.strptime(str(out_time), "%Y%m%dT%H:%M:%S")-datetime.strptime(str(in_time), "%Y%m%dT%H:%M:%S"))
        else:
            return datetime.strptime(str(out_time), "%Y%m%dT%H:%M:%S")-datetime.strptime(str(in_time), "%Y%m%dT%H:%M:%S")
    
    def format(self,index,role):
        if not index.isValid():
            return QtCore.QVariant()
        elif role == QtCore.Qt.BackgroundRole:
            if self.arraydata[index.row()][index.column()]=='succeeded':
                return QtGui.QBrush(QtCore.Qt.darkGreen)
            elif self.arraydata[index.row()][index.column()]=='cancelled':
                return QtGui.QBrush(QtCore.Qt.black)
            elif self.arraydata[index.row()][index.column()]=='queued':
                return QtGui.QBrush(QtCore.Qt.darkCyan)
            elif self.arraydata[index.row()][index.column()]=='failed':
                return QtGui.QBrush(QtCore.Qt.red)
        if role==QtCore.Qt.ForegroundRole:
            if self.arraydata[index.row()][index.column()]=='cancelled':
                    return QtGui.QBrush(QtCore.Qt.white)
        elif role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()

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

    def sort(self, Ncol, order):
        """Sort table by given column number.
        """
        self.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))
        self.arraydata = sorted(self.arraydata, key=operator.itemgetter(Ncol))
        if order == QtCore.Qt.DescendingOrder:
            self.arraydata.reverse()
        self.emit(QtCore.SIGNAL("layoutChanged()"))

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if self.format(index,role):
            return self.format(index,role)
        return QtCore.QVariant(self.arraydata[index.row()][index.column()])

def center_window(obj):
    qr = obj.frameGeometry()
    cp = QtGui.QDesktopWidget().availableGeometry().center()
    qr.moveCenter(cp)
    obj.move(qr.topLeft())

def upd(model1,model2):
    thread_upd = worker([model1,model2])
    thread_upd.finished.connect(lambda: thread_upd.buttonDisabler(True))
    thread_upd.finished.connect(lambda: resizeTableSlot())
    thread_upd.started.connect(lambda: thread_upd.buttonDisabler(False))
    thread_upd.start()

def resizeTableSlot():
    table_fin.resizeColumnsToContents()
    table_fin.resizeRowsToContents()
    table_fin.setSortingEnabled(True)
    table_run.resizeColumnsToContents()
    table_run.resizeRowsToContents()
    table_run.setSortingEnabled(True)

def clickedCell(fin=True):
    if fin:
        thread_children = worker([modelFin],children=True, view=table_fin)
    else:
        thread_children = worker([modelRun],children=True, view=table_run)
    thread_children.started.connect(lambda: sb.showMessage('Aquring child jobs'))
    thread_children.finished.connect(lambda: thread_children.buttonDisabler(True))
    thread_children.finished.connect(lambda: show_children())
    thread_children.start()

def show_children():
    tabs_widget.addTab(tab_children,'Children')
    table_children.setModel(modelChildren)
    layout_children.addWidget(table_children)
    tab_children.setLayout(layout_children)
    table_children.resizeColumnsToContents()
    table_children.resizeRowsToContents()
    table_children.setSortingEnabled(True)
    sb.showMessage('Child jobs aquired')


if __name__ == '__main__':
    # num_cores = cpu_count()
    log = False #Enables writing jobs' names in the log
    #Connect to the server, aborting function if it's not availible
    server_adress = "http://proxy:algous@92.63.64.132:5002"
    #server_adress = "http://fx25:5002/"
    try:
        hq_server = xmlrpclib.ServerProxy(server_adress)
        print "Server is reachable: " + str(hq_server.ping())
    except:
        print "Unable to connect to HQueue server." #TODO: add GUI implementation
        sys.exit()
    
    #Run app and GUI
    app = QtGui.QApplication(sys.argv)
    mainWindow = QtGui.QWidget(parent=None)
    mainWindow.setWindowTitle('HQueue Python')
    mainWindow.setWindowIcon(QtGui.QIcon("/studio/tools/icons/hou.png"))
    mainWindow.setGeometry(0,0,1400,1200)
    center_window(mainWindow)

    #Tabs
    tabs_widget = QtGui.QTabWidget(mainWindow)
    tab_main_jobs = QtGui.QWidget()
    tab_children = QtGui.QWidget()
    tabs_widget.addTab(tab_main_jobs,'Jobs')

    #Tableviews
    table_run = QtGui.QTableView()
    table_fin = QtGui.QTableView()
    table_children = QtGui.QTableView()

    table_run.doubleClicked.connect(lambda: clickedCell(False))
    table_fin.doubleClicked.connect(lambda: clickedCell(True))
    

    #Creating entities: Running and Finished
    modelFin = jobsTable(True)
    modelRun = jobsTable(False)
    modelChildren = jobsTable(False,children=True)

    #Linking entities to tableviews
    table_fin.setModel(modelFin)
    table_run.setModel(modelRun)

    upd_button = QtGui.QPushButton('Get Jobs', tab_main_jobs)
    upd_button.clicked.connect(lambda: upd(modelRun,modelFin))
    upd_button.setMaximumWidth(500)

    sb = QtGui.QStatusBar(mainWindow)
    sb.setStyleSheet('.QStatusBar { background-color: rgb(220, 220, 255); border:1px solid rgb(170, 170, 170); }')

    sb.showMessage("Ready")

    # Setting up the layout
    
    layout_main = QtGui.QVBoxLayout(mainWindow)
    layout_jobs_tab = QtGui.QVBoxLayout()
    layout_children = QtGui.QVBoxLayout()

    layout_main.addWidget(tabs_widget)
    layout_jobs_tab.addWidget(upd_button)
    layout_jobs_tab.addWidget(QtGui.QLabel("<center><h3>Unfinished jobs</h3></center>"))
    layout_jobs_tab.addWidget(table_run)
    layout_jobs_tab.addWidget(QtGui.QLabel("<center><h3>Finished jobs</h3></center>"))
    layout_jobs_tab.addWidget(table_fin)

    
    #Quit btn
    quit_btn = QtGui.QPushButton('Quit', mainWindow)
    quit_btn.clicked.connect(app.quit)
    quit_btn.setMaximumWidth(500)
    layout_main.addWidget(quit_btn)

    layout_main.addWidget(sb)
    tab_main_jobs.setLayout(layout_jobs_tab)
    mainWindow.setLayout(layout_main)
    # QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('cleanlooks'))
    mainWindow.show()

    # Getting the jobs after UI loaded
    upd(modelFin,modelRun)

    #====================FOR TEST PURPOSES=====================

    #==========================================================
    sys.exit(app.exec_())

