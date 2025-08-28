from shapely.geometry import Polygon, LineString, Point
from shapely import affinity
from math import tan, pi, sin
from shapely.ops import split

class Line: 
    def __init__(self, a : float, b : float):
        '''
        Initilization of a Line object to represent a straight line.

        Parameters
        ----------
        a : float
            a is the slope of the line.
        b : float
            b is the crossing of the y-axis -> coordinate (0, b).

        Returns
        -------
        None.

        '''
        
        self.a = a
        self.b = b
        
    def points(self, x : float):
        '''
        Function to return two points on the line with (x, y1) and (-x, y2).
        A larger x value pushes the two points further away from eachother on 
        the line. 

        Parameters
        ----------
        x : float
            x coordinate for the two points. 

        Returns
        -------
        list
            A list with two tuples for each coordinate [(x, y1), (-x, y2)].

        '''
        
        y1 = self.a * x + self.b
        y2 = self.a * (-x) + self.b
        return [(x, y1), (-x, y2)]

def select_polygon(poly):
    '''
    This is a function to select the relevant polygon after a polygon has been 
    sliced in two by a line. The criteria for selection is whether the
    coordinate (1e-5, 1e5) is within the polygon. 

    Parameters
    ----------
    poly : shapely.geometry.polygon.Polygon
        Shapely geometry with multiple polygons.

    Returns
    -------
    geom : shapely.geometry.polygon.Polygon
        DESCRIPTION.

    '''
    for geom in poly.geoms:
        if geom.contains(Point(1e-5, 1e-5)):
            return geom
    return None

def zone_7sa8(ang : float, X : float, R : float, inclination : float, DirMode : str ="Forward"):
    '''
    This functions creates the a Zone Quadrilateral Characteristic Curve for the relay 7SA8.

    Parameters
    ----------
    ang : float
        The distance protection characteristic angle in degrees.
        Addr.: _:2311:107.
    X : float
        Zone reach reactive in ohms.
        Addr.: _:_:102.
    R : float
        Zone reach resistive in ohms.
        Addr.: _:_:103.
    inclination : float
        Zone inclination angle.
        Addr.: _:_:113.
    DirMode : str, optional
        Directional mode. The default is "Forward".
        Addr.: _:_:113.

    Returns
    -------
    TYPE
        Return a shapely Polygon.

    '''
    
    # Check of arguments. Ranges as per the relay manual
    if not(30.0 <= ang <= 90.0):
        raise ValueError('"ang" must be in the range 30 to 90 degree')
        
    if not(0.050 <= X <= 600.0):
        raise ValueError('"X" must be in the range 0.050 to 600 ohms')
    
    if not(0.050 <= R <= 600.0):
        raise ValueError('"R" must be in the range 0.050 to 600 ohms')
    
    if not(0.0 <= inclination <= 45.0):
        raise ValueError('"inclination" must be in the range 0.0 to 45.0 degree')
    
    if DirMode not in ["Forward",
                       "Reverse",
                       "Non-directional"]:
        raise ValueError('"DirMode" must be either "Forward", "Reverse" or "Non-directional"')
    
    
    
    # Concept
    # First the non-directional polygon is created
    # Then the polygon is splitted/sliced by lines cooresponding to the settings
    # E.g. blinders, X reach etc
    # The lines are defined as straight lines with a slope and y-axis crossing
    # or as two points.
    # Then the lines are converted to two points (inf) on the line far away
    # from the polygon.
    # The the polygon is sliced by the lines into two polygons
    # The point (0,0) shifted slightly into 1st quardrant is used to select 
    # the correct polygon.
    
    
    inf = 9999
    
    # As per the relay manual
    DirBlinder1 = 30 # (120 degree) -> in 2nd quadrant
    DirBlinder2 = 22 # (-22 degree) -> in 4th quadrant
    
    # Non-dir polygon
    A = (-R + X / tan(ang/180*pi), X)
    B = (R + X / tan(ang/180*pi) , X)
    C = (R - X / tan(ang/180*pi), -X)
    D = (-R - X / tan(ang/180*pi), -X)
    
    nondir_poly = Polygon([A, B, C, D])
    
    # DirBlinder1 -> in 2nd quadrant
    L1 = Line(-1/tan((DirBlinder1)/180*pi), 0)
    L1p = LineString(L1.points(inf))
    
    # Line connecting DirBlinder1 and line for reactive reach
    L2 = Line(tan(ang/180*pi), tan(ang/180*pi) * R )
    L2p = LineString(L2.points(inf))
    
    # Line for the inclination
    L4 = [(X/(tan(ang/180*pi)), X),
          (1*inf - X/(tan(ang/180*pi)), X + sin(-inclination/180*pi)*inf)]
    
    L4p = LineString(L4)
    
    # Line for the resistive reach R
    L5 = Line(tan(ang/180*pi), -tan(ang/180*pi) * R)
    L5p = LineString(L5.points(inf))
    
    # DirBlinder2 -> in 4th quadrant
    L6 = Line(-tan(DirBlinder2/180*pi), 0)
    L6p = LineString(L6.points(inf))
    
    # Slicing of the non-directional polygon
    result = select_polygon(split(nondir_poly, L1p))
    result = select_polygon(split(result, L2p))
    result = select_polygon(split(result, L4p))
    result = select_polygon(split(result, L5p))
    result = select_polygon(split(result, L6p))
    
    forwardpoly = result

    if DirMode == "Forward":
        return forwardpoly
    
    if DirMode == "Reverse":
        return affinity.rotate(forwardpoly, 180, (0, 0))
    
    if DirMode == "Non-directional":
        return nondir_poly


