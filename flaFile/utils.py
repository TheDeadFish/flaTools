import zipfile
from dfxml import XmlNode

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
	
def qstr_skip(str, s):
	return str.index('"', str.index('"', s)+1)+1
	
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
	return doc.get_outerXML();
	
def load_xml(str):
	return XmlNode.create_fromStr(str)
	
def elem_to_dict(elem):
	return elem.attr
	
def indent_crlf(node, level):
	node.append_text('\r\n'+level*' ')
	
def indent_elem(node, pre, post, tag, attr=None):
	indent_crlf(node, pre)
	ret = node.append_elem(tag, attr)
	indent_crlf(node, post)
	return ret
