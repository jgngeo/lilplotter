from pyqtgraph.dockarea import *
import pyqtgraph as pg

from utils import *
from pyqtgraph.Qt import QtCore, QtGui
 
modes = ["PLOT", "TABLE"]

pens = ['b', 'r', 'g', 'c', 'y']

class lildock(Dock):
	def __init__(self, title, mode="PLOT", size=None, closable=False):
		if mode not in modes:
			raise Exception("INvalid Mode Specified. PSecify PLOT or TABLE")	
		self.mode = mode
		Dock.__init__(self, title, size=size, closable=closable) 
		self.newdata =  []
		self.data = []
		self.refdata = []
		self.startindex = 0
		self.endindex = 0
		if  mode == "PLOT":
			self.wid = pg.PlotWidget(title="")
			self.addWidget(self.wid)
			self.plotList = []
		elif mode == "TABLE":
			self.wid = pg.TableWidget()
			self.addWidget(self.wid)
			self.wid.setColumnCount(len(tableoptkeys))
			self.wid.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
			self.tabList = []



	#Returns the instance ID.
	def addPlot(self, pen='k', name="Curve"):
		if self.mode != "PLOT":
			raise Exception("Mode for this dock should be PLOT")

		self.data.append([])
		self.newdata.append([])
		plot = self.wid.plot(self.data[-1], pen=pen, name=name)
		print plot
		self.plotList.append(plot)
		return len(self.plotList)-1;
		
	def addTable(self, ydata, pen='k', name="Curve"):
		if self.mode != "TABLE":
			raise Exception("Mode for this dock should be TABLE")

		#qlab = QtGui.QLabel("Hello World")
		#self.wid.insertRow(len(self.data))
		#self.wid.setCellWidget(len(self.data), 0, qlab)

		print ("Rows = %d Cols = %d" %(self.wid.rowCount(), self.wid.columnCount()))

		self.data.append([0] * len(tableoptkeys))
		
		self.newdata.append([])
		
		self.tabList.append(None)
		
		self.wid.clear()
		self.data[-1][tableopts['SIGNAL']] = name
		self.wid.setData(self.data)
		self.wid.setHorizontalHeaderLabels(tableoptkeys)
		#print name, len(self.tabList) -1, tableopts['SIGNAL']

		return len(self.tabList)-1;

	def addData(self, inst, dat):
		self.newdata[inst] += dat

	def isPlotTransformationsApplied(self):
		uiobj =  self.wid.plotItem.ctrl
		return (uiobj.fftCheck.isChecked() or uiobj.logXCheck.isChecked() or uiobj.logYCheck.isChecked())
		

	def update(self):
		if self.mode == "PLOT":
			#update only the number of points for which all the plots have been updated
			lenlist = []
			for inst in range(len(self.data)):
				lenlist.append(len(self.newdata[inst]))	

			updatelen = min(lenlist)
			updatelen = MAX_PTS_TO_UPDATE if  updatelen > MAX_PTS_TO_UPDATE	else updatelen

			if updatelen:
				lenavail = MAX_PTS_TO_SHOW - len(self.data[0])
				removelen = (updatelen - lenavail) if (updatelen > lenavail) else 0
			
				if len(self.refdata):
					if len(self.refdata) < MAX_PTS_TO_SHOW:
						self.startindex = 0
						self.endindex = len(self.refdata)
					else:
						if not self.isPlotTransformationsApplied() :
							rangex = self.wid.viewRange()[0]
							start = int(rangex[0])
							end = int(rangex[1])
							npts = end - start
							if start > 0 and start > self.refdata[0]:
								self.startindex = self.refdata.index(start)
							else:
								self.startindex = 0
							if end < self.refdata[-1]:
								self.endindex = self.refdata.index(end)
							else:
								self.endindex = len(self.refdata) - 1
					self.refdata += range(self.refdata[-1]+1, self.refdata[-1] + updatelen+1)
					self.refdata = self.refdata[removelen:]
				else:
					self.refdata += range(0, updatelen)
				
				#print self.startindex, self.endindex	
				if not self.isPlotTransformationsApplied() :
					self.wid.setXRange(self.refdata[self.startindex], self.refdata[self.endindex], padding = 0)

				for inst in range(len(self.data)):
					self.data[inst][:] = self.data[inst][removelen:]
					self.data[inst] += self.newdata[inst][:updatelen]
					del self.newdata[inst][:updatelen]
					self.plotList[inst].setData(self.refdata, self.data[inst], pen=pens[inst])

		elif self.mode == "TABLE":
			for inst in range(len(self.data)):
				if len(self.newdata[inst]):
					self.data[inst][tableopts['VAL']] = self.newdata[inst][-1]
					#print inst
					#print (self.wid.item(inst, 0))
					if max(self.newdata[inst]) > self.data[inst][tableopts['MAX']]:
						self.data[inst][tableopts['MAX']] = max(self.newdata[inst])
					if min(self.newdata[inst]) < self.data[inst][tableopts['MIN']]:
						self.data[inst][tableopts['MIN']] = min(self.newdata[inst])

					self.data[inst][tableopts['AVG']] = (((sum(self.newdata[inst])/len(self.newdata[inst])) + self.data[inst][tableopts['AVG']])/2)
					
					self.wid.item(inst, tableopts['VAL']).setText(str(self.data[inst][tableopts['VAL']]))
					self.wid.item(inst, tableopts['MIN']).setText(str(self.data[inst][tableopts['MIN']]))
					self.wid.item(inst, tableopts['MAX']).setText(str(self.data[inst][tableopts['MAX']]))
					self.wid.item(inst, tableopts['AVG']).setText(str(self.data[inst][tableopts['AVG']]))
					del self.newdata[inst][:]
