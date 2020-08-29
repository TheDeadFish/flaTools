import hashlib
from collections import OrderedDict
from utils import *
import re
	
class FlaNode:
	def __init__(self):	self.refs = []
	@property
	def name(self): return self.attr['name']
	@name.setter
	def name(self, x): self.attr['name'] = x
	def __getitem__(self, i): return self.refs[i]
	def __iter__(self): return self.refs.__iter__()
	
	def get(self, i=None):
		if isinstance(i, FlaNode): return i;
		if i == None: return self[0]
		if type(i) == int: return self[i]
		for x in self: 
			if x.name == i: return x
		return None
	
	def remove(self, i):
		x = self.get(i); 
		self.refs.remove(x); 
		return x
	
	def keep(self, klst):
		self.refs = [x for x in self if x.name in klst]

class Symbol(FlaNode):

	def __init__(self, tag, attr):
		FlaNode.__init__(self)
		self.tag = tag;	self.attr = attr;
		self.data = None; self.name = attr.get('name');
		self.hash_ = None; self.hash = None;
		self.keep = False;
		
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
		hash = hashlib.sha1()
		
		pos = 0
		if self.symbol:
			xx = re.finditer(r'(libraryItemName|soundName)="([^"]*)"', self.data)
			for x in xx:
				curPos = x.start(2)
				hash.update(buffer(self.data, curPos, curPos-pos))
				name = x.group(2); dict[name].do_hash(dict)
				self.refs.append(dict[name])
				hash.update(dict[name].hash)
				pos = curPos
		
		hash.update(buffer(self.data, pos));
		self.hash = hash.digest();
		
	def init(self, data):
		self.data = data
		if self.symbol:
			self.name = index_qstr(self.data, 'name="');
		
class FlaFrame(FlaNode):
	def __init__(self, node, dict):
		FlaNode.__init__(self)
		self.node = node
		refs = node.find_attr_all('libraryItemName')
		self.refs = [dict[x] for x in refs]
		
	@property
	def attr(self): return self.node.attr
	
class FlaLayer(FlaNode):
	def __init__(self, node, dict):
		FlaNode.__init__(self)
		self.attr = elem_to_dict(node)
		for x in node.find_all('DOMFrame'):
			self.refs.append(FlaFrame(x, dict))
	
class FlaTimeLine(FlaNode):
	def __init__(self, node, dict):
		FlaNode.__init__(self)
		self.attr = elem_to_dict(node)
		for x in node.find_all('DOMLayer'):
			self.refs.append(FlaLayer(x, dict))
	
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
		self.files['DOMDocument.xml'] =	save_xml(self.dom)
		save_zip(fName, self.files)
		
	def gc_symbols(self):
		nodeset = set()
		self.__ge_recurese(nodeset, self.scene)
		self.symbols = list(nodeset)
	
	# layer manipulation
	def scene_get(self, i=None):
		return self.scene.get(i)
	def layer_get(self, i, scn=None):
		x = self.scene_get(scn); 
		return x.get(i) if x else x
	def layer_remove(self, i, scn=None):
		x = self.scene_get(scn);
		if x: return x.remove(i)
	def layer_keep(self, klst, scn=None):
		x = self.scene_get(scn);
		if x: x.keep(klst)
		
	def __load_symbols(self, symDict):
		self.__parse_symbols('media', symDict)
		self.__parse_symbols('symbols', symDict)
		for k,v in symDict.iteritems(): 
			v.do_hash(symDict);
			
	def __parse_symbols(self, nodeName, symDict):
		node = self.dom.find(nodeName);
		for x in node.children:
			symb = Symbol(x.tag, elem_to_dict(x));
			symb.init(self.files.pop(symb.get_path()))
			symDict[symb.name] = symb
		node.remove_all()
		
	def __rebuild_symbols(self):
		nodes = [self.dom.find('media'), self.dom.find('symbols')]
		for v in self.symbols:
			nodes[v.symbol].append_elem(v.tag, v.attr)
		
	def __parse_scene(self, symDict):
		self.scene = FlaNode()
		node = self.dom.find('timelines');
		for x in node.children:
			if not x.tag: continue
			self.scene.refs.append(FlaTimeLine(x, symDict))
		node.remove_all()
		
	def __build_frames(self, frames, node):
		node = node.append_elem('frames')
		for frame in frames:
			node.append_node(frame.node)
		
	def __build_layer(self, layers, node):
		node = node.append_elem('layers')
		for layer in layers:
			self.__build_frames(layer.refs,
				node.append_elem('DOMLayer', layer.attr))
		
	def __build_scene(self):
		node = self.dom.find('timelines');
		for scn in self.scene:
			self.__build_layer(scn.refs,
				node.append_elem('DOMTimeline', scn.attr))
				
	def __ge_recurese(self, nodeset, node):
		if isinstance(node, Symbol): 
			if node in nodeset: return
			nodeset.add(node)
		for x in node: self.__ge_recurese(nodeset, x)
