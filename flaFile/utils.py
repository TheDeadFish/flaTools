import zipfile
import xml.dom.minidom

def list_add_unique(lst, item):
	if item in lst: return
	lst.append(item)
	
def index_end(str, elem, start=0):
	pos = str.index(elem, start);
	return pos + len(elem);
def find_end(str, elem, start=0):
	pos = str.find(elem, start);
	if pos >= 0: pos += len(elem);
	return pos
	
def index_qstr(str, elem, start=0):
	pos = index_end(str, elem, start);
	end = str.index('"', pos)
	return str[pos:end]

def load_zip(fName):
	files = {}
	with zipfile.ZipFile(fName, 'r') as myzip:
		names = myzip.namelist()
		for x in names:
			files[x] = myzip.read(x)
	return files

def save_zip(fName, files):
	with zipfile.ZipFile(fName, 'w') as myzip:
		for x in files:
			myzip.writestr(x, files[x])
			
def save_xml(doc, tmpl):
	str = doc.toxml(); y = tmpl.index('>',22)+22
	return tmpl[:tmpl.index('>')] + str[y:]
	
def load_xml(str):
	return xml.dom.minidom.parseString(str)
	
def elem_to_dict(elem):
	items = elem.attributes.items()
	ret = {}
	for x in items:
		ret[x[0]] = x[1]
	return ret
	