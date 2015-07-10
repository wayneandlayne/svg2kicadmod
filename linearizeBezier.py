
# Linearizes cubic bezier curve
# Two end points and two control points
# Using the de Castejau subdivision, per usual
# Based on http://hcklbrrfnn.files.wordpress.com/2012/08/bez.pdf


import math
from collections import namedtuple

Point = namedtuple("Point", "x, y")
CubicBezier = namedtuple("CubicBezier", "p0, p1, p2, p3")

def midpoint(p0, p1, t=0.5):
   """ Returns a point that is (100*t)% of the way from p0 to p1, defaulting to 50% (true midpoint). """
   return Point( (p0.x + p1.x) / 2.0, (p0.y + p1.y) / 2.0)
   #return Point( p0.x + t * (p1.x - p0.x), p0.y + t * (p1.y - p0.y) ) # TODO test this form

def subdivide(curve, t=0.5):
   """ Divides curve into two cubic beziers that combine to form the original curve.
       Returns (left, right) curves.
       You can also specify a value for t to indicate where to split. Defaults to t=0.5. """
   m = midpoint(curve.p1, curve.p2, t)
   l0 = curve.p0
   r3 = curve.p3
   l1 = midpoint(curve.p0, curve.p1)
   r2 = midpoint(curve.p2, curve.p3)
   l2 = midpoint(l1, m)
   r1 = midpoint(m, r2)
   l3 = r0 = midpoint(l2, r1)
   left = CubicBezier(l0, l1, l2, l3)
   right = CubicBezier(r0, r1, r2, r3)
   
   return left, right

def flatEnough(curve, tolerance):
   """ Evaluates if a cubic bezier is flat enough. Returns True or False. From the link above. """
   ux = math.pow(3.0 * curve.p1.x - 2.0 * curve.p0.x - curve.p3.x, 2)
   uy = math.pow(3.0 * curve.p1.y - 2.0 * curve.p0.y - curve.p3.y, 2)
   vx = math.pow(3.0 * curve.p2.x - 2.0 * curve.p3.x - curve.p0.x, 2)
   vy = math.pow(3.0 * curve.p2.y - 2.0 * curve.p3.y - curve.p0.y, 2)
   if ux < vx:
      ux = vx
   if uy < vy:
      uy = vy
   return (ux + uy <= tolerance) # tolerance is 16*tol^2 - WTF?

def linearize(curve, tolerance):
   """ Linearizes cubic bezier from p0 to p3 with control points p1 and p2, to specified tolerance.
       Returns a list of flat-enough cubic beziers. """
   
   if flatEnough(curve, tolerance):
      return [curve] # need to return a list to iterate over

   # Split the curve and recurse - For now let's just split at t=0.5 (TODO heuristic to pick better t?)
   curves = []
   left, right = subdivide(curve)
   curves.extend(linearize(left, tolerance))
   curves.extend(linearize(right, tolerance))
   return curves

def simplifyCurves(curves):
   """ Converts a list of linearized cubic beziers into a simple list of Point objects. """
   points = []
   points.append(curves[0].p0)
   for curve in curves:
      points.append(curve.p3)
   return points

def elevateQuadraticToCubic(q0, q1, q2):
   """ Elevates a quadratic bezier curve to be a cubic bezier curve.
       No loss of accuracy, but it's not reversable. """
   
   # Endpoints are the same
   p0 = q0
   p3 = q2

   # From http://pomax.github.io/bezierinfo/
   # "If we have a curve with three points, then we can create a four point curve that exactly reproduce
   # the original curve as long as we give it the same start and end points, and for its two control
   # points we pick "1/3rd start + 2/3rd control" and "2/3rd control + 1/3rd end", and now we have
   # exactly the same curve as before, except represented as a cubic curve, rather than a quadratic curve."
   p1 = midpoint(q0, q1, 0.66666666)
   p2 = midpoint(q1, q2, 0.33333333)

   return CubicBezier(p0, p1, p2, p3)


if __name__ == "__main__":
   cb = CubicBezier(Point(0, 0), Point(0, 2), Point(1, -1), Point(1, 1))
   print "Linearizing curve:", cb
   
   tolerance = 0.0001
   print "Tolerance:", tolerance

   curves = linearize(cb, tolerance)
   print "Linearized into %d curves:" % len(curves)
   for curve in curves:
      print curve

   print "Just end points:"
   for curve in curves:
      print "{}, {}, {}, {}".format(curve.p0.x, curve.p0.y, curve.p3.x, curve.p3.y)

   print "Suitable for spreadsheet plotting:"
   print "{}".format(curves[0].p0.x)
   for curve in curves:
      print "{}".format(curve.p3.x)
   print "--------------"
   print "{}".format(curves[0].p0.y)
   for curve in curves:
      print "{}".format(curve.p3.y)

   print simplifyCurves(curves)
