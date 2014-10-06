import fontforge, os, time;
from ctypes import CDLL

ttf2eot = CDLL('ttf2eot.dll')

def GenerateFonts(junk, font):
	#print os.path.dirname(font.path);
	font_file_name = os.path.dirname(font.path) + '/' + font.fontname

	font.generate(font_file_name + ".ttf");
	font.generate(font_file_name + ".woff");
	font.generate(font_file_name + ".svg");
	
	#fix xmlns that chrome is fussy about
	with open(font_file_name + ".svg", 'r') as svgfile:
		svgfont = svgfile.read().replace('<svg>', '<svg xmlns="http://www.w3.org/2000/svg">')
	with open(font_file_name + ".svg", 'w') as svgfile:
		svgfile.write(svgfont)
	#os.system('''sed -i 's#<svg>#<svg xmlns="http://www.w3.org/2000/svg">#' ''' + font_file_name + ".svg")

	#make eot
	ttf2eot.make_eot(font_file_name + ".ttf", font_file_name + ".eot")
	#os.system("ttf2eot \""+ font_file_name + ".ttf" + "\" \"" + font_file_name + ".eot" + "\"");

	css = ""
	html = "<table width='100%'>"
	i=1
	for glyph in font.glyphs():
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