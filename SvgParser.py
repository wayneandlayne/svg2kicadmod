# TODO comments, license

import sys
from lxml import etree

# Inkscape extension code (GPL2)
import simpletransform
import simplestyle
import simplepath
import cubicsuperpath
import cspsubdiv


class SvgParser:
   """ This class has nothing to do with any specific output format.
       It simply parses an SVG file and returns a list of raw objects,
       which are like (fill=True/False, [points]), where points is a
       list of (x, y) coordinate pairs.
       
       Smoothness influences the linearization process.
       
       Some of this code is heavily based on the Egg-Bot Inkscape extension code.
       TODO what is their license?
   """

   # Alignment constants
   ALIGN_CENTER = 0
   ALIGN_TOP = 1
   ALIGN_BOTTOM = 2
   ALIGN_LEFT = 3
   ALIGN_RIGHT = 4


   # How many of a given unit equal one pixel?
   # Not currently used for scaling, but only for detecting valid units
   svgUnitsTable = {"px": 1.0,
                    "pt": 1.25,
                    "pc": 15,
                    "mm": 3.543307,
                    "cm": 35.43307,
                    "in": 90.0}

   def __init__(self, filename, smoothness=0.1):
      self.smoothness = smoothness
      with open(filename, "r") as fid:
         self.tree = etree.parse(fid)
      self.svgRoot = self.tree.getroot()
      self.nsmap = self.svgRoot.nsmap
      self.rawObjects = [] # An object = (fill=True/False, [(x,y),...])


   def svgQName(self, foo):
      return etree.QName(self.nsmap["svg"], foo)


   def findMinCenterMaxOfObjects(self, objects):
      """ Analyses all the raw objects to determine the min, center, and max of all coordinates. """
      xmin = xmax = ymin = ymax = None
      for fill, points in objects:
         for x, y in points:
            #print x, y
            if not xmin or x < xmin:
               xmin = x
            if not xmax or x > xmax:
               xmax = x
            if not ymin or y < ymin:
               ymin = y
            if not ymax or y > ymax:
               ymax = y
      xcenter = (xmax + xmin) / 2
      ycenter = (ymax + ymin) / 2
      return xmin, ymin, xcenter, ycenter, xmax, ymax

   def alignObjects(self, horizAlign=ALIGN_CENTER, vertAlign=ALIGN_CENTER):
      """ Analyzes all the objects in self.rawObjects, and aligns them based on the input options (LEFT/CENTER/RIGHT and TOP/CENTER/BOTTOM). """
      xmin, ymin, xcenter, ycenter, xmax, ymax = self.findMinCenterMaxOfObjects(self.rawObjects)

      xsub = xcenter
      if horizAlign == self.ALIGN_LEFT:
         xsub = xmin
      elif horizAlign == self.ALIGN_RIGHT:
         xsub = xmax

      ysub = ycenter
      if vertAlign == self.ALIGN_BOTTOM:
         ysub = ymin
      elif vertAlign == self.ALIGN_TOP:
         ysub = ymax

      #print "xsub: %f, ysub: %f" % (xsub, ysub)

      # update coordinates of each object
      newRawObjects = []
      for fill, points in self.rawObjects:
         newPoints = [(x - xsub, y - ysub) for x, y in points]
         newRawObjects.append( (fill, newPoints) )
      self.rawObjects = newRawObjects


   def scaleRawObjects(self, scale):
      """ CALL THIS AFTER centerAroundZeroZero SO THAT IT WORKS RIGHT. This multiplies each coordinate by scale. """
      newRawObjects = []
      for fill, points in self.rawObjects:
         newPoints = [(x * scale, y * scale) for x, y in points]
         newRawObjects.append( (fill, newPoints) )

      self.rawObjects = newRawObjects


   def plotPath(self, node, matTransform):
      """ Plot the path while applying the transformation defined by the matrix matTransform. """

      filledPath = (simplestyle.parseStyle(node.get("style")).get("fill", "none") != "none")

      # Plan: Turn this path into a cubicsuperpath (list of beziers)...
      d = node.get("d")
      if len(simplepath.parsePath(d)) == 0:
         return
      p = cubicsuperpath.parsePath(d)

      # ... and apply the transformation to each point.
      simpletransform.applyTransformToPath(matTransform, p)

      # p is now a list of lists of cubic beziers [cp1, cp2, endp]
      # where the start-point is the last point of the previous segment.
      # For some reason the inkscape extensions uses csp[1] as the coordinates of each point,
      # but that makes it seem like they are using control point 2 as line points.
      # Maybe that is a side-effect of the CSP subdivion process? TODO
      realPoints = []
      for sp in p:
         cspsubdiv.subdiv(sp, self.smoothness)
         for csp in sp:
            realPoints.append( (csp[1][0], csp[1][1]) )

      self.rawObjects.append( (filledPath, realPoints) )



   def parseLengthAndUnits(self, string):
      """ Parses string to discover units. Returns (value, units).
          Currently only used to parse SVG root width/height values. """
      s = string.strip()
      u = "px" # by default, if no explicit "px" in string
      if s[-2:] in self.svgUnitsTable.keys():
         u = s[-2:]
         s = s[:-2]

      try:
         v = float(s)
         return v, u
      except:
         pass

      return None, None



   def recursivelyTraverseSvg(self, nodeList=None, matCurrent=[[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]], parent_visibility='visible' ):
      """ Based on the Eggbot extension for Inkscape.
      Recursively traverse the svg file to plot out all the paths. Keeps track of the composite transformation that should be applied to each path.

      Handles path, group.
      Doesn't yet handle line, text, rect, polyline, polygon, circle, ellipse and use (clone) elements.
      Unhandled elements should be converted to paths in Inkscape.
      Probably want to avoid paths with holes inside.
      """

      if not nodeList:
         nodeList = self.svgRoot

         # get svg document width and height
         width, units_width = self.parseLengthAndUnits(nodeList.get("width"))
         height, units_height = self.parseLengthAndUnits(nodeList.get("height"))
         if units_width != units_height:
            print "Weird, units for SVG root document width and height differ..."
            print nodeList.get("width")
            print nodelist.get("height")
            sys.exit(1)

         # set initial viewbox from document root
         viewbox = nodeList.get("viewBox")
         print "Document size: %f x %f (%s)" % (width, height, units_width)
         if viewbox:
            vinfo = viewbox.strip().replace(',', ' ').split(' ')
            if (vinfo[2] != 0) and (vinfo[3] != 0):
               sx = width / float(vinfo[2])
               sy = height / float(vinfo[3])
               matCurrent = simpletransform.parseTransform("scale(%f, %f) translate(%f, %f)" % (sx, sy, -float(vinfo[0]), -float(vinfo[1])))

      print "Initial transformation matrix:", matCurrent


      for node in nodeList:

         # Ignore invisible nodes
         v = node.get('visibility', parent_visibility)
         if v == 'inherit':
            v = parent_visibility
         if v == 'hidden' or v == 'collapse':
            pass

         # first apply the current matrix transform to this node's transform
         matNew = simpletransform.composeTransform( matCurrent, simpletransform.parseTransform(node.get("transform")) )

         if node.tag in [self.svgQName("g"), "g"]:
            print "group tag - Might not be handled right!"
            self.recursivelyTraverseSvg( list(node), matNew, v )

         elif node.tag in [self.svgQName("path")]:
            self.plotPath( node, matNew )

         else:
            print "Other tag: '%s'" % node.tag


