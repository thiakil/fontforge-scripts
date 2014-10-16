import fontforge

scaleup = psMat.scale(1.001)
scaledown = psMat.scale(0.999)

def	importIcon(junk, font):
	iconbase = 0xe000
	while iconbase in font and font[iconbase].isWorthOutputting():
		iconbase += 1
	svgfile = fontforge.openFilename("Select SVG file", "", "*.svg")
	if svgfile:
		newglyph = font.createChar(iconbase)
		try:
			newglyph.importOutlines(svgfile)
			newglyph.right_side_bearing = 0
			newglyph.left_side_bearing = 0

			boundingbox = newglyph.layers[1].boundingBox()
			if boundingbox[2]-boundingbox[0] > 1000 or boundingbox[3]-boundingbox[1] > 1000:
				print("bigger than 1000")
				if boundingbox[2]-boundingbox[0] > boundingbox[3]-boundingbox[1]:
					while boundingbox[2]-boundingbox[0] > 1000:
						newglyph.transform(scaledown, ["round"])
						boundingbox = newglyph.layers[1].boundingBox()
				else:
					while boundingbox[3]-boundingbox[1] > 1000:
						newglyph.transform(scaledown, ["round"])
						boundingbox = newglyph.layers[1].boundingBox()
			elif boundingbox[2]-boundingbox[0] < 1000 or boundingbox[3]-boundingbox[1] < 1000:
				print("smaller than 1000")
				if boundingbox[2]-boundingbox[0] > boundingbox[3]-boundingbox[1]:
					while boundingbox[2]-boundingbox[0] < 1000:
						newglyph.transform(scaleup, ["round"])
						boundingbox = newglyph.layers[1].boundingBox()
				else:
					while boundingbox[3]-boundingbox[1] < 1000:
						newglyph.transform(scaleup, ["round"])
						boundingbox = newglyph.layers[1].boundingBox()

			newglyph.right_side_bearing = 0
			newglyph.left_side_bearing = 0

		except Exception as e:
			fontforge.postError("Error", "Something went wrong!\n\n"+e)
			#newglyph.clear()
			font.removeGlyph(iconbase)

fontforge.registerMenuItem(importIcon,None,None,"Font",None,"Import Icon");