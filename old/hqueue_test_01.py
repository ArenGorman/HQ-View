#!/bin/python

#TODO: use multithreading/multiprocessing for getting jobs

import xmlrpclib
import sys
from PyQt4 import QtCore
from PyQt4 import QtGui
from multiprocessing.dummy import Pool as tpool
from multiprocessing import cpu_count



class jobsTable(QtCore.QAbstractTableModel):
    def __init__(self, server, finished=True, parent=None):
        super(jobsTable,self).__init__()
        self.server = server
        self.initUI()

    def initUI(self):
        pass

    def appendList(list,item):
        list.append(item)

    def getFinishedJobs(self):
        fin_jobs_ids = []
        fin_jobs = []
        for i,item in enumerate(self.server.getFinishedRootJobIds()):
            fin_jobs_ids.append(item)
            fin_jobs.append(self.server.getJob(fin_jobs_ids[i]))
        return fin_jobs
            
    def getRunningJobs(self):
        run_jobs_ids = []
        run_jobs = []
        for i,item in enumerate(self.server.getRunningJobIds()):
            run_jobs_ids.append(item)
            run_jobs.append(self.server.getJob(run_jobs_ids[i]))
        return run_jobs

def main():
    #Connect to the server, aborting function if it's not availible
    try:
        hq_server = xmlrpclib.ServerProxy("http://proxy:algous@92.63.64.132:5002")
        print hq_server.ping()
    except:
        print "Unable to connect to HQueue server." #TODO: add GUI implementation
        return
    #Run GUI
    app = QtGui.QApplication(sys.argv)
    tableFin = jobsTable(hq_server,False)
    print tableFin.getFinishedJobs()[0]

    #get finished job ids
    # print hq_server.getAllJobStatusNames()
    # print hq_server.getJobIdsByStatus(['succeeded', 'failed', 'abandoned', 'cancelled', 'ejected'])

if __name__ == '__main__':
    num_cores = cpu_count()
    main()    
