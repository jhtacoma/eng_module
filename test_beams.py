import math
import eng_module.beams as beams
from importlib import reload
reload (beams)


def test_calc_shear_modulus ():
    E_1 = 200_000
    nu_1 = 0.3
    E_2 = 3645
    nu_2 = 0.2 
    assert beams.calc_shear_modulus (nu_1, E_1) == 76923.07692307692
    assert beams.calc_shear_modulus (nu_2, E_2) == 1518.75
   

def test_euler_buckling_mode ():
    # Column 1 - Value will be in Newtons
    l_1 = 5300 # mm
    E_1 = 200000 # MPa
    I_1 = 632e6 # mm**4
    k_1 = 1.0

    # Column 2 - Value will be in kips ("kips" == "kilopound" == 1000 lbs)
    l_2 = 212 # inch
    E_2 = 3645 # ksi ("ksi" == "kips per square inch")
    I_2 = 5125.4 # inch**4
    k_2 = 2.0
    assert beams.euler_buckling_mode (l_1, E_1, I_1, k_1) == 44411463.02234584
    assert beams.euler_buckling_mode (l_2, E_2, I_2, k_2) == 1025.6361727834453
   

def test_beam_reactions_ss_cant ():
    # Beam 1
    w_1 = 50 # kN/m (which is the same as N/mm)
    b_1 = 4500 # mm
    a_1 = 2350 # mm

    # Beam 2 # Equal spans; should get 0.0 at backspan reaction
    w_2 = 19 # lbs/inch == 228 lbs/ft
    b_2 = 96 # inch
    a_2 = 96 # inch

    R1_1, R2_1 = beams.beam_reactions_ss_cant (w_1, b_1, a_1)
    R1_2, R2_2 = beams.beam_reactions_ss_cant (w_2, b_2, a_2)
    assert round (R1_1, 2), round (R2_1, 2) == (260680.56, 81819.44)
    assert round (R1_2, 2), round (R2_2, 2)  == (3648.0, 0.0)
   

def test_get_spans ():
    assert beams.get_spans (10, 7) == (7, 3)
    assert beams.get_spans (4000, 2500) == (2500, 1500)


def test_convert_to_numeric ():
    example_LIST = [['4800', '19200', '1000000000'], ['0', '3000', '4800'], ['-100', '500', '4800'], ['-200', '3600', '4800']]
    assert beams.convert_to_numeric (example_LIST) == [[4800.0, 19200.0, 1000000000.0], [0.0, 3000.0, 4800.0], [-100.0, 500.0, 4800.0], [-200.0, 3600.0, 4800.0]]


def test_get_structured_beam_data ():
    example_LIST = [['Roof beam'], ['4800', '19200', '1000000000'], ['0', '3000', '4800'], ['-100', '500', '4800'], ['-200', '3600', '4800']]
    assert beams.get_structured_beam_data (example_LIST) == {
        'Name': 'Roof beam',
        'L': 4800.0,
        'E': 19200.0,
        'I': 1000000000.0,
        'Supports': [0.0, 3000.0, 4800.0],
        'Loads': [[-100.0, 500.0, 4800.0], [-200.0, 3600.0, 4800.0]]}
    
def test_get_node_locations ():
    example_DICT = {
        'Name': 'Roof beam',
        'L': 4800.0,
        'E': 19200.0,
        'I': 1000000000.0,
        'Supports': [0.0, 3000.0, 4800.0],
        'Loads': [[-100.0, 500.0, 4800.0], [-200.0, 3600.0, 4800.0]]}
    assert beams.get_node_locations (example_DICT['Supports']) == {'N0': 0.0, 'N1': 3000.0, 'N2': 4800.0}


def test_parse_supports ():
    assert beams.parse_supports (['1000:P', '3800:R', '4800:F', '8000:R']) == {1000.0: 'P', 3800.0: 'R', 4800.0: 'F', 8000.0: 'R'}


def test_parse_loads ():
    assert beams.parse_loads ([
    ['POINT:Fy', -10000.0, 4800.0, 'case:Live'],
    ['DIST:Fy', 30.0, 30.0, 0.0, 4800.0, 'case:Dead']]) == [
    {
        "Type": "Point", 
        "Direction": "Fy", 
        "Magnitude": -10000.0, 
        "Location": 4800.0, 
        "Case": "Live"
    },
    {
        "Type": "Dist", 
        "Direction": "Fy",
        "Start Magnitude": 30.0,
        "End Magnitude": 30.0,
        "Start Location": 0.0,
        "End Location": 4800.0,
        "Case": "Dead"
    }]


def test_parse_beam_attributes ():
    assert (beams.parse_beam_attributes ([20e3, 200e3, 6480e6, 390e6, 43900, 11900e3, 0.3])) == {
        'L': 20000.0,
        'E': 200000.0,
        'Iz': 6480000000.0,
        'Iy': 390000000.0,
        'A': 43900,
        'J': 11900000.0,
        'nu': 0.3,
        'rho': 1
    }
    assert (beams.parse_beam_attributes ([4800, 24500, 1200000000, 10])) == {
        'L': 4800.0,
        'E': 24500.0,
        'Iz': 1200000000.0,
        'Iy': 10,
        'A': 1,
        'J': 1,
        'nu': 1,
        'rho': 1
    }


def test_get_node_locations ():
    assert (beams.get_node_locations (10000.0, [1000.0, 4000.0, 8000.0])) == {'N0': 0.0, 'N1': 1000.0, 'N2': 4000.0, 'N3': 8000.0, 'N4': 10000.0}
    assert (beams.get_node_locations (210.0, [0.0, 210.0])) == {'N0': 0.0, 'N2': 210.0}


def test_get_structured_beam_data ():
    assert (beams.get_structured_beam_data (
        [
            ['Balcony transfer'],
            ['4800', '24500', '1200000000', '1', '1'],
            ['1000:P', '3800:R'],
            ['POINT:Fy', '-10000', '4800', 'case:Live'],
            ['DIST:Fy', '30', '30', '0', '4800', 'case:Dead']
        ])) == {'Name': 'Balcony transfer',
    'L': 4800.0,
    'E': 24500.0,
    'Iz': 1200000000.0,
    'Iy': 1.0,
    'A': 1.0,
    'J': 1,
    'nu': 1,
    'rho': 1,
    'Supports': {1000.0: 'P', 3800.0: 'R'},
    'Loads': [{'Type': 'Point',
    'Direction': 'Fy',
    'Magnitude': -10000.0,
    'Location': 4800.0,
    'Case': 'Live'},
    {'Type': 'Dist',
    'Direction': 'Fy',
    'Start Magnitude': 30.0,
    'End Magnitude': 30.0,
    'Start Location': 0.0,
    'End Location': 4800.0,
    'Case': 'Dead'}]}