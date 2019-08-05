'''
Created on 7 Jul 2019

@author: petrileskinen, petri.leskinen@icloud.com

'''

from collections import Counter
from math import sqrt
import numpy as np
import os
import re


MINDIST = 16
STLFILENAME = "model.stl"

def main():
    imgfilename = "bitmap.png"
    distfilename = "tmp_dist.txt"
    skelfilename = "tmp_skel.txt"
    
    params = ' '.join(['bash',
                   'makeDistanceImage.bash',
                   imgfilename,
                   distfilename,
                   skelfilename
                   ])
    
    print("Calculating distance transformations")
    os.system(params)
    
    #    convert -define profile:skip=ICC en.png -negate -morphology Distance Euclidean:4 -auto-level en_dist.png
    #    convert -define profile:skip=ICC en.png -negate -morphology Thinning:-1 Skeleton -auto-level en_skel.png
    
    print("Reading point set")
    
    pointset={}
    xmax = 0 
    ymax = 0
    dmax = 0
    with open(distfilename, 'r') as infile:
        for row in infile:
            m=re.match(r'(?P<x>\d+),(?P<y>\d+): \((?P<pxl>\d+)', row)
            if m is not None:
                pxl = int(m.groupdict()['pxl'])
                if pxl > MINDIST:
                    # if pxl<0.25: pxl=0
                    
                    x = int(m.groupdict()['x'])
                    y = int(m.groupdict()['y'])
                    
                    pointset[(x,y)] = Point(x,-y,pxl)
                    if x>xmax: xmax=x
                    if y>ymax: ymax=y
                    if pxl>dmax: dmax=pxl
    
    print("Maximum distance {}".format(dmax))
    
    with open(skelfilename, 'r') as infile:
        for row in infile:
            m=re.match(r'(?P<x>\d+),(?P<y>\d+): \((?P<pxl>\d+)', row)
            if m is not None:
                
                x = int(m.groupdict()['x'])
                y = int(m.groupdict()['y'])
                
                if (x,y) in pointset:
                    r = pointset[(x,y)].z
                    r2 = int(m.groupdict()['pxl'])
                    
                    #    calculate z level based knowing the distance to the edge and to the center line
                    d = (dmax+2*(r+r2))/3.0
                    
                    z2 = d*sqrt(1.0-r2*r2/((r+r2)**2))
                    pointset[(x,y)].z = z2/90.5
                    
                    
    
    
    print("Forming triangles")

    tri = []
    for y in range(ymax):
        for x in range(xmax):
            
            c0 = (x,y) in pointset 
            c1 = (x+1,y) in pointset 
            c2 = (x,y+1) in pointset 
            c3 = (x+1,y+1) in pointset
            
            if c0+c1+c2+c3<3:
                continue
            
            p0 = pointset[(x,y)] if c0 else None
            p1 = pointset[(x+1,y)] if c1 else None
            p2 = pointset[(x,y+1)] if c2 else None
            p3 = pointset[(x+1,y+1)] if c3 else None
            
            if c0+c1+c2+c3==4:
                #    p0,p2,p3,p1
                addTriangs(p0, p1, p2, p3, tri)
            
            elif c0==False:
                tri.append(Triangle(p2,p3,p1))
            elif c1==False:
                tri.append(Triangle(p0,p2,p3))
            elif c2==False:
                tri.append(Triangle(p0,p3,p1))
            elif c3==False:
                tri.append(Triangle(p0,p2,p1))
    
    
    print("Detecting edges")
    edges = []
    for tr in tri:
        edges += tr.edges()
    c = Counter(edges)
    #    The contour is formed by the edges appearing only once in the total shape
    edges = [key for key,count in c.items() if count==1]
    
    print("Added bottom triangles")
    triR = []
    for tr in tri:
        addReverseTriang(tr,triR)
        
    tri += triR
    
    print("Added edge triangles")
    for e in edges:
        addEdgeTriangs(e.start, e.end, tri)
    
    #    flatten the bottom of the model
    ZMIN = -7.50
    for tr in tri:
        if tr.p0.z<ZMIN: tr.p0.z=ZMIN
        if tr.p1.z<ZMIN: tr.p1.z=ZMIN
        if tr.p2.z<ZMIN: tr.p2.z=ZMIN
    
    #    write output file
    writeSTL(STLFILENAME, "textmodel", tri)
    
    
