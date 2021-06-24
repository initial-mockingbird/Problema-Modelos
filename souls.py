#####################################################################################
## Title:  Souls Model Parser                                                      ##
## Author: Daniel Pinto (15-11139)                                                 ##
## Year:   2021                                                                    ##
## Description: The following script is used to generate                           ##
##              excel csv file needed in order to solve the souls problem          ##
#####################################################################################


from sympy import *
from typing import Tuple
import sys

# Base statistics of the chosen undead
BASE_STATS = {
    'Str': 3,
    'Dex': 2,
    'Item': 3,
    'f_prev': 200
}


def souls_lothric(Str : str,Dex : str,Item_discovery : str) -> str:
    '''
    Given the stats for `strength`, `dexterity` and `item discovery` yields a string representation
    of the formula that's used to calculate the number of souls for the High Wall of Lothric.
    '''

    # Direct Transcript of the formula
    str_earned = f"3*({Str})"
    dex_earned = f"(-11)*({Dex})/7"
    high_items = f"(1*({Item_discovery})/4)"
    mid_items  = f"(5*({Item_discovery})/4)"
    low_items  = f"(3*({Item_discovery})/2)"
    total_items= f"{high_items} + {mid_items} + {low_items}"
    return f"({str_earned} + {dex_earned} + {total_items})"
    
def souls_londo (Str : str,dex : str,item_discovery : str) -> str:
    '''
    Given the stats for `strength`, `dexterity` and `item discovery` yields a string representation
    of the formula that's used to calculate the number of souls for the New Londo Ruins.
    '''

    # Direct Transcript of the formula
    combined_earned = f"1*((({Str})*({dex})) - 2*({Str}+{dex}))"
    high_items = f"(3*({item_discovery})/5)"
    mid_items  = f"(2*({item_discovery})/4)"
    low_items  = f"(11*({item_discovery})/20)"
    total_items= f"{high_items} + {mid_items} + {low_items}"
    return f"({combined_earned} + {total_items})"

def souls_archives(Str : str,Dex : str,Item_discovery : str) -> str:
    '''
    Given the stats for `strength`, `dexterity` and `item discovery` yields a string representation
    of the formula that's used to calculate the number of souls for the Archhives.
    '''

    # Direct Transcript of the formula
    str_earned = f"(-1)*{Str}"
    dex_earned = f"5*{Dex}/2"
    high_items = f"(3*({Item_discovery})/2)"
    mid_items  = f"(1*({Item_discovery})/2)"
    total_items= f"{high_items} + {mid_items}"
    return f"({str_earned} + {dex_earned} + {total_items}) + 300"

def subir_nivel(new_levels : str,total_levels : str) -> str:
    '''
    Given the total number of levels and the number of new levels, yields the total number of souls
    that the chosen undead must pay in order to level up that many levels
    '''
    # Direct Transcript of the formula
    return f"(((1/300)*({new_levels})*({total_levels})) + (5)*({new_levels}))"

def general_obj(iter : int, total_str_n : str, total_dex_n : str,total_item_n : str,new_levels : str,total_levels: str) -> str:
    '''
    Given the number of the current run, the simbolic variable for each skill, the number of new levels and the total number of levels
    yields the formula for the objective function for the n-th run.
    '''
    # Direct Transcript of the formula
    return (
        f"((lotrhic_{iter}*({souls_lothric(total_str_n, total_dex_n,total_item_n)})) + (londo_{iter} * ({souls_londo(total_str_n, total_dex_n,total_item_n)})) + (archives_{iter} *({souls_archives(total_str_n, total_dex_n,total_item_n)})) - ({subir_nivel(new_levels,total_levels)}))"
    )


def generate_restrictions(iter : int,str_n : str, dex_n : str, item_n : str, total_levels_prev : str,f_prev : str) -> str:
    '''
    Given the number of the current run, the simbolic variable for each skill, the total number of levels and the profit thus far
    yields a list of restrictions for the n-th run
    '''

    new_levels = f"{str_n} + {dex_n} + {item_n}"
    # We find the difference: profit so far - cost of leveling up
    subir_nivel_restr = str(expand(parse_expr(f"{f_prev} - ({subir_nivel(new_levels,total_levels_prev)})")))
    # each restriction has the form: (restriction, EQ | LT | GT | LTE | GTE, value)
    # EQ : EQuals
    # LT : Less Than
    # GT : Greater Than
    # LTE: Less Than or Equal
    # GTE: Greater Than or Equal
    restrictions = [
        (f"lotrhic_{iter}*londo_{iter}","LT","1"),
        (f"lotrhic_{iter}*archives_{iter}","LT","1"),
        (f"londo_{iter}*archives_{iter}","LT","1"),
        (f"lotrhic_{iter} + londo_{iter} + archives_{iter}","EQ","1"),
        (subir_nivel_restr,"GTE","0")
        ]
    return restrictions

