import fontforge, os, time, re;
#from ctypes import CDLL
import struct

ttf_tables = {
# Required Tables
	'cmap': "Character to glyph mapping",
	'head': "Font header",
	'hhea': "Horizontal header",
	'hmtx': "Horizontal metrics",
	'maxp': "Maximum profile",
	'name': "Naming table",
	'OS/2': "OS/2 and Windows specific metrics",
	'post': "PostScript information",
# Tables Related to TrueType Outlines
	'cvt ': "Control Value Table",
	'fpgm': "Font program",
	'glyf': "Glyph data",
	'loca': "Index to location",
	'prep': "CVT program",
# Tables Related to PostScript Outlines
	'CFF ': "PostScript font program (compact font format)",
# Obsolete Multiple Master support
	'fvar': "obsolete",
	'MMSD': "obsolete",
	'MMFX': "obsolete",
# Advanced Typographic Tables
	'BASE': 'Baseline data',
	'GDEF': 'Glyph definition data',
	'GPOS': 'Glyph positioning data',
	'GSUB': 'Glyph substitution data',
	'JSTF': 'Justification data',
# Tables Related to Bitmap Glyphs
	'EBDT': 'Embedded bitmap data',
	'EBLC': 'Embedded bitmap location data',
	'EBSC': 'Embedded bitmap scaling data',
# Other OpenType Tables
	'DSIG': 'Digital signature',
	'gasp': 'Grid-fitting/Scan-conversion',
	'hdmx': 'Horizontal device metrics',
	'kern': 'Kerning',
	'LTSH': 'Linear threshold data',
	'PCLT': 'PCL 5 data',
	'VDMX': 'Vertical device metrics',
	'vhea': 'Vertical Metrics header',
	'vmtx': 'Vertical Metrics',
	'VORG': 'Vertical Origin',
}

class TTFParser:

	def __init__(self, file):
		"Creates a TrueType font file parser.  File can be a file name, or a file object."
		if type(file) == type(""):
			file = open(file, "rb")
		self.file = file
		version = self.read_ulong()
		if version == 0x4F54544F:
			raise 'TTFError', 'OpenType fonts with PostScript outlines are not supported'
		if version != 0x00010000:
			raise 'TTFError', 'Not a TrueType font'
		self.numTables = self.read_ushort()
		self.searchRange = self.read_ushort()
		self.entrySelector = self.read_ushort()
		self.rangeShift = self.read_ushort()
		
		self.table = {}
		self.tables = []
		for n in range(self.numTables):
			record = {}
			record['tag'] = self.read_tag()
			record['checkSum'] = self.read_ulong()
			record['offset'] = self.read_ulong()
			record['length'] = self.read_ulong()
			self.tables.append(record)
			self.table[record['tag']] = record

		pos = file.tell()  # Save the current position
		file.seek(0, 2)  # Seek to the end of the file
		self.file_length = file.tell()  # The current position is the length
		file.seek(pos)
		print "ttf length: %d" % self.file_length

	def get_table_pos(self, tag):
		tag = (tag + "	")[:4]
		offset = self.table[tag]['offset']
		length = self.table[tag]['length']
		return (offset, length)

	def get_table(self, tag):
		offset, length = self.get_table_pos(tag)
		self.file.seek(offset)
		return self.file.read(length)

	def tell(self):
		return self.file.tell()

	def seek(self, pos):
		self.file.seek(pos)

	def skip(self, delta):
		self.file.seek(pos, 1)

	def seek_table(self, tag, offset_in_table = 0):
		pos = self.get_table_pos(tag)[0] + offset_in_table
		self.file.seek(pos)
		return pos

	def read_tag(self):
		return self.file.read(4)

	def read_ushort(self):
		s = self.file.read(2)
		return (ord(s[0]) << 8) + ord(s[1])
	def read_short(self):
		us = self.read_ushort()
		if us >= 0x8000:
			return us - 0x10000
		else:
			return us

	def read_ulong(self):
		s = self.file.read(4)
		return (ord(s[0]) << 24) + (ord(s[1]) << 16) + (ord(s[2]) << 8) + ord(s[3])

	def debug_printHeader(self):
		print "sfnt version: 1.0"
		print "numTables: %d" % self.numTables
		print "searchRange: %d" % self.searchRange
		print "entrySelector: %d" % self.entrySelector
		print "rangeShift: %d" % self.rangeShift

	def debug_printIndex(self):
		print "Tag   Offset	   Length	Checksum"
		print "----  -----------  --------  ----------"
		for record in self.tables:
			print "%(tag)4s  +0x%(offset)08X  %(length)8d  0x%(checkSum)08x" % record,
			if ttf_tables.has_key(record['tag']):
				print "", ttf_tables[record['tag']],
			print

#ttf2eot = CDLL('ttf2eot.dll')

		#unsigned eotSize;
	#unsigned fontDataSize;
	#unsigned version;
	#unsigned flags;
	#uint8_t fontPANOSE[10];
	#uint8_t charset;
	#uint8_t italic;
	#unsigned weight;
	#unsigned short fsType;
	#unsigned short magicNumber;
	#unsigned unicodeRange[4];
	#unsigned codePageRange[2];
	#unsigned checkSumAdjustment;
	#unsigned reserved[4];
	#unsigned short padding1;

