
dtypes4bytes = {
	'1': ['char', 'uint8', 'int8'],
	'2': ['uint16', 'int16'],
	'4': ['uint32', 'int32', 'float'],
	'8': ['uint64', 'int64', 'double'],
}

unpackchar = { 
		'char': 'c', 'uint8':'B', 'int8': 'b',
		'uint16' : 'H', 'int16' : 'h',
		'uint32' : 'I', 'int32' : 'i', 'float'  : 'f',
		'uint64' : 'Q', 'int64' : 'q', 'double' : 'd',
		'string' : 's'
}

datatypeslist = unpackchar.keys()
	     
tableopts = {'SIGNAL':0, 'VAL':1, 'AVG':2, 'MIN':3, 'MAX':4}
tableoptkeys = ['SIGNAL','VAL', 'AVG', 'MIN', 'MAX']  #Order is important. Should match tableopts


MAX_PTS_TO_SHOW = 1000
MAX_PTS_TO_UPDATE = 500
