#
# This is the main file for the lil plotter
#

import sys
import json
import struct
from threading import Thread

import numpy as np

from jsonconsts import *
from lildock import *
from utils import *
from serialconsts import *
from pyqtgraph.dockarea import *

from pyqtgraph.Qt import QtCore, QtGui

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')


if len(sys.argv) < 2:
	print("Expecting the config file name.")
	print("Usage: %s <config_file_name>"%sys.argv[0])
	sys.exit(-1)

cfgfile = sys.argv[1]

jsonobj = None

with open(cfgfile) as jsonstring:
	jsonobj = json.load(jsonstring)

uiconfigobj 	= jsonobj[JKEY_UICONFIG]
datmapobj	= jsonobj[JKEY_DATAMAP]

plotobjs	= uiconfigobj[JKEY_PLOTS]
tableobjs	= uiconfigobj[JKEY_TABLES]
configobjs	= uiconfigobj[JKEY_CONFIG]

decodestrhead 	= "<III"
decodestrtail 	= "I"
decodestr	= decodestrhead

stopWorker = False

print ("Found %d plots"%len(plotobjs))
print ("Found %d Tables"%len(tableobjs))

app = QtGui.QApplication([])
win = QtGui.QMainWindow()
area = DockArea()
win.setCentralWidget(area)
win.resize(1000,500)
win.setWindowTitle('pyqtgraph example: dockarea')

#Lets get the number of plots required.
dockdict = {}
signallist = []
plotidlist = []
tabidlist = []

for plotobj in plotobjs:
	dock = lildock(plotobj[JKEY_PLOTTITLE], size=(1,1), mode="PLOT")	
	area.addDock(dock, 'left')
	dockdict.update({plotobj[JKEY_PLOTID]:{'dock': dock, 'jsonobj': plotobj.copy()}})
	plotidlist.append(plotobj[JKEY_PLOTID])
	
for tableobj in tableobjs:
	dock = lildock(tableobj[JKEY_TABTITLE], size=(1,1), mode="TABLE")	
	area.addDock(dock, 'left')
	dockdict.update({tableobj[JKEY_PLOTID]:{'dock': dock, 'jsonobj': tableobj.copy()}})
	tabidlist.append(tableobj[JKEY_TABID])

#Now lets get to the data part 
for datmemb in datmapobj:
	print("Signal : %s"%datmemb[JKEY_SIGNALID])
	start, end = [int(x) for x in datmemb[JKEY_BYTES].split(':')]
	assert(end >= start)
	nbytes = (end-start)+1
	print("Bytes = %d"%nbytes);
	if datmemb[JKEY_READAS] not in datatypeslist:
		raise Exception("Invalid Data Type. Supported types" + str(datatypeslist))

	if datmemb[JKEY_READAS] != 'string':
		if datmemb[JKEY_READAS] not in dtypes4bytes[str(nbytes)]:
			raise Exception("For " + str(nbytes) +" bytes expected data types are " + str(dtypes4bytes[str(nbytes)]))	
		decodestr += unpackchar[datmemb[JKEY_READAS]]
	else:
		decodestr += str(nbytes)+unpackchar['string']
	
	signallist.append({'showlist': [], 'jsonobj':datmemb.copy()})
	
	showonlist = datmemb[JKEY_SHOWON]	

	print dockdict
	
	for showon in showonlist:
		if showon not in plotidlist and showon not in tabidlist:
			raise Exception("THe showOn item ID is not defined. Available options are " + str(idlist) + " Got " + str(showon))

		dockobj = dockdict[showon]['dock']
		if showon in plotidlist:
			inst = dockobj.addPlot([], name=datmemb[JKEY_SIGNALNAME])
			showtype = 'PLOT'
		if showon in tabidlist:
			inst = dockobj.addTable([], name=datmemb[JKEY_SIGNALNAME])
			showtype = 'TABLE'
		
		signallist[-1]['showlist'].append({'obj':dockdict[showon]['dock'], 'inst':inst, 'showtype' : showtype})
		print("Added " + datmemb[JKEY_SIGNALID] + " on " + str(dockobj) + " with Inst ID " + str(inst));
			
def updateData():
	global signallist
	for signal in signallist:
		for showitem in signal['showlist']:
			showitem['obj'].addData(showitem['inst'], np.random.normal(size=1).tolist())
def updatePlots():
	global signallist
	for signal in signallist:
		for showitem in signal['showlist']:
			if showitem['showtype'] == 'PLOT':
				showitem['obj'].update()

def updateTable():
	global signallist
	for signal in signallist:
		for showitem in signal['showlist']:
			if showitem['showtype'] == 'TABLE':
				showitem['obj'].update()
	
timerDat = pg.QtCore.QTimer()
timerDat.timeout.connect(updateData)
#timerDat.start(10)

timer = pg.QtCore.QTimer()
timer.timeout.connect(updatePlots)
timer.start(configobjs[JKEY_PLOTREFRESH_MS])
#timer.start(50)

timer2 = pg.QtCore.QTimer()
timer2.timeout.connect(updateTable)
timer2.start(configobjs[JKEY_TABLEREFRESH_MS])


decodestr += decodestrtail
print decodestr

#We will start a thread and parse the serial protocol packet
def serialWorker(port, baud, decodestr):
	import serial
	global signallist
	global stopWorker
	ser = serial.Serial(port, baud)
	print ser
	print("Starting Serial Worker Thread");		
	bytestr = ''
	while(1):
		if stopWorker:
			return
		byte = ser.read()
		bytestr+= byte
		if len(bytestr) == 4:
			dat = struct.unpack('<I', bytestr[0:4])[0]
			if dat == PRTCL_SOF:
				while 1:
					if stopWorker:
						return
					bytestr += ser.read()	
					if(len(bytestr) == 8):
						datalen = struct.unpack('<I', bytestr[4:8])[0]
						totlen = datalen + 8		#for CRC and EOF
						while(totlen):
							if stopWorker:
								return
							bytestr += ser.read()
							totlen -= 1
						#We have the complete packet. Validate it
						try:
							decodedata = struct.unpack(decodestr, bytestr)
							bytestr = ''
							if decodedata[PRTCL_INDEXOF_SOF] != PRTCL_SOF:
								print("INvalid Packet. ERR in SOF");
								break

							if decodedata[-1] != PRTCL_EOF:
								print("Invalid Packet. ERR in EOF Got : "), (hex(decodedata[-1]))
								break
							#We have the compelte data. Add it to the dock data list
							dlen = len(decodestr) - 5
							assert(dlen == len(signallist))
							inst = 0
							for signal in signallist:
								for showitem in signal['showlist']:
									showitem['obj'].addData(showitem['inst'], [decodedata[PRTCL_INDEXOF_DATA + inst]])
								inst += 1
							break
						except Exception as e:
							print("Not possible to decode data "), e;
							bytestr = ''
							break
						
						
			else:
				bytestr = bytestr[1:]
				continue


		


thread = Thread(target= serialWorker, args=("/dev/ttyACM1", 115200, decodestr))
thread.start()
win.show()

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
	stopWorker = True

