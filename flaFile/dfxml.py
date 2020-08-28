# DeadFish Shitware xml parser
# because all the existing ones are complete shit

import re
from collections import OrderedDict
import dfxmlent

def SU(str,s):
	return buffer(str, s)
#def SV(str,s,e):
#	return buffer(str, s, e-s)

def parse_prop(str, pos):
	equ = str.index('=', pos)
	end = str.index(str[equ+1], equ+3)
	
def encode_tag(tag, attr, hasChild=0):
	str = '<'+tag; 
	for k, v in attr.iteritems():
		v = dfxmlent.encode(v); quot = '"'; 
		if '"' in v: quot = "'"
		str += ' %s=%s%s%s' % (k, quot, v, quot)
	if hasChild: str += '>'
	else: str += '/>'
	return str

class XmlNode:

	def __init__(self):
		self.tag = None
		self.children = []
		self.attr = OrderedDict()
		
	def __str__(self):
		return self.get_outerXML()
		
	@staticmethod
	def create_fromFile(name):
		with open(name, 'r') as f:
			return XmlNode.create_fromStr(f.read())
	
	@staticmethod
	def create_fromStr(str):
		node = XmlNode()
		node.set_outerXML(str)
		return node
		
	@staticmethod
	def create_text(text):
		node = XmlNode(); node.tag = "";
		node.text = text; return node
		
	@staticmethod
	def create_elem(tag, attr=OrderedDict()):
		node = XmlNode(); node.tag = tag
		node.attr = attr; return node
	
	# append nodes
	def append_node(self, node):
		self.children.append(node)
	def append_text(self, text):
		self.append_node(self.create_text(text))
	def append_elem(self, tag, attr=OrderedDict()):
		self.append_node(self.create_elem(tag, attr))
		
	# remove nodes
	def node_index(self, node):
		return self.children.index(node)
	def remove_node(self, node):
		return self.remove_index(node_index(node))
	def remove_index(self, index):
		return self.children.pop(index);
	def remove_all(self):
		self.children = []
		
	# search nodes
	def find(self, tag):
		for x in self.children:
			if x.tag == tag: return x
			y = x.find(tag);
			if y: return y
		return None

	def get_innerXML(self, str=''):
		for x in self.children:
			str = x.get_outerXML(str)
		return str
	
	def get_outerXML(self, str=''):
		if self.tag != None:
			if self.tag == "": str += self.text; return str
			str += encode_tag(self.tag, self.attr, len(self.children));
		
		if not len(self.children): return str
		str = self.get_innerXML(str)
		if self.tag: str += '</%s>'%self.tag
		return str
		
	def set_innerXML(self, str, pos=0):
		while pos < len(str):
			if str.startswith('</', pos):
				return str.index('>', pos)+1
			node = XmlNode()
			pos = node.set_outerXML(str, pos)
			self.children.append(node)
		return pos;
			
	def set_outerXML(self, str, pos=0):
		# parse text node
		if str[pos] != '<':
			end = str.find('<', pos)
			if end < 0: end = len(str)
			self.text = str[pos:end]
			self.tag = ""; return end
			
		# parse tag name
		pos += 1
		end = re.search(r'[^\s/>]+', 
			SU(str, pos)).end()+pos;
		self.tag = str[pos:end]
		pos = end
		
		# parse attributes
		while str[pos] == ' ':
			pos += 1; equ = str.index('=', pos)
			end = str.index(str[equ+1], equ+3)
			self.attr[str[pos:equ]] = dfxmlent.decode(str[equ+2:end])
			pos = end+1
			
		# parse children
		if str[pos] == '/': return pos+2
		return self.set_innerXML(str, pos+1);