def generate_problem(base_stats,max_iter = 3) -> Tuple[str,str]:
    '''
    Given the base stats, and an optional parameter specifying how many runs are allowed, yields a tuple:
    `(objective_function,restrictions)`, where `objective_function`  is a string representation of the objective
    function and `restrictions` is a list of triplets restrictions, like the ones specified in `generate_restrictions`
    '''

    # We initialize the variables
    
    # The skills are the base skills
    total_str    = f"{base_stats['Str']} "
    total_dex    = f"{base_stats['Dex']} "
    total_item   = f"{base_stats['Item']} "
    # initially, there are no new levels
    new_levels   = f""
    # We start at level 0
    total_levels = f"0"
    # initially, the objective function is how many currency we initially have
    objective_function = f"{base_stats['f_prev']}"
    # and the set of restrictions is empty
    restrictions       = []
    # now, for each run
    for i in range(0,max_iter):
        # add a new variable representing the posibility to add the skill
        total_str += f" + str_{i}"
        total_dex += f" + dex_{i}"
        total_item+= f" + item_{i}"
        
        new_levels = f" str_{i} + dex_{i} + item_{i}"
        # generate the restriction and objective functions
        restrictions       += generate_restrictions(i,f'str_{i}',f'dex_{i}',f'item_{i}',total_levels,objective_function)
        objective_function += f" + ({expand(parse_expr(general_obj(i,total_str,total_dex,total_item,new_levels,total_levels)))})"
        # and finally, update the total_levels so that in the next iteration, can take the new levels into account
        total_levels += f"+ {new_levels}"
        
        
    # finally, simplify one last time the objective
    objective_function = str(expand(parse_expr(objective_function)))
    # and sort the restictions by the type constraint: EQ | LT | GT | LTE | GTE
    restrictions       = sorted(restrictions, key = lambda x: x[1])
    return (objective_function,restrictions )


def wrapper_parsedVars():
    '''
    Wrapper function so we don't create the operators string each time....
    ok, so listen up, i thought that the shared states were gonna be bigger than this...
    IT'S NOT MY FAULT!
    '''
    operators = "-+*/"
    def parseVars(objective_function):
        '''
        Given the objective functions, returns a list of variables that composes it.
        '''
        # Since we don't want repeated variables, we use a set to hold it
        variables = set()
        parsed = ""
        # replace every space so parsing is easier
        objective_function = objective_function.replace(" ","")
        parsing_var = False 
        # super hacky, the function has the following pattern:
        # Number | Variable <operator> Number | Variable
        # thus it suffices to check that the token that we are parsing is not a number
        # nor an operator:

        # for every character in the funcition
        for c in objective_function:
            # if we are not parsing a variable, and the next char is not a digit nor an operator
            # then it must be the beginning of a variable.
            if not parsing_var and not c.isdigit() and c not in operators:
                # begin to parse the variable
                parsed += c
                # and signal that we are parsing a variable
                parsing_var = True
            # if we are parsing a variable and we have not yet arrived and an operator
            elif parsing_var and c not in operators:
                # continue creating the variable token
                parsed +=c
            # if we were parsing a variable and we hit an operator:
            elif parsing_var and c in operators:
                # then we are finished parsing this token and we add the variable to the set
                variables.add(parsed)
                # we signal that we are no longer parsing a variable
                parsing_var = False
                # and we clean the parsed string
                parsed = ""
        return variables
    return parseVars

def parseVars(objective_function):
    unwrapped = wrapper_parsedVars()
    return list(unwrapped(objective_function))

def pair_variables(variables):
    '''
    Given a list of variables, creates a list of objects that hold enough information to post
    the variable vector that the solver will modify.

    Currently, The name of each variable will be hold in the `A` column and the values are hold
    in the `B` column
    '''
    paired = []
    i = 1
    # for each variable
    for variable in variables:
        # build the object
        info = {
            "header": {
                "name": variable,
                "pos":f"A{i}"
            },
            "value": {
                "value": 0,
                "pos":f"B{i}"
            }
        }
        # append the info
        paired.append(info)
        i += 1
    return paired