def generateEOT(font, font_file_name):
	ttf = TTFParser(font_file_name + ".ttf")
	ttf.seek_table("head", 8)
	checksum = struct.unpack(">I", ttf.read_tag())[0]
	#print "checksum: %d" % checksum
	
	familyname = font.familyname.encode("utf_16_le")
	familyname_length = len(familyname)
	# if familyname_length % 4:
	# 	familyname += (u'\x00' * (familyname_length % 4 / 2)).encode("utf_16_le")
	# 	familyname_length += familyname_length % 4
	stylename = font.weight.encode("utf_16_le")
	stylename_length = len(stylename)
	# if stylename_length % 4:
	# 	stylename += (u'\x00' * (stylename_length % 4 / 2)).encode("utf_16_le")
	# 	stylename_length += stylename_length % 4
	versionname = ("Version "+font.version).encode("utf_16_le")
	versionname_length = len(versionname)
	# if versionname_length % 4:
	# 	versionname += (u'\x00' * (versionname_length % 4 / 2)).encode("utf_16_le")
	# 	versionname_length += versionname_length % 4
	fullname = font.fullname.encode("utf_16_le")
	fullname_length = len(fullname)
	# if fullname_length % 4:
	# 	fullname += (u'\x00' * (fullname_length % 4 / 2)).encode("utf_16_le")
	# 	fullname_length += fullname_length % 4
	
	print "macstyle: %d, %d" % (font.macstyle, font.macstyle & 0x1)
	
	print "fn: %d, sn: %d, vn: %d, fn: %d" % (familyname_length,stylename_length,versionname_length,fullname_length)
	
	if font.macstyle == -1:
		macstyle = 0
	else: 
		macstyle = font.macstyle
	
	prefix_fmt = struct.Struct("<4I10B2BI2H4I2II4IHH%dsHH%dsHH%dsHH%dsHH" % (familyname_length, stylename_length, versionname_length, fullname_length))
	eot_size = prefix_fmt.size + ttf.file_length
	data = prefix_fmt.pack(eot_size, ttf.file_length, 0x00020001, 0, font.os2_panose[0], font.os2_panose[1], font.os2_panose[2], font.os2_panose[3], font.os2_panose[4], font.os2_panose[5], font.os2_panose[6], font.os2_panose[7], font.os2_panose[8], font.os2_panose[9], 0x01, macstyle & 0x1, font.os2_weight, 0, 0x504c, font.os2_unicoderanges[0], font.os2_unicoderanges[1], font.os2_unicoderanges[2], font.os2_unicoderanges[3], font.os2_codepages[0], font.os2_codepages[1], checksum, 0,0,0,0,0, familyname_length, familyname, 0, stylename_length, stylename, 0, versionname_length, versionname, 0, fullname_length, fullname, 0, 0)
	ttf.file.seek(0)
	with open(font_file_name + ".eot", 'wb') as eotfile:
		eotfile.write(data)
		eotfile.write(ttf.file.read(ttf.file_length))
	

def GenerateFonts(junk, font):
	#print os.path.dirname(font.path);
	font_file_name = os.path.dirname(font.path) + '/' + font.fontname

	font.generate(font_file_name + ".ttf");
	font.generate(font_file_name + ".woff");
	font.generate(font_file_name + ".svg");
	
	#fix xmlns that chrome is fussy about
	with open(font_file_name + ".svg", 'r+') as svgfile:
		svgfont = svgfile.read().replace('<svg>', '<svg xmlns="http://www.w3.org/2000/svg">')
		#with open(font_file_name + ".svg", 'w') as svgfile:
		svgfile.seek(0)
		svgfile.truncate()
		svgfile.write(svgfont)
	#os.system('''sed -i 's#<svg>#<svg xmlns="http://www.w3.org/2000/svg">#' ''' + font_file_name + ".svg")

	#make eot
	#ttf2eot.make_eot(font_file_name + ".ttf", font_file_name + ".eot")
	#os.system("ttf2eot \""+ font_file_name + ".ttf" + "\" \"" + font_file_name + ".eot" + "\"");
	generateEOT(font, font_file_name)

	commentregex = re.compile(r"Use [A-F0-9]+ Instead")

	css = ""
	html = "<!-- VERSION 2.0 --><table width='100%'>"
	i=1
	for glyph in font.glyphs():
		if not commentregex.match(glyph.comment):
			css += '.%X:before { content: "\%X"; }\n' % (glyph.unicode, glyph.unicode)
			if i % 4 == 1:
				html += '<tr>'
			html += '<td>%X <i class="fontdemo %X"></i></td>\n' % (glyph.unicode, glyph.unicode)
			if i % 4 == 0:
				html += '</tr>'
			i += 1
	
	gentime = time.time()

	base_font_face = '''@font-face {
	font-family: '{fontname}';
	src: url('{fontname}.eot?{gentime}');
	src: url('{fontname}.eot?{gentime}#iefix') format('embedded-opentype'),
		 url('{fontname}.svg?{gentime}#{fontname}') format('svg'),
		 url('{fontname}.woff?{gentime}') format('woff'),
		 url('{fontname}.ttf?{gentime}') format('truetype');
	font-weight: normal;
	font-style: normal;
}'''

	if 0xe000 in font:#dont bother if not icon based font!
		f = open(font_file_name + ".html",'w')
		htmlbase = "<style>"+base_font_face+"\n.fontdemo:before { display: inline; font-size: 40px; font-family: {fontname}; font-style: normal; }\n"
		htmlbase = htmlbase.replace("{fontname}", font.fontname)
		htmlbase = htmlbase.replace("{gentime}", "%d" % gentime)
		f.write(htmlbase)
		f.write(css+'</style>')
		f.write(html+'</table>')
		f.close();

	#write css file too
	f = open(font_file_name + ".css",'w')
	f.write(base_font_face.replace("{fontname}", font.fontname).replace("{gentime}", "%d" % gentime))

	fontforge.postNotice("Finished", "Files have been output")

fontforge.registerMenuItem(GenerateFonts,None,None,"Font",None,"Generate Webfonts");