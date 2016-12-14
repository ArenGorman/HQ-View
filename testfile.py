import xmlrpclib, time

from datetime import datetime
server_adress = "http://proxy:algous@92.63.64.132:5002"
    #server_adress = "http://fx25:5002/"
try:
    hq_server = xmlrpclib.ServerProxy(server_adress)
    print "Server is reachable: "+str(hq_server.ping())
except:
    print "Unable to connect to HQueue server." #TODO: add GUI implementation

# id_=hq_server.getFinishedRootJobIds()
# a = hq_server.getJobs(id_)
# print a

def getFinishedJobs():
    print "getting Finished jobs"
    fin_jobs_ids = hq_server.getFinishedRootJobIds()
    fin_jobs = hq_server.getJobs(fin_jobs_ids)
    array = []
    for i,item in enumerate(fin_jobs):
        array.append([])
        array[i].append(item.items()[18][1]) #ID 0
        array[i].append(item.items()[19][1]) #Name 1
        array[i].append(item.items()[17][1]) #Status 2
        array[i].append(item.items()[7][1]) #Children IDs 3
        array[i].append(item.items()[13][1]) #StartTime 4
        print item['name']
        #TODO: find API function that returns "submitted by" 5
    return array #returns only necessary list of values

a=hq_server.getClientsByHostname(['node158'])[0]['lastHeartbeat']
print datetime.strptime(a.value,"%Y%m%dT%H:%M:%S")
print dir(a)

