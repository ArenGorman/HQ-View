import xmlrpclib, time,sys

from datetime import datetime
server_adress = "http://proxy:algous@92.63.64.132:5002"
    #server_adress = "http://fx25:5002/"
try:
    hq_server = xmlrpclib.ServerProxy(server_adress)
    print "Server is reachable: "+str(hq_server.ping())
except:
    print "Unable to connect to HQueue server." #TODO: add GUI implementation
    sys.exit()

def getFinishedJobs():
    a = hq_server.getClientsByHostname(['node158'])
    a = a[0]
    label1 = "Hostname: \t{0}\nStatus: \t{1}\nHeartbeat: \t%s\nPort is: \t%s\nLoad is: \t%s"
    label2 = "Ip"
    return label1

a = hq_server.getClientsByHostname(['node158'])
a = a[0]

j=getFinishedJobs().format(a['hostname'],a['available'])
print j