def addReverseTriang(tr,tri):
    p0 = tr.p0.copy()
    p0.z = -p0.z
    p1 = tr.p1.copy()
    p1.z = -p1.z
    p2 = tr.p2.copy()
    p2.z = -p2.z
    
    tri.append(Triangle(p0,p2,p1))
    
def addTriangs(p0,p1,p2,p3, tri):
    #    Adds a square as two triangles
    #    Two possible divisions:
    trA0 = Triangle(p2,p1,p0)
    trA1 = Triangle(p2,p3,p1)
    
    trB0 = Triangle(p0,p2,p3)
    trB1 = Triangle(p0,p3,p1)
    
    #    Choose the division with a smaller total area:
    if trA0.area()+trA1.area() < trB0.area()+trB1.area():
        tri.append(trA0)
        tri.append(trA1)
    else:
        tri.append(trB0)
        tri.append(trB1)
    
    
def addEdgeTriangs(start,end, tri):
    s2 = start.copy()
    s2.z = -s2.z
    e2 = end.copy()
    e2.z = -e2.z
    tri.append(Triangle(end, start, e2))
    tri.append(Triangle(start, s2, e2))
    

def writeSTL(outfilename, label, tri):
    outfile = open(outfilename,"w") 
    outfile.write("solid {}\n".format(label))
    
    for tr in tri:
        v = tr.normal()
        for st in ["facet normal {} {} {}".format(v.x, v.y, v.z),
                   "outer loop",
                   "vertex {} {} {}".format(tr.p0.x, tr.p0.y, tr.p0.z),
                   "vertex {} {} {}".format(tr.p1.x, tr.p1.y, tr.p1.z),
                   "vertex {} {} {}".format(tr.p2.x, tr.p2.y, tr.p2.z),
                   "endloop",
                   "endfacet"
                   ]:
            outfile.write(st+"\n")
    outfile.write("endsolid {}\n".format(label))
    outfile.close() 
    print("Results written to {}".format(outfilename))
    

class Point:
    def __init__(self, x,y,z):
        self.x = x
        self.y = y
        self.z = z
    
    def key(self):
        return self.__key()
    
    def __key(self):
        return (self.x, self.y, self.z)
    
    def copy(self):
        return self.__copy__()
    
    def __copy__(self):
        return Point(self.x, self.y, self.z)
    
    def __add__(self, other):
        return Point(self.x+other.x, self.y+other.y, self.z+other.z)
    
    def __sub__(self, other):
        return Point(self.x-other.x, self.y-other.y, self.z-other.z)
    
    def __truediv__(self, other):
        return Point(self.x/other, self.y/other, self.z/other)
    
    
    def __repr__(self):
        return "Point({:.5f}, {:.5f}, {:.5f})".format(self.x, self.y, self.z)
    
    def __str__(self):
        return self.__repr__()
    
    def __hash__(self):
        return hash(self.__key())
    
    
    def __eq__(self, other):
        if isinstance(other, Point):
            return self.__key() == other.__key()
        return NotImplemented
    
class Edge:
    def __init__(self, start, end):
        self.start = start 
        self.end = end 
        
    def __hash__(self):
        h1 = hash(self.start)
        h2 = hash(self.end)
        if h1<h2:
            return hash((h1,h2))
        else:
            return hash((h2,h1))
    
    def __repr__(self):
        p1 = self.start.__repr__()
        p2 = self.end.__repr__()
        return "Edge({},{})".format(p1,p2)
    
    def __str__(self):
        return self.__repr__()
        
    def __eq__(self, other):
        if isinstance(other, Edge):
            return (self.start == other.start and self.end == other.end) or \
                (self.start == other.end and self.end == other.start)
        return NotImplemented
    
class Triangle():
    def __init__(self, p0,p1,p2):
        self.p0 = p0
        self.p1 = p1
        self.p2 = p2
    
    def edges(self):
        return [Edge(self.p0, self.p1), 
                Edge(self.p1, self.p2), 
                Edge(self.p2, self.p0)]
    
    def area(self):
        a = self.p1-self.p0
        b = self.p2-self.p0
        
        v = np.cross(a.key(), b.key())
        return 0.5 * np.linalg.norm(v)
        
    
    def normal(self):
        a = self.p1-self.p0
        b = self.p2-self.p0
        
        v = np.cross(a.key(), b.key())
        norm = np.linalg.norm(v)
        
        v = Point(v[0], v[1], v[2])
        if norm == 0:
            return v
        return v / norm
        
    def __repr__(self):
        return "Triangle({}, {}, {})".format(self.p0,self.p1,self.p2)
    
if __name__ == '__main__':
    main()