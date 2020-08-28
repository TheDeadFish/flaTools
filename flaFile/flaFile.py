import hashlib
from collections import OrderedDict
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

	def __init__(self, tag, attr):
		self.tag = tag;	self.attr = attr;
		self.data = None; self.name = attr.get('name');
		self.hash_ = None; self.hash = None;
		self.refs = []; self.keep = False;
		
	@property
	def symbol(self):
		return self.tag == 'Include'
		
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
		self.refs = [dict[x] for x in self.refs]
		for x in self.refs:
			x.do_hash(dict);
			hash.update(x.hash)
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
		
class FlaFrame:
	def __init__(self, node, dict):
		self.node = node
		refs = node.find_attr_all('libraryItemName')
		self.refs = [dict[x] for x in refs]
	
class FlaLayer:
	def __init__(self, node, dict):
		self.attr = elem_to_dict(node)
		self.frames = []
		for x in node.find_all('DOMFrame'):
			self.frames.append(FlaFrame(x, dict))
	
class FlaTimeLine:
	def __init__(self, node, dict):
		self.attr = elem_to_dict(node)
		self.layers = []
		for x in node.find_all('DOMLayer'):
			self.layers.append(FlaLayer(x, dict))
	
class FlaFile:

	def __init__(self, fName):
		self.files = load_zip(fName)
		del self.files['bin/SymDepend.cache']
		domData = self.files['DOMDocument.xml']
		self.dom = load_xml(domData)
				
		# load the symbols
		symDict = OrderedDict()
		self.__load_symbols(symDict);
		self.__parse_scene(symDict);
		self.symbols = [v for k,v in symDict.iteritems()]
		
	def save(self, fName):
		for v in self.symbols: self.files[v.get_path()] = v.data
		self.__rebuild_symbols(); self.__build_scene()
		self.files['DOMDocument.xml'] =	save_xml(self.dom, domHeadOrder)
		save_zip(fName, self.files)
		
	def __load_symbols(self, symDict):
		self.__parse_symbols('media', symDict)
		self.__parse_symbols('symbols', symDict)
		for k,v in symDict.iteritems(): 
			v.do_hash(symDict);
			
	def __parse_symbols(self, nodeName, symDict):
		node = self.dom.find(nodeName);
		for x in node.children:
			if not x.tag: continue
			symb = Symbol(x.tag, elem_to_dict(x));
			symb.init(self.files.pop(symb.get_path()))
			symDict[symb.name] = symb
		node.remove_all()
		
	def __rebuild_symbols(self):
		nodes = [self.dom.find('media'), self.dom.find('symbols')]
		for v in self.symbols:
			nodes[v.symbol].append_text('\r\n          ')
			nodes[v.symbol].append_elem(v.tag, v.attr)
		nodes[0].append_text('\r\n     ')
		nodes[1].append_text('\r\n     ')
		
	def __parse_scene(self, symDict):
		self.scene = []
		node = self.dom.find('timelines');
		for x in node.children:
			if not x.tag: continue
			self.scene.append(FlaTimeLine(x, symDict))
		node.remove_all()
		
	def __build_frames(self, frames, node):
		node = indent_elem(node, 25, 20, 'frames')
		for frame in frames:
			indent_crlf(node, 30)
			node.append_node(frame.node)
		if len(frames): indent_crlf(node, 25)
		
	def __build_layer(self, layers, node):
		node = indent_elem(node, 15, 10, 'layers')
		for layer in layers:
			indent_crlf(node, 20)
			self.__build_frames(layer.frames,
				node.append_elem('DOMLayer', layer.attr))
		if len(self.scene): indent_crlf(node, 15)
		
	def __build_scene(self):
		node = self.dom.find('timelines');
		for scn in self.scene:
			indent_crlf(node, 10)
			self.__build_layer(scn.layers,
				node.append_elem('DOMTimeline', scn.attr))
		if len(self.scene): indent_crlf(node, 5)
