import eng_module.utils as utils

def test_str_to_float ():
    string_1 = "43"
    string_2 = "2000"
    string_3 = "324.625" # This one should generate a ValueError
    string_4 = "COLUMN300X300" # This one should generate a ValueError, too
    assert utils.str_to_float (string_1) == 43.0
    assert utils.str_to_float (string_2) == 2000.0
    assert utils.str_to_float (string_3) == 324.625


def test_str_to_int ():
    string_1 = "43"
    string_2 = "2000"
    assert utils.str_to_int (string_1) == 43
    assert utils.str_to_int (string_2) == 2000
   
