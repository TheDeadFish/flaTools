import hashlib
from utils import *

class Symbol:

	def __init__(self, symbol, attr, data, name):
		self.symbol = symbol;	self.attr = attr;
		self.data = data; self.name = name;
		self.hash_ = None; self.hash = None;
		self.refs = []; self.keep = False;

	def do_hash(self, dict):
		if self.hash: return;
		if not len(self.refs):
			self.hash = self.hash_; return;
		hash = hashlib.sha1()
		hash.update(self.hash_)
		for x in self.refs:
			dict[x].do_hash(dict);
			hash.update(dict[x].hash)
		self.hash = hash.digest();
		
"""
	def update(self, map):
		if self.symbol:
		
			for x in self.refs:
				
				
				
			
		
		
			data.replace(
		else:
			self.attr['name'] = map[self.name]
"""

def parse_symbols(doc, files):
	symList = {}
	
	media = doc.getElementsByTagName('media');
	for x in media[0].childNodes:
		if x.nodeType != x.ELEMENT_NODE: continue
		
		# basic symbol info
		attr = elem_to_dict(x)
		for x in attr:
			if x.endswith("HRef"):
				data = files['bin/'+attr[x]]
		tmp = Symbol(False, attr, data, attr['name']);
		
		# content hash
		hash = hashlib.sha1()
		hash.update(data);
		tmp.hash_ = hash.digest();
		
		symList[tmp.name] = tmp
	
	symbols = doc.getElementsByTagName('symbols');
	for x in symbols[0].childNodes:
		if x.nodeType != x.ELEMENT_NODE: continue
		
		# basic symbol info
		attr = elem_to_dict(x)
		data = files['LIBRARY/'+attr['href']]
		name = index_qstr(data, 'name="');
		tmp = Symbol(True, attr, data, name);
		
		# parse symbol data
		symList[tmp.name] = tmp
		hash = hashlib.sha1()
		
		# get library refs
		pos = tmp.data.index('>')+1
		while True:
			prevPos = pos
			pos = find_end(tmp.data, 'libraryItemName="', pos)
			if pos < 0: 
				hash.update(buffer(tmp.data, prevPos))
				tmp.hash_ = hash.digest(); break;
			hash.update(buffer(tmp.data, prevPos, pos-prevPos))
			end = tmp.data.index('"', pos)	
			list_add_unique(tmp.refs, tmp.data[pos:end])
			pos = end
		
	# compute hashes
	for x in symList:
		symList[x].do_hash(symList);
			
	return symList
	
class FlaFile:


	def __init__(self, fName):
		self.files = load_zip(fName)
		del self.files['bin/SymDepend.cache']
		
		
"""
		
		
		
		
		
	
	
	



	
	
files = load_zip("MLP214_001-new.fla")


doc = load_xml(files['DOMDocument.xml'])
files['DOMDocument.xml'] = save_xml(doc, files['DOMDocument.xml'])

print parse_symbols(doc, files)

save_zip("out.fla", files)
			
			

"""



	
	
			





