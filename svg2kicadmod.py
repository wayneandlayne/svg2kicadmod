# TODO comments, license

import sys
import math

from SvgParser import SvgParser

from KicadPcbnewModuleWriter import writeRawObjectsToKicadPcbnewModuleFile


def usageAndExit():
   print """Usage: %s input output layer [width [height]]
Notes: input and output are filenames
       layer is a string like "F.SilkS" or TODO
       width and height are dimensions in mm.
          If you specify a non-zero width, scale the output to match that width.
          If you specify a zero width and non-zero height, scale the output to match that height.
          If both width and height are non-zero, scale the output to be no larger than either.
          If neither are specified or both zero, no scaling is performed, and YMMV.
          """ % sys.argv[0]
   sys.exit(1)

if __name__ == "__main__":

   # TODO make this properly parse the command line options
   # TODO what about flipping the y coordinate? Isn't inkscape upside down from kicad?
   # TODO add options for the module name and line width
   if len(sys.argv) < 4:
      usageAndExit()

   filename = sys.argv[1]
   output = sys.argv[2]
   layer = sys.argv[3]

   width_mm = 0.0
   height_mm = 0.0
   try:
      if len(sys.argv) >= 5:
         width_mm = float(sys.argv[4])
      if len(sys.argv) == 6:
         height_mm = float(sys.argv[5])
   except:
      print "Width and height must be specified as floats or ints."
      usageAndExit()


   sd = SvgParser(filename)
   sd.recursivelyTraverseSvg()
   print "Stats - min: (%f, %f), center: (%f, %f), max: (%f, %f)" % sd.findMinCenterMaxOfObjects(sd.rawObjects)
   print "Centering drawing about (0, 0)..."
   sd.alignObjects(horizAlign=SvgParser.ALIGN_CENTER, vertAlign=SvgParser.ALIGN_CENTER)
   print "Stats - min: (%f, %f), center: (%f, %f), max: (%f, %f)" % sd.findMinCenterMaxOfObjects(sd.rawObjects)

   # Now we need to use the provided width and height to scale the drawing
   xmin, ymin, xcenter, ycenter, xmax, ymax = sd.findMinCenterMaxOfObjects(sd.rawObjects)
   width = xmax - xmin
   height = ymax - ymin
   if width_mm == 0.0 and height_mm == 0.0:
      # Neither defined, scale = 1
      scale = 1.0
   elif width_mm == 0.0:
      # Just use the height
      scale = height_mm / height
   elif height_mm == 0.0:
      # Just use the width
      scale = width_mm / width
   else:
      # Use both, but keep the final size within width x height.
      # Which means, compute both scale factors, and use the smaller of the two.
      scale_height = height_mm / height
      scale_width = width_mm / width
      scale = min(scale_height, scale_width)

   if scale != 1.0:
      print "Scaling by %f" % scale
      sd.scaleRawObjects(scale)
      print "Stats - min: (%f, %f), center: (%f, %f), max: (%f, %f)" % sd.findMinCenterMaxOfObjects(sd.rawObjects)

   writeRawObjectsToKicadPcbnewModuleFile(output, sd.rawObjects, name="TestModule", layer=layer, lineWidth=0.01)

   #for fill, points in sd.rawObjects:
      #print "Filled object" if fill else "Unfilled object"
      #print "\n".join(["%f, %f" % (n[0], n[1]) for n in points])

