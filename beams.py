import csv
import math
#import PyNite.FEModel3D
from PyNite import FEModel3D
#import eng_module.utils as utils
from eng_module.utils import str_to_int, str_to_float, read_csv_file



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

# used to also take A:float=1.0, J:float=1.0, nu:float=1.0, rho:float=1.0
def build_beam (this_beam_data_DICT:dict) -> FEModel3D:
    """
    Returns a beam finite element model for the data in 'this_beam_data_DICT' which is assumed to contain:
    {
        'Name': <name of beam>,
        'L': <length>,
        'E': <elastic modulus of the beam material>,
        'I' or 'Iz' or 'Iy' or 'Iz': <moment of inertia of the beam section>,
        'A' - <cross-sectional area of the beam section>
        'J' - <polar moment of inertia of the beam section>
        'nu' - <Poisson's ratio of the beam material>
        'rho' - <density of the beam material>
        'Supports': <a dict of support locations, from left to right>,
        'Loads': <a list of loads acting on the beam; each load is its own list>        
    }
    """

    L = this_beam_data_DICT ['L']
    E = this_beam_data_DICT ['E']

    if 'I' in this_beam_data_DICT: I = this_beam_data_DICT ['I']
    elif 'Ix' in this_beam_data_DICT: I = this_beam_data_DICT ['Ix']
    elif 'Iy' in this_beam_data_DICT: I = this_beam_data_DICT ['Iy']
    elif 'Iz' in this_beam_data_DICT: I = this_beam_data_DICT ['Iz']
    else: I = 1.0

    A = this_beam_data_DICT ['A']
    J = this_beam_data_DICT ['J']
    nu = this_beam_data_DICT ['nu']
    rho = this_beam_data_DICT ['rho']
    G = calc_shear_modulus (nu, E)


    #nodes_DICT = {} # get_node_locations (L, supports_LIST:list[float]) -> dict [str:float]:
    nodes_DICT = {'N0': 0.0} #define the first node
    supports_DICT = this_beam_data_DICT ['Supports']
    supports_DICT = dict (sorted (supports_DICT.items())) # not sure if this is necessary, but I want to be sure for later assumptions!
    loads_LIST = this_beam_data_DICT ['Loads']

    print (nodes_DICT)
    print (supports_DICT)
    print (loads_LIST)
    # return None
    the_model = FEModel3D ()
    the_model.add_material ('default', E, G, nu, rho)

    count_of_nodes:int = 1
    the_model.add_node ("N0", 0.0, 0, 0) # create the first node

    for support_location, support_type in supports_DICT.items ():
        if support_type == 'P': #pin
            this_DX = True
            this_DY = True
            this_DZ = True
            this_RX = True
            this_RY = True
            this_RZ = False
        elif support_type == 'R':#roller
            this_DX = False
            this_DY = True
            this_DZ = False
            this_RX = False
            this_RY = False
            this_RZ = False
        elif support_type == 'F':#roller
            this_DX = True
            this_DY = True
            this_DZ = True
            this_RX = True
            this_RY = True
            this_RZ = True
        else: # not sure this would ever come up!
            this_DX = False
            this_DY = False
            this_DZ = False
            this_RX = False
            this_RY = False
            this_RZ = False

        if support_location == 0: # at first node
            the_model.def_support ("N0", this_DX, this_DY, this_DZ, this_RX, this_RY, this_RZ)
            # don't increment count_of_nodes; we've already counted this one!
        elif support_location == L: # at last node
            count_of_nodes += 1
            the_model.add_node (f"N{count_of_nodes}", L, 0, 0)
            the_model.def_support (f"N{count_of_nodes}", this_DX, this_DY, this_DZ, this_RX, this_RY, this_RZ)
        else: # at an intermediate location
            count_of_nodes += 1
            print ("about to call!")
            print (f"{count_of_nodes=}")
            print (f"{this_DX=}")
            print (f"{this_DY=}")
            print (f"{this_DZ=}")
            print (f"{this_RX=}")
            print (f"{this_RY=}")
            print (f"{this_RZ=}")
            the_model.add_node (f"N{count_of_nodes}", support_location, 0, 0)
            the_model.def_support (f"N{count_of_nodes}", this_DX, this_DY, this_DZ, this_RX, this_RY, this_RZ)

    #print (the_model.Nodes)

    the_model.add_member ('M0', 'N0', f"N{count_of_nodes}", 'default', Iy=1.0, Iz=I, J=J, A=A)

    for load_DICT in loads_LIST:
        if load_DICT ['Type'] == 'Dist':
            the_model.add_member_dist_load (
                'M0',
                Direction=load_DICT ['Direction'], 
                w1=load_DICT ['Start Magnitude'], 
                w2=load_DICT ['End Magnitude'], 
                x1=load_DICT ['Start Location'], 
                x2=load_DICT ['End Location'])
        elif load_DICT ['Type'] == 'Point':
            the_model.add_member_pt_load (
                'M0',
                Direction=load_DICT ['Direction'], 
                P=load_DICT ['Magnitude'], 
                x=load_DICT ['Location'])
   
    return the_model


