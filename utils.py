import csv #btw, you DO include import statements here as opposed to whatever python file imports this current file ...

def read_csv_file (the_filename:str) -> list[list[str]]:
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
    return_LIST = [] # File data goes here
    with open(the_filename, "r") as csv_file:
        csv_reader = csv.reader(csv_file)
        for line in csv_reader:
            return_LIST.append(line)
    return (return_LIST)


def str_to_float (s:str) -> float | str:
    '''
    Returns a float if the string 's' represents a floating point number;
    if it's not an int or float, the original string is returned.
    Params:
    's' - string to convert
    '''
    try:
        x = float (s)
        return float (s)
    except:
        return s
    

def str_to_int (s:str) -> int | str:
    '''
    Returns an int if the string 's' represents an integer;
    if it's not an int, the original string is returned.
    Params:
    's' - string to convert
    '''
    try:
        x = int (s)
        return int (s)
    except:
        return s

