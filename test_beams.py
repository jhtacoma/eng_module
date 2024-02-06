import math
import eng_module.beams as beams
from importlib import reload
reload (beams)


def test_str_to_int ():
    string_1 = "43"
    string_2 = "2000"
    assert beams.str_to_int (string_1) == 43
    assert beams.str_to_int (string_2) == 2000
   

def test_str_to_float ():
    string_1 = "43"
    string_2 = "2000"
    string_3 = "324.625" # This one should generate a ValueError
    string_4 = "COLUMN300X300" # This one should generate a ValueError, too
    assert beams.str_to_float (string_1) == 43.0
    assert beams.str_to_float (string_2) == 2000.0
    assert beams.str_to_float (string_3) == 324.625
   

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
   

def test_separate_lines():
    example_1_data = '4800, 200000, 437000000\n0, 3000\n-10'
    example_2_data = '228, 28000, 756\n0, 114\n-15'
    example_3_data = '6800, 200000, 803000000\n0, 3000\n18'
    example_4_data = '8000, 28000, 756e6\n0, 7000\n-52'
    assert beams.separate_lines(example_1_data) == ['4800, 200000, 437000000', '0, 3000', '-10']
    assert beams.separate_lines(example_2_data) == ['228, 28000, 756', '0, 114', '-15']
    assert beams.separate_lines(example_3_data) == ['6800, 200000, 803000000', '0, 3000', '18']
    assert beams.separate_lines(example_4_data) == ['8000, 28000, 756e6', '0, 7000', '-52']


def test_get_spans ():
    assert beams.get_spans (10, 7) == (7, 3)
    assert beams.get_spans (4000, 2500) == (2500, 1500)


def test_separate_data ():
    example_LIST = ['Roof beam', '4800, 19200, 1000000000', '0, 3000, 4800', '-100, 500, 4800', '-200, 3600, 4800']
    assert beams.separate_data (example_LIST) == [['Roof beam'], ['4800', '19200', '1000000000'], ['0', '3000', '4800'], ['-100', '500', '4800'], ['-200', '3600', '4800']]


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