def calc_shear_modulus (nu:float, E:float) -> float:
    '''
    Return the shear modulus calculated from 'nu' and 'E'
    '''
    shear_modulus:float = E / (2 * (1 + nu))
    return shear_modulus


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


def get_node_locations (beam_length:float, supports_LIST:list[float]) -> dict [str:float]:
    '''
    Takes the beam's length and a list of all support locations,
    then returns a dictionary of all the resulting nodes.
    '''
    return_DICT = {'N0' : 0.0}
    idx = 1
    for support_location in supports_LIST:
        if support_location > 0 :
            return_DICT.update ({f"N{idx}" : support_location})
        idx+=1
    
    if support_location < beam_length :
        return_DICT.update ({f"N{idx}" : beam_length})
    return return_DICT


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


def get_structured_beam_data (input_LIST:list [list [str]]) -> dict:
    '''
    This converts the file data passed (as a list) into a dictionary and returns that dictionary.
    outer_LIST - the file data already parsed into nested lists

    
    Data in the text file is expected in this format:
    [
        [Beam name],
        [Length,E,Iz,[Iy,A,J,nu,rho]],
        [support_loc:support_type, support_loc:support_type, ...]
        [POINT:load_direction, load_magnitude, load_location, case:load_case]
        [DIST:load_direction, load_start_magnitude, load_end_magnitude, load_start_location, load_end_location, case:load_case]

        * note that each individual item above is a string *
    ]

    ret_dict = {name}
    att_dict = parse_beam_attributes # list[float]
    supports_dict = parse_supports # list[str]
    loads_dict = parse_loads # list[list[str|float]]
    ret_dict = att + supports + loads
    '''

    
    output_DICT:dict = {}
    attributes_LIST  = input_LIST [1]
    supports_LIST  = input_LIST [2]

    # the loads are each on their own line, so we'll concat them into one nested list:
    loads_LIST = []
    this_len = len (input_LIST)
    for i in range (3, this_len):
        loads_LIST.append (input_LIST [i])
    # we convert all the load values, which are currently strings, to floats:
    for load_LIST in loads_LIST:
        for i in range (1, len (load_LIST) - 1):
            load_LIST [i] = str_to_float (load_LIST [i])
        
    for i, val in enumerate (attributes_LIST):
        attributes_LIST [i] = str_to_float (val)
    print (attributes_LIST)
    print (supports_LIST)
    print (loads_LIST)
    

    output_DICT ['Name'] = input_LIST [0][0]
    att_dict = parse_beam_attributes (attributes_LIST) # list[float]
    supports_dict = parse_supports (supports_LIST) # list[str]
    loads_dict = parse_loads (loads_LIST) # list[list[str|float]]
    output_DICT = output_DICT | att_dict #| supports_dict
    output_DICT ['Supports'] = supports_dict
    output_DICT ['Loads'] = loads_dict

    return output_DICT


def load_beam_model (the_filename:str) -> FEModel3D:
    the_beam_data_LIST = read_beam_file (the_filename)
    the_beam_data_DICT = get_structured_beam_data (the_beam_data_LIST)
    the_model = build_beam(the_beam_data_DICT)
    return the_model


