import math
import eng_module.beams as beams

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
   

def test_euler_buckling_load ():
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
    assert beams.euler_buckling_load (l_1, E_1, I_1, k_1) == 44411463.02234584
    assert beams.euler_buckling_load (l_2, E_2, I_2, k_2) == 1025.6361727834453
   

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
   

def test_FEModel_ss_cant ():
    # Beam 1
    w_1 = 50 # kN/m (which is the same as N/mm)
    b_1 = 4500 # mm
    a_1 = 2350 # mm
    E = 1
    I = 1
    A = 1
    J = 1
    nu = 1

    model = beams.fe_model_ss_cant (w_1, b_1, a_1, E, I, A, J, nu)
    model.analyze (check_statics=True)

    r2 = round (model.Nodes ['N0'].RxnFY['Combo 1'], 2)
    r1 = round (model.Nodes ['N1'].RxnFY['Combo 1'], 2)

    ar1, ar2 = beams.beam_reactions_ss_cant (w_1, b_1, a_1)
    assert  round (ar1, 2) == r1
    assert  round (ar2, 2) == r2
