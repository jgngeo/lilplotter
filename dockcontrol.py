import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui


class controlDock(pg.LayoutWidget, QtCore.QObject):
	paused = QtCore.pyqtSignal(bool)
	showLegend = QtCore.pyqtSignal(bool)
	def __init__(self, title):
		pg.LayoutWidget.__init__(self) 
		lab = QtGui.QLabel(title)
		self.addWidget(lab, row=0, col=0)

		self.pauseBtn = QtGui.QPushButton('Pause')
		self.pauseBtn.clicked.connect(self.pausePressed)
		self.addWidget(self.pauseBtn, row=1, col=0)

		self.legendBtn = QtGui.QPushButton('Legend')
		self.legendBtn.setCheckable(True)
		self.legendBtn.clicked.connect(self.legendPressed)
		self.addWidget(self.legendBtn, row=1, col=1)

		self.updatepaused = False

	def pausePressed(self):
		self.updatepaused = False if self.updatepaused else True
		if self.updatepaused:
			self.pauseBtn.setText('Resume')
		else:
			self.pauseBtn.setText('Pause')

		self.paused.emit(self.updatepaused)
	
	def legendPressed(self):
		self.showLegend.emit(self.legendBtn.isChecked())
			
	
