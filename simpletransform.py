#!/usr/bin/env python
'''
Copyright (C) 2006 Jean-Francois Barraud, barraud@math.univ-lille1.fr
Copyright (C) 2010 Alvin Penner, penner@vaxxine.com

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
barraud@math.univ-lille1.fr

This code defines several functions to make handling of transform
attribute easier.
'''
import math, re

def parseTransform(transf,mat=[[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]):
    if transf=="" or transf==None:
        return(mat)
    stransf = transf.strip()
    result=re.match("(translate|scale|rotate|skewX|skewY|matrix)\s*\(([^)]*)\)\s*,?",stransf)
#-- translate --
    if result.group(1)=="translate":
        args=result.group(2).replace(',',' ').split()
        dx=float(args[0])
        if len(args)==1:
            dy=0.0
        else:
            dy=float(args[1])
        matrix=[[1,0,dx],[0,1,dy]]
#-- scale --
    if result.group(1)=="scale":
        args=result.group(2).replace(',',' ').split()
        sx=float(args[0])
        if len(args)==1:
            sy=sx
        else:
            sy=float(args[1])
        matrix=[[sx,0,0],[0,sy,0]]
#-- rotate --
    if result.group(1)=="rotate":
        args=result.group(2).replace(',',' ').split()
        a=float(args[0])*math.pi/180
        if len(args)==1:
            cx,cy=(0.0,0.0)
        else:
            cx,cy=map(float,args[1:])
        matrix=[[math.cos(a),-math.sin(a),cx],[math.sin(a),math.cos(a),cy]]
        matrix=composeTransform(matrix,[[1,0,-cx],[0,1,-cy]])
#-- skewX --
    if result.group(1)=="skewX":
        a=float(result.group(2))*math.pi/180
        matrix=[[1,math.tan(a),0],[0,1,0]]
#-- skewY --
    if result.group(1)=="skewY":
        a=float(result.group(2))*math.pi/180
        matrix=[[1,0,0],[math.tan(a),1,0]]
#-- matrix --
    if result.group(1)=="matrix":
        a11,a21,a12,a22,v1,v2=result.group(2).replace(',',' ').split()
        matrix=[[float(a11),float(a12),float(v1)], [float(a21),float(a22),float(v2)]]

    matrix=composeTransform(mat,matrix)
    if result.end() < len(stransf):
        return(parseTransform(stransf[result.end():], matrix))
    else:
        return matrix

def formatTransform(mat):
    return ("matrix(%f,%f,%f,%f,%f,%f)" % (mat[0][0], mat[1][0], mat[0][1], mat[1][1], mat[0][2], mat[1][2]))

def composeTransform(M1,M2):
    a11 = M1[0][0]*M2[0][0] + M1[0][1]*M2[1][0]
    a12 = M1[0][0]*M2[0][1] + M1[0][1]*M2[1][1]
    a21 = M1[1][0]*M2[0][0] + M1[1][1]*M2[1][0]
    a22 = M1[1][0]*M2[0][1] + M1[1][1]*M2[1][1]

    v1 = M1[0][0]*M2[0][2] + M1[0][1]*M2[1][2] + M1[0][2]
    v2 = M1[1][0]*M2[0][2] + M1[1][1]*M2[1][2] + M1[1][2]
    return [[a11,a12,v1],[a21,a22,v2]]

def applyTransformToNode(mat,node):
    m=parseTransform(node.get("transform"))
    newtransf=formatTransform(composeTransform(mat,m))
    node.set("transform", newtransf)

def applyTransformToPoint(mat,pt):
    x = mat[0][0]*pt[0] + mat[0][1]*pt[1] + mat[0][2]
    y = mat[1][0]*pt[0] + mat[1][1]*pt[1] + mat[1][2]
    pt[0]=x
    pt[1]=y

def applyTransformToPath(mat,path):
    for comp in path:
        for ctl in comp:
            for pt in ctl:
                applyTransformToPoint(mat,pt)

