from shapely.geometry import Polygon
from math import tan, pi
from shapely import affinity

def start_REL670(X1, R1, RF, Rrev):
    A_pp_x = - Rrev/2
    A_pp_y = 0
    B_pp_x = - Rrev/2
    B_pp_y = X1 
    
    C_pp_x = R1 + RF/2
    C_pp_y = X1 
    D_pp_x = RF/2
    D_pp_y = 0
    E_pp_x = RF/2
    E_pp_y = - X1
    F_pp_x = - R1
    F_pp_y = - X1
    
    pointsPP = []
    pointsPP.append((A_pp_x, A_pp_y))
    pointsPP.append((B_pp_x, B_pp_y))
    pointsPP.append((C_pp_x, C_pp_y))
    pointsPP.append((D_pp_x, D_pp_y))
    pointsPP.append((E_pp_x, E_pp_y))
    pointsPP.append((F_pp_x, F_pp_y))
    
    shapePP = Polygon(pointsPP)
    return shapePP

def zone_ph_REL670(AngDir, AngNegRes, DirModeZx, X1Zx, R1Zx, RFPPZx):
    # Phase-Phase points
    # Origon is A, B is the next point clockwise and so fort
    
    pointsPP = [(0, 0)]

    B_pp_x = - RFPPZx / 2
    B_pp_y = (RFPPZx / 2) / tan((AngNegRes - 90)/180*pi)

    C_pp_x = - RFPPZx / 2
    C_pp_y = X1Zx

    if C_pp_y < B_pp_y:
        # Remove point B and re-calculate C
        C_pp_x = - X1Zx / tan( (180 - AngNegRes)/180*pi )
        B_pp_x = None
        B_pp_y = None

    D_pp_x = R1Zx + RFPPZx / 2
    D_pp_y = X1Zx
    E_pp_x = RFPPZx / 2
    E_pp_y = 0
    F_pp_x = RFPPZx / 2
    F_pp_y = (RFPPZx / 2) * tan(-AngDir/180*pi)

    if B_pp_x:
        pointsPP.append((B_pp_x, B_pp_y))
    pointsPP.append((C_pp_x, C_pp_y))
    pointsPP.append((D_pp_x, D_pp_y))
    pointsPP.append((E_pp_x, E_pp_y))
    pointsPP.append((F_pp_x, F_pp_y))
    shapePP = Polygon(pointsPP)

    if DirModeZx == 'Reverse':
        # Rotating polygon 180 degrees around 0,0
        shapePP = affinity.rotate(shapePP, 180, (0, 0))
    
    if DirModeZx == 'Non-directional':
        #Not tested
        A_pp_x = - RFPPZx/2
        A_pp_y = 0
        
        B_pp_x = - RFPPZx/2
        B_pp_y = X1Zx 

        C_pp_x = R1Zx + RFPPZx/2
        C_pp_y = X1Zx 
        
        D_pp_x = RFPPZx
        D_pp_y = 0
        
        E_pp_x = RFPPZx
        E_pp_y = - X1Zx
        
        F_pp_x = - RFPPZx/2 - R1Zx
        F_pp_y = - X1Zx

        pointsPP_2 = []
        pointsPP_2.append((A_pp_x, A_pp_y))
        pointsPP_2.append((B_pp_x, B_pp_y))
        pointsPP_2.append((C_pp_x, C_pp_y))
        pointsPP_2.append((D_pp_x, D_pp_y))
        pointsPP_2.append((E_pp_x, E_pp_y))
        pointsPP_2.append((F_pp_x, F_pp_y))

        shapePP = Polygon(pointsPP_2)

    return shapePP

def zone_pe_REL670(AngDir, AngNegRes, DirModeZx, X1Zx, R1Zx, X0Zx, R0Zx, RFPEZx):
    zone_pe = zone_ph_REL670(AngDir = AngDir,
                         AngNegRes = AngNegRes,
                         DirModeZx = DirModeZx,
                         X1Zx = X1Zx + X0Zx,
                         R1Zx = R1Zx + R0Zx,
                         RFPPZx = RFPEZx * 2)
    return zone_pe