def pair_objective_function(paired_vars,objective_function):
    '''
    Given the list of object variables and the objective function, yields an object that holds enough information
    to post the objective function.

    The name "obj" will be posted to the `C1` cell and the value will we posted to `D1`.
    '''
    info = {
            "header": {
                "name": "obj:",
                "pos":f"C{1}"
            },
            "value": {
                "value": 0,
                "pos":f"D{1}"
            }
        }
    
    # for each variable
    for var_info in paired_vars:
        # replace all the occurrences of the variable for the Cell position.
        objective_function = objective_function.replace(var_info["header"]["name"],var_info["value"]["pos"])
    
    # Finally, since excel formulas are of the form '=FORMULA', we prepend an '='
    info["value"]["value"] = f'={objective_function}'

    return [info]

def pair_restriction (paired_vars,restrictions):
    '''
    Given the list of object variables and a list of restrictions, yields an object that holds enough information
    to post the restrictions.

    The Restrictions are posted to the `E` column, the relation to the `F` and the constraint to the `G` function.
    '''
    i = 1
    rs = []
    # for each triplet in the restrictions
    for (restriction,comparator,value) in restrictions:
        # replace each variable in the restriction
        for var_info in paired_vars:
            restriction = restriction.replace(var_info["header"]["name"],var_info["value"]["pos"])

        restriction = f'={restriction}'
        # and create the object
        info = {
            "header": {
                "name": comparator,
                "pos":f"F{i}"
            },
            "value": {
                "value": restriction,
                "pos":f"E{i}"
            },
            "ternary": {
                "value": value,
                "pos":f"G{i}"
            }
        }
        rs.append(info)
        i += 1
    return rs

def toCSVMatrix(p_vars,p_obj,p_r):
    '''
    Given the objects for variables, function and restriction, construct a Matrix that is going to represent the CSV
    '''

    # gets the row of an object
    def getRow(x):
        col_row = x["value"]["pos"]
        number = ""
        for c in col_row:
            if c.isdigit():
                number += c
        return int(number)
    # gets the maximum row of a list of objects
    def getMaxRow(x):
        return max(map(getRow,x))
    
    # Transforms the position of an object (Cell) to an index
    def posToIndex(pos):
        col = ""
        row = ""
        for c in pos:
            if c.isdigit():
                row += c
            else:
                col += c
        cols = ["A","B","C","D","E","F","G"]
        row  = int(row)
        col  = cols.index(col)
        return (row-1,col)

    #get the maximum number of rows
    row_number = getMaxRow(p_vars + p_obj + p_r)
    # get the maximum number of columns
    col_number = len(["A","B","C","D","E","F","G"])
    # build an empty matrix 
    matrix     = [['' for _ in range(col_number)] for _ in range(row_number)] 

    # and for each object
    for info_var in (list(p_vars)+list(p_obj)+list(p_r)):
        # fill all the common entries
        (header_row,header_col)        = posToIndex(info_var["header"]["pos"])
        matrix[header_row][header_col] = info_var["header"]["name"]
        (value_row,value_col)          = posToIndex(info_var["value"]["pos"])
        matrix[value_row][value_col]   = info_var["value"]["value"]
        # and try to fill the ternary field
        try:
            (ternary_row,ternary_col)        = posToIndex(info_var["ternary"]["pos"])
            matrix[ternary_row][ternary_col] = info_var["ternary"]["value"]
        except:
            pass
    return matrix

def toCSV(p_vars,p_obj,p_r,csv_file="csv_log.csv"):
    matrix   = toCSVMatrix(p_vars,p_obj,p_r)
    csv_repr = ""
    for row in map(str,matrix):
        csv_repr += row.replace("[","").replace("]","") + "\n"
    
    with open(csv_file,mode="w") as f:
        csv_repr = csv_repr.replace("'","").replace(" ","").strip()
        f.write(csv_repr)
    

if __name__=="__main__":
    try:
        max_iter = int(sys.argv[1])
    except:
        max_iter = 3
    (objective_function,restrictions) = generate_problem(BASE_STATS,max_iter=max_iter)
    variables = parseVars(objective_function)
    p_var     = pair_variables(variables)
    p_obj     = pair_objective_function(p_var,objective_function)
    p_r       = pair_restriction(p_var,restrictions)
    csv_file  = f"csv_log{max_iter}.csv"
    toCSV(p_var,p_obj,p_r,csv_file=csv_file)

