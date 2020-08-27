# DeadFish Shitware xml parser
# because all the existing ones are complete shit

import re
from collections import OrderedDict
import time



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
		quot = '"'; 
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
			self.attr[str[pos:equ]] = str[equ+2:end]
			pos = end+1
			
		# parse children
		if str[pos] == '/': return pos+2
		return self.set_innerXML(str, pos+1);
			
node = XmlNode()

node.set_innerXML("<fred poop='greb'/>hello<joe poop='sdfsdf'>greb</joe>")
print node.get_outerXML()


