
# This module takes lists of raw objects: (fill=True/False, [(x1, y1), (x2, y2), ...]) and generates a .kicad_mod file
# TODO comments, license

kicadPcbHeaderTemplate = """(module {name} (layer F.Cu)
"""
# TODO make invisible ref and value, otherwise the defaults get added with visible=True.


def makeKicadPolygon(points, fill, layer, lineWidth):
   # points = [(x1,y1),(x2,y2),...]
   # fill is current ignored (see below)
   # layer is a string, used verbatim
   # lineWidth is a float, used verbatim (see below)
   #
   # It seems to be filled always - TODO investigate this.
   # Smaller line widths make it less "rounded" looking.
   #  The fill is drawn as the the fill, period.
   #  Then it makes a line of width lineWidth from point to point to point.
   #  If you make this line very thin then the line doesn't affect things very much.
   #
   # TODO what about inverting the Y coordinates?
   # TODO really long lines seem to mess up the parser
   #pointList = " ".join( ["(xy %f %f)" % (x, y) for x, y in points] )
   pointList = ""
   for ii in range(len(points)):
      x, y = points[ii]
      pointList += "(xy %f %f) " % (x, y)
      if ii % 10 == 0:
         pointList += "\n                "
   pointList += "\n"

   return "  (fp_poly (pts %s) (layer %s) (width %f))\n" % (pointList, layer, lineWidth)


def writeRawObjectsToKicadPcbnewModuleFile(filename, rawObjects, name="ConvertedSvgModule", layer="F.SilkS", lineWidth=0.01):

   with open(filename, "w") as fid:
      # Header
      fid.write(kicadPcbHeaderTemplate.format(name=name))

      # Body
      for fill, points in rawObjects:
         fid.write(makeKicadPolygon(points, fill, layer, lineWidth))

      # Footer
      fid.write("\n)\n")

