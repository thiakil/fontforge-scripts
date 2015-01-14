import fontforge

scaleup = psMat.scale(1.001)
scaledown = psMat.scale(0.999)
translateup = psMat.translate(0, 0.1)
translatedown = psMat.translate(0, -0.1)

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

			boundingbox = newglyph.boundingBox()
			if boundingbox[3]-boundingbox[1] > 1000:
				print("bigger than 1000")
				while boundingbox[3]-boundingbox[1] > 1000:
					newglyph.transform(scaledown)
					boundingbox = newglyph.boundingBox()
			elif boundingbox[3]-boundingbox[1] < 1000:
				print("smaller than 1000")
				while boundingbox[3]-boundingbox[1] < 1000:
					newglyph.transform(scaleup)
					boundingbox = newglyph.boundingBox()

			boundingbox = newglyph.boundingBox()
			#fontforge.postNotice("Info", "y1 = %f, y2 = %f" % (boundingbox[1], boundingbox[3]))
			print("y1 = %f, y2 = %f" % (boundingbox[1], boundingbox[3]))
			if min(boundingbox[1], boundingbox[3]) > -200:
				print("need to move down")
				while min(boundingbox[1], boundingbox[3]) > -200:
					newglyph.transform(translatedown)
					boundingbox = newglyph.boundingBox()
			elif max(boundingbox[1], boundingbox[3]) > 1000:
				while max(boundingbox[1], boundingbox[3]) > 1000:
					print("need to move up")
					newglyph.transform(translateup)
					boundingbox = newglyph.boundingBox()

			newglyph.right_side_bearing = 0
			newglyph.left_side_bearing = 0

		except Exception as e:
			fontforge.postError("Error", "Something went wrong!\n\n"+str(e))
			#newglyph.clear()
			font.removeGlyph(iconbase)

fontforge.registerMenuItem(importIcon,None,None,"Font",None,"Import Icon");