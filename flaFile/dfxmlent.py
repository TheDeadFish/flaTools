import re

ent_table = { '&quot;':'"', '&amp;':'&', '&apos;':'\'', '&lt;':'<', '&gt;':'>' }
ent_table2 = {v: k for k, v in ent_table.iteritems()}
ent_re = re.compile(r'["&\'<>]')

def SU(str,s):
	return buffer(str, s)

def decode(str):
	pos = 0
	while True:
		pos = str.find('&', pos)
		if pos < 0: return str
		end = str.index(';', pos+1)+1;
		ch = ent_table[str[pos:end]]
		str = str[:pos] + ch + str[end:]
		pos += 1
		
def encode(str):
	pos = 0
	while pos < len(str):
		m = ent_re.search(SU(str,pos))
		if not m: return str
		pos += m.start(); ch = ent_table2[m.group()]
		end = pos+len(ch)
		str = str[:pos] + ch + str[pos+1:]
		pos = end
