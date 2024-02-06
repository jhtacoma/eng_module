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

    # PREVIOUS:
    # with open (the_filename) as the_file:
    #    the_file_data = the_file.read () # returns one big long string of every character in the file
    
    with open (the_filename) as the_file:
        the_file_data_LIST = the_file.readlines ()
        the_file_data_LIST = [each_string.replace('\n', '') for each_string in the_file_data_LIST]
    return (the_file_data_LIST)



def separate_lines (the_string: str, the_splitter: str = "\n") -> list:
    '''
    This function splits a string around user-defined points and returns a list of the substrings retrieved.
    'the_string' - the string to be split
    'the_splitter' - the string to be used as a delimiter
    '''
    ret_list = the_string.split (the_splitter)
    return ret_list


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


def build_beam (this_beam_data_DICT:dict, A:float=1.0, J:float=1.0, nu:float=1.0, rho:float=1.0) -> FEModel3D:
    """
    Returns a beam finite element model for the data in 'this_beam_data_DICT' which is assumed to contain:
    {
        'Name': <name of beam>,
        'L': <length>,
        'E': <elastic modulus of the beam material>,
        'I': <moment of inertia of the beam section>,
        'Supports': <a list of support locations, from left to right>,
        'Loads': <a list of loads acting on the beam; each load is its own list>
    }
    
    This function also takes these additional parameters:
    'A' - The cross-sectional area of the beam section
    'J' - The polar moment of inertia of the beam section
    'nu' - The Poisson's ratio of the beam material
    'rho' - The density of the beam material
    """

    L = this_beam_data_DICT ['L']
    E = this_beam_data_DICT ['E']
    I = this_beam_data_DICT ['I']
    G = calc_shear_modulus (nu, E)


    nodes_DICT = {}
    supports_DICT = {}
    for i in range (len(this_beam_data_DICT ['Supports'])):
        nodes_DICT [f"N{i}"] = this_beam_data_DICT ['Supports'][i] # ie {"N0" : 0.0}
        supports_DICT [f"N{i}"] = this_beam_data_DICT ['Supports'][i]

    #THIS NEXT BIT WASN'T REQUIRED, BUT IT BUGGED ME NOT TO PUT IT IN, SINCE I KNOW SOMETHING LIKE IT WILL BE NECESSARY EVENTUALLY...
    if this_beam_data_DICT ['Supports'][i] < L: # if cantilever, and therefore no support at far end, add one more node!
        nodes_DICT [f"N{i+1}"] = L
    
    loads_LIST = []
    for i in range (len(this_beam_data_DICT ['Loads'])):
        loads_LIST.append (this_beam_data_DICT ['Loads'][i])

    # print (nodes_DICT)
    # print (supports_DICT)
    # print (loads_LIST)

    the_model = FEModel3D ()
    the_model.add_material ('default', E, G, nu, rho)

    for node in nodes_DICT.items ():
        the_model.add_node (node [0], node [1], 0, 0)

    # MAKING AN ASSUMPTION HERE, THAT THE FIRST SUPPORT IS A PIN, AND ALL THE REST ARE ROLLERS:
    for support in supports_DICT.items ():
        if support [0] == "N0":
            the_model.def_support (support [0], True, True, True, True, True, False)
        else:
            the_model.def_support (support [0], False, True, False, False, False, False)

    the_model.add_member ('M0', 'N0', f"N{len(nodes_DICT)-1}", 'default', Iy=1.0, Iz=I, J=J, A=A)

    for load in loads_LIST:
        the_model.add_member_dist_load ('M0','Fy', w1=load[0], w2=load[0], x1=load[1], x2=load[2]) #member name, Fy, starting load, ending load
   
    return the_model


def load_beam_model (the_filename:str) -> FEModel3D:
    the_beam_data_LIST = read_beam_file (the_filename)
    the_beam_data_LIST = separate_data (the_beam_data_LIST)
    the_beam_data_DICT = get_structured_beam_data (the_beam_data_LIST)
    the_model = build_beam(the_beam_data_DICT)
    return the_model


def separate_data (the_list:list[str]) -> list [list[str]]:
    '''
    This splits up individual lines of comma-separated data into a nested list, so that
    each comma-separated portion of the string becomes its own item in the sublist that we'll create
    Parameters:
        the_list: the list of text lines retrieved from a file
    '''
    return_LIST = []
    for each_string in the_list:
        temp_LST = []
        temp_LST = separate_lines (each_string, ",")
        temp_LST = [sub.strip() for sub in temp_LST]
        return_LIST.append (temp_LST)

    return return_LIST


def convert_to_numeric (outer_LIST:list [list [str]]) -> list [list[float]]:
    '''
    This takes a list containing lists of string data, converts those string into floats,
    then returns the list.
    '''
    return_LIST = []
    for outer_item_LIST in outer_LIST:
        temp_LST = []
        for inner_item in outer_item_LIST:
            temp_LST.append (str_to_float(inner_item))
        return_LIST.append (temp_LST)
    return return_LIST


def get_structured_beam_data (input_LIST:list [list [str]]) -> dict:
    '''
    This converts the file data passed (as a list) into a dictionary and returns that dictionary.
    outer_LIST - the file data already parsed into nested lists

    
    Data in the text file is expected in this format:
        Length, E, I # Line 0
        Vertical (pin) support locations # Line 1
        UDL Magnitude[, [Load Start], [Load End]] # Line 2
        UDL Magnitude[, [Load Start], [Load End]] # Lines 3+ ...
        ... # etc.
    '''
    numeric_data_LIST = convert_to_numeric (input_LIST[1:])
    output_DICT:dict = {}
    output_DICT ['Name'] = input_LIST [0] [0]
    output_DICT ['L'] = numeric_data_LIST [0] [0]
    output_DICT ['E'] = numeric_data_LIST [0] [1]
    output_DICT ['I'] = numeric_data_LIST [0] [2]
    output_DICT ['Supports'] = numeric_data_LIST [1]
    output_DICT ['Loads'] = numeric_data_LIST [2:]
    return output_DICT


def get_node_locations (support_info_LST:list) -> dict [str:float]:
    return_DICT = {}
    idx = 0
    for node_location in support_info_LST:
        return_DICT [f"N{idx}"] = node_location
        idx+=1
    return return_DICT