# Testing

# import matplotlib.pyplot as plt
# # Settings
# ang = 60
# X_reach = 30 #Ohm
# R_ph_g = 52 #Ohm
# R_ph_ph = 52 #Ohm
# inclination = 5 # 0 to 45

# shapePP1 = zone_7sa8(ang, X_reach, R_ph_g, inclination, "Forward")
# shapePP2 = zone_7sa8(ang, X_reach, R_ph_g, inclination, "Reverse")
# shapePP3 = zone_7sa8(ang, X_reach, R_ph_g, inclination, "Non-directional")

# fig, ax = plt.subplots(1, 1)

# poly, = ax.plot(*shapePP1.exterior.xy , '-', color = 'Green')
# poly, = ax.plot(*shapePP2.exterior.xy , '-', color = 'Red')
# poly, = ax.plot(*shapePP3.exterior.xy , '-', color = 'Black')

# ax.set_aspect('equal', adjustable='box')
# plt.show()


## Alternative implementation
# class Line:
#     def __init__(self, a, b):
#         self.a = a
#         self.b = b
#     def points(self, inf):
#         y1 = self.a * inf + self.b
#         y2 = self.a * (-inf) + self.b
#         return [(inf, y1), (-inf, y2)]

# def zone_7sa8(ang : float, X : float, R : float, inclination : float, DirMode : str ="Forward"):
#     '''
#     This functions creates the a Zone Quadrilateral Characteristic Curve for the relay 7SA8.

#     Parameters
#     ----------
#     ang : float
#         The distance protection characteristic angle in degrees.
#         Addr.: _:2311:107.
#     X : float
#         Zone reach reactive in ohms.
#         Addr.: _:_:102.
#     R : float
#         Zone reach resistive in ohms.
#         Addr.: _:_:103.
#     inclination : float
#         Zone inclination angle.
#         Addr.: _:_:113.
#     DirMode : str, optional
#         Directional mode. The default is "Forward".
#         Addr.: _:_:113.

#     Returns
#     -------
#     TYPE
#         Return a shapely Polygon.

#     '''
    
#     # Check of arguments
#     if not(30.0 <= ang <= 90.0):
#         raise ValueError('"ang" must be in the range 30 to 90 degree')
        
#     if not(0.050 <= X <= 600.0):
#         raise ValueError('"X" must be in the range 0.050 to 600 ohms')
    
#     if not(0.050 <= R <= 600.0):
#         raise ValueError('"R" must be in the range 0.050 to 600 ohms')
    
#     if not(0.0 <= inclination <= 45.0):
#         raise ValueError('"inclination" must be in the range 0.0 to 45.0 degree')
    
#     if DirMode not in ["Forward",
#                        "Reverse",
#                        "Non-directional"]:
#         raise ValueError('"DirMode" must be either "Forward", "Reverse" or "Non-directional"')
    
#     inf = 9999
    
#     # As per the manual
#     DirBlinder1 = 30 # (120 degree) -> in 2nd quadrant
#     DirBlinder2 = 22 # (-22 degree) -> in 4th quadrant
    
#     # Auxillary lines
#     # Drawn from the top blinder and clockwise
    
#     # DirBlinder1 -> in 2nd quadrant
#     L1 = Line(-1/tan((DirBlinder1)/180*pi), 0)
    
#     # Line connecting DirBlinder1 and line for reactive reach
#     L2 = Line(tan(ang/180*pi), tan(ang/180*pi) * R )
    
#     # Horizontal line for reactive reach X
#     L3 = Line(0, X)
    
#     # Line for the inclination
#     L4 = [(X/(tan(ang/180*pi)), X),
#           (1*inf - X/(tan(ang/180*pi)), X + sin(-inclination/180*pi)*inf)]
    
#     # Line for the resistive reach R
#     L5 = Line(tan(ang/180*pi), -tan(ang/180*pi) * R)
    
#     # DirBlinder2 -> in 4th quadrant
#     L6 = Line(-tan(DirBlinder2/180*pi), 0)
    
#     L1p = LineString(L1.points(inf))
#     L2p = LineString(L2.points(inf))
#     L3p = LineString(L3.points(inf))
#     L4p = LineString(L4)
#     L5p = LineString(L5.points(inf))
#     L6p = LineString(L6.points(inf))
    
#     p1 = L1p.intersection(L2p)
#     p2 = L2p.intersection(L3p)
#     p3 = L1p.intersection(L3p)
#     p4 = L3p.intersection(L4p)
#     p5 = L4p.intersection(L5p)
#     p6 = L5p.intersection(L6p)
#     p7 = Point((0, 0))
    
#     result = []
    
#     # This logic deals with shape in the 4th quadrant
#     if p3.x > p1.x:
#         result.append(p3)
#     else:
#         result.append(p1)
#         result.append(p2)
    
#     # If inclination is not zero
#     if isinstance(p4, Point):
#         result.append(p4)
        
#     result.append(p5)
#     result.append(p6)
#     result.append(p7)
    
#     if DirMode == "Forward":
#         return Polygon(result)
    
#     if DirMode == "Reverse":
#         return affinity.rotate(Polygon(result), 180, (0, 0))
    
#     if DirMode == "Non-directional":
        
#         A = (-R + X / tan(ang/180*pi), X)
#         B = (R + X / tan(ang/180*pi) , X)
#         C = (R - X / tan(ang/180*pi), -X)
#         D = (-R - X / tan(ang/180*pi), -X)
        
#         return Polygon([A, B, C, D])