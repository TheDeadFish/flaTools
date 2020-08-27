import hashlib
from utils import *

domHeadOrder = [
	'xmlns:xsi', 'xmlns', 'backgroundColor', 'gridColor', 'guidesColor', 
	'width', 'height', 'currentTimeline', 'xflVersion', 'creatorInfo', 
	'platform', 'versionInfo', 'majorVersion', 'buildNumber', 'gridSpacingX', 
	'gridSpacingY', 'snapAlign', 'snapAlignBorderSpacing', 'objectsSnapTo', 
	'timelineHeight', 'timelineLabelWidth', 'nextSceneIdentifier', 
	'viewOptionsPasteBoardView', 'playOptionsPlayLoop', 'playOptionsPlayPages', 
	'playOptionsPlayFrameActions'];

class Symbol:

	def __init__(self, symbol, attr):
		self.symbol = symbol;	self.attr = attr;
		self.data = None; self.name = attr.get('name');
		self.hash_ = None; self.hash = None;
		self.refs = []; self.keep = False;
		
	def get_path(self):
		if self.symbol: return 'LIBRARY/'+self.attr['href']
		return 'bin/'+self.attr[self.attrHref()]
		
	def attrHref(self):
		for x in self.attr:
			if x.endswith("HRef"):
				return x

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
		
	def init(self, data):
		self.data = data
		hash = hashlib.sha1()
		if not self.symbol:
			hash.update(data);
		else:
			self.name = index_qstr(self.data, 'name="');
			
			# get library refs
			pos = self.data.index('>')+1
			while True:
				prevPos = pos
				pos = find_end(self.data, 'libraryItemName="', pos)
				if pos < 0: 
					hash.update(buffer(self.data, prevPos)); break;
				hash.update(buffer(self.data, prevPos, pos-prevPos))
				end = self.data.index('"', pos)	
				list_add_unique(self.refs, self.data[pos:end])
				pos = end
		
		self.hash_ = hash.digest();
	
class FlaFile:

	def __init__(self, fName):
		self.files = load_zip(fName)
		del self.files['bin/SymDepend.cache']
		domData = self.files['DOMDocument.xml']
		self.dom = load_xml(domData)
				
		# load the symbols
		self.symbols = {}
		self.__parse_symbols('media', False)
		self.__parse_symbols('symbols', True)
		for k,v in self.symbols.iteritems(): v.do_hash(self.symbols);
		
	def save(self, fName):
		for k,v in self.symbols.iteritems(): self.files[v.get_path()] = v.data
		self.files['DOMDocument.xml'] =	save_xml(self.dom, domHeadOrder)
		save_zip(fName, self.files)
			
	def __parse_symbols(self, nodeName, symbMode):
		nodes = self.dom.getElementsByTagName(nodeName);
		for x in nodes[0].childNodes:
			if x.nodeType != x.ELEMENT_NODE: continue
			symb = Symbol(symbMode, elem_to_dict(x));
			symb.init(self.files.pop(symb.get_path()))
			self.symbols[symb.name] = symb
			
		
		
"""
		
		
		
		
		
	
	
	



	
	
files = load_zip("MLP214_001-new.fla")


doc = load_xml(files['DOMDocument.xml'])
files['DOMDocument.xml'] = save_xml(doc, files['DOMDocument.xml'])

print parse_symbols(doc, files)

save_zip("out.fla", files)
			
			

"""



	
	
			





