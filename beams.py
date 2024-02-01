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

def euler_buckling_mode (
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


def read_beam_file (the_filename:str) -> str:
    '''
    Takes a filename 'the_filename' as a parameter and reads it from the current working directory.
    Returns a string containing the contents of that file.

    Data in the text file is expected in this format:
        Length, E, I # Line 0
        Vertical (pin) support locations # Line 1
        UDL Magnitude[, [Load Start], [Load End]] # Line 2
        UDL Magnitude[, [Load Start], [Load End]] # Lines 3+ ...
        ... # etc.
    '''
    with open (the_filename) as the_file:
        the_file_data = the_file.read ()
    return (the_file_data)


def separate_lines (the_string: str, the_splitter: str = "\n") -> list:
    '''
    This function splits a string around user-defined points and returns a list of the substrings retrieved.
    'the_string' - the string to be split
    'the_splitter' - the string to be used as a delimiter
    '''
    ret_list = the_string.split (the_splitter)
    return ret_list


def extract_data (the_list:list, the_index:int) -> list: # SHOULD BE CALLED EXTRACT_DATA_FROM_SPECIFIED_LINE
    '''
    This function extracts a particular line of comma-delimited text (an item in the_list)
    and returns it as its own list containing a sublist of that line's individual elements.
    
    Params:
    'the_list' - a list of string data
    'the_index' - the index from where to extract the data from the list (i.e. what line)
    '''
    ret_val = separate_lines (the_list [the_index])
    # The above code returns something like ['4800, 200000, 437000000'] - i.e. a list with only 1 item, but that item is still a comma-delimited string!
    # We must convert that string to its individual elements and append those to our return list, i.e. ['4800', '200000', '437000000'] - a list with 3 items
    temp_str = ret_val [0].replace (', ', ',')
    ret_val = separate_lines (temp_str, the_splitter = ',')
    return (ret_val)


def get_spans (total_beam_length:float, dist_to_cantilever:float) -> tuple [float, float]:
    '''
    Function takes a beam length and cantilever point and returns the backspan length and cantilever length.
    It assumes the backspan starts at the beginning of the beam; therefore it is equal to the cantilever's distance from the start of the beam.
    Arguments:
        'total_beam_length' in mm
        'dist_to_cantilever' in mm
    '''
    b = dist_to_cantilever # backspan
    a = total_beam_length - dist_to_cantilever # span of cantilevered portion
    return (b, a)


def build_beam (this_beam_data:list) -> FEModel3D:
    """
    Returns a beam finite element model for the data in 'beam_data' which is assumed to represent
    a simply supported beam with a cantilever at one end with a uniform distributed load applied
    in the direction of gravity.
    """
    LEI = beams.extract_data(this_beam_data, 0) # get the first line in list form
    L = beams.str_to_float(LEI[0])
    E = beams.str_to_float(LEI[1])
    I = beams.str_to_float(LEI[2])
    #print (LEI)
    pin_locations = beams.extract_data(this_beam_data, 1)
    cant_location = beams.str_to_float (pin_locations [1])
    spans = beams.get_spans (L, cant_location)
    #print (spans)
    
    # Beam 1
    w_1 = beams.str_to_float (beams.extract_data(this_beam_data, 2) [0])
    a_1 = spans [1]
    b_1 = spans [0]
    A = 1
    J = 1
    nu = 1
    the_model = beams.fe_model_ss_cant (w_1, b_1, a_1, E, I, A, J, nu)
    
    return the_model


def load_beam_model (the_filename:str) -> FEModel3D:
    the_beam_data_STR = beams.read_beam_file (the_filename)
    the_beam_data_LS = beams.separate_lines (the_beam_data_STR)
    the_model = build_beam(the_beam_data_LS)
    return the_model