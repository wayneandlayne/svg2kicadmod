SVG to Kicad PCB Module converter
=================================

Written by Matthew Beckler and Adam Wolf, of Wayne and Layne, LLC
TODO figure out licensing
Released under the terms of the GPLv2 or whatever is required by the library code

This script reads an SVG file and attempts to convert all the objects into
Kicad PCBNEW module files for inclusion as either silkscreen or copper or
soldermask artwork in a printed circuit board.

Only supports the latest .kicad_mod file format.
Try converting your SVG objects to path first to improve results.
Doesn't properly handle overly complex shapes that have lots of holes and stuff,
so you might have to introduce tiny cuts in your holey objects to connect the
outside region to the region inside (such as the hole in the letter A).

SvgParser is the code to parse an SVG file and flatten all the transformation
hierarchy to return a set of raw objects like (fill=True/False, [(x0, y0), (x1, y1), ...]).
Also includes methods to center some raw objects, and also to scale raw objects.

KicadPcbnewModuleWriter is the code to take those raw objects and write them
to a Kicad PCBNEW module file (new format).

