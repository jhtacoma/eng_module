import math
#import PyNite.FEModel3D
from PyNite import FEModel3D

def str_to_int (s:str) -> int:
    '''
    Returns an integer if the string 's' represents an integer.
    '''
    ret_value:int = int (s)
    return ret_value


def str_to_float (s:str) -> float:
    '''
    Returns a float if the string 's' represents a floating point number.
    '''
    ret_value:float = float (s)
    return ret_value

def calc_shear_modulus (nu:float, E:float) -> float:
    '''
    Return the shear modulus calculated from 'nu' and 'E'
    '''
    shear_modulus:float = E / (2 * (1 + nu))
    return shear_modulus

def euler_buckling_load (
    l:float, 
    E:float, 
    I:float, 
    k:float
) -> float:
    '''
    Returns the Euler critical load for the column section, calculated from:
    'l' - Representing the braced length (height) of the column
    'E' - Representing the elastic modulus of the column material
    'I' - Representing the moment of inertia of the column section
    'k' - Representing the effective length factor
    '''
    P_cr = math.pi**2 * E * I / (k*l)**2
    return P_cr

def beam_reactions_ss_cant (
    w:float, 
    b:float, 
    a:float
) -> tuple [float, float]:
    '''
    Returns the reactions 'R1' and 'R2' for the simply supported beam with a continuous cantilever on one end.
    R2 is the 'back span' support
    R1 is the 'hammer' support
    '''
    length = b + a
    centroid_of_udl = length / 2
    equiv_point_load = w * length
    R1 = equiv_point_load * centroid_of_udl / b
    R2 = equiv_point_load - R1
    print (R1, R2)
    return -R1, -R2

def fe_model_ss_cant (
    w:float,
    b:float,
    a:float,
    E:float,
    I:float,
    A:float,
    J:float,
    nu:float,
    rho:float = 1.0,

) -> FEModel3D:
    '''
    Returns a PyNite.FEModel3D model of a simply supported beam
    with a cantilever on one end. The beam is loaded with a udl.

    'w' - The magnitude of the distributed load
    'b' - The length of the backspan
    'a' - The length of the cantilever
    'E' - The elastic modulus of the beam material
    'I' - The moment of inertia of the beam section
    'A' - The cross-sectional area of the beam section
    'J' - The polar moment of inertia of the beam section
    'nu' - The Poisson's ratio of the beam material
    'rho' - The density of the beam material   
    '''
    G = calc_shear_modulus (nu, E)
    model = FEModel3D ()
    model.add_material ('default', E, G, nu, rho)
    model.add_node ('N0', 0, 0, 0)
    model.add_node ('N1', b, 0, 0)
    model.add_node ('N2', b+a, 0, 0)
    model.def_support ('N0', True, True, True, True, True, False)
    model.def_support ('N1', False, True, False, False, False, False)
    model.add_member ('M0', 'N0', 'N2', 'default', Iy=1.0, Iz=I, J=J, A=A)
    model.add_member_dist_load ('M0','Fy', w1=w, w2=w)
    return model