def parse_beam_attributes (attributes_LIST:list[float]) -> dict:
    '''
    This takes a list of 3 to 8 attributes (all floats) and returns a dictionary of those items.
    Expected format:
        Length,E,Iz,[Iy,A,J,nu,rho]
        i.e.:
        [4800, 24500, 1200000000] minimum list length
        [20e3, 200e3, 6480e6, 390e6, 43900, 11900e3, 0.3] maximum list length

    '''
    ret_DICT = {
        'L' : str_to_float (attributes_LIST [0]),
        'E' : str_to_float (attributes_LIST [1]),
        'Iz' : str_to_float (attributes_LIST [2]),
        'Iy' : 1,
        'A' : 1,
        'J' : 1,
        'nu' : 1,
        'rho' : 1
    }

    try:
        ret_DICT.update ({"Iy" : attributes_LIST [3]})
    except:
        pass

    try:
        ret_DICT.update ({"A" : attributes_LIST [4]})
    except:
        pass

    try:
        ret_DICT.update ({"J" : attributes_LIST [5]})
    except:
        pass

    try:
        ret_DICT.update ({"nu" : attributes_LIST [6]})
    except:
        pass

    try:
        ret_DICT.update ({"rho" : attributes_LIST [7]})
    except:
        pass

    return ret_DICT


def parse_loads (all_loads_LIST:list[list[str|float]]) -> list [dict]:
    '''
    Turns a messy nested list of strings and floats into a dictionary of load data.
    Params: all_loads_LIST - ie [['POINT:Fy', -10000.0, 4800.0, 'case:Live']]
    Returns: ret_LIST - ie [{"Type": "Point", "Direction": "Fy", "Magnitude": -10000.0, "Location": 4800.0, "Case": "Live"}, ...]
    '''
    ret_LIST = []
    for each_load_LIST in all_loads_LIST: # ie ['POINT:Fy', -10000.0, 4800.0, 'case:Live']
        
        num_data_items = len (each_load_LIST) # either 4 (point load) or 6 (distributed load)
        
        this_load_DICT = {}
        
        this_load_type_LIST = each_load_LIST [0].split (':')
        this_load_type = this_load_type_LIST [0].capitalize()
        this_load_direction = this_load_type_LIST [1]
        
        this_load_DICT ['Type'] = this_load_type
        this_load_DICT ['Direction'] = this_load_direction
        
        ret_LIST.append (this_load_DICT)
        if num_data_items == 4: # point load
            this_load_DICT ['Magnitude'] = str_to_float (each_load_LIST [1])
            this_load_DICT ['Location'] = str_to_float (each_load_LIST [2])
        elif num_data_items == 6: # distributed load
            this_load_DICT ['Start Magnitude'] = str_to_float (each_load_LIST [1])
            this_load_DICT ['End Magnitude'] = str_to_float (each_load_LIST [2])
            this_load_DICT ['Start Location'] = str_to_float (each_load_LIST [3])
            this_load_DICT ['End Location'] = str_to_float (each_load_LIST [4])     
        else:
            print ("UNEXPECTED DATA!")

        this_load_DICT ['Case'] = each_load_LIST [num_data_items - 1].split (':') [1]
            

    return ret_LIST


def parse_supports (supports_LIST:list[str]) -> dict [float, str]:
    '''
    Turns a list of strings into a dictionary of support data.
    Params: supports_LIST - ie ['1000:P', '3800:R', '4800:F', '8000:R']
    Returns: ret_DICT - ie {1000: 'P', 3800: 'R', 4800: 'F', 8000: 'R'}
    '''
    ret_DICT = {}
    for support in supports_LIST:
        temp_LIST = support.split (':')
        support_location = str_to_float (temp_LIST [0])
        support_type = temp_LIST [1]
        ret_DICT [support_location] = support_type
    return ret_DICT


def read_beam_file (the_filename:str) -> list[list[str]]:
    '''
    Takes a filename 'the_filename' as a parameter and reads it from the current working directory.
    Returns a list of beams, where each beam's data is its own list of strings containing the actual data.

    Data in the text file is expected in this format:
        Beam name
        Length,E,Iz,[Iy,A,J,nu,rho]
        support_loc:support_type,support_loc:support_type, ...
        POINT:load_direction,load_magnitude,load_location,case:load_case
        DIST:load_direction,load_start_magnitude,load_end_magnitude,load_start_location,load_end_location,case:load_case
        ... # more loads
    '''
    return read_csv_file (the_filename)
