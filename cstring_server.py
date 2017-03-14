#!/usr/bin/python
'''

First, you should set the surrogates's IPs on the S array. 
After you can start the servers.
By default the servers will listen on the port 2222.


'''

from socket import *
import os
import numpy as np
from cStringIO import StringIO
from timeit import default_timer as timer

mA = ""
mB = ""

tcp = socket(AF_INET,SOCK_STREAM)
tcp.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
tcp.bind(('',2222))
tcp.listen(1)
conn, addr = tcp.accept()

ultimate_buffer=''
while True:
    receiving_buffer = conn.recv(2000)

    if not receiving_buffer: break
    ultimate_buffer+= receiving_buffer

mA = np.load(StringIO(str(ultimate_buffer).split('||||||')[0]))['frame']
mB = np.load(StringIO(str(ultimate_buffer).split('||||||')[1]))['frame']

start = timer()
tosend = np.dot(mA,mB)
end = timer()
print "Time to process> %.3f" % (end-start)

start = timer()
f = StringIO()
np.savez_compressed(f,frame=tosend)
f.seek(0)
out = f.read()
end = timer()
print "Time to serialize> %.3f" % (end-start)

start = timer()
conn.sendall(out)
conn.shutdown(1)
conn.close()
end = timer()
print "Time to send> %.3f" % (end-start)
