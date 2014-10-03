import fontforge

def	importIcon(junk, font):
	iconbase = 0xe000
	while iconbase in font:
		iconbase += 1
	svgfile = fontforge.openFilename("Select SVG file", "", "*.svg")
	if svgfile:
		newglyph = font.createChar(iconbase)
		newglyph.importOutlines(svgfile)

fontforge.registerMenuItem(importIcon,None,None,"Font",None,"Import Icon");