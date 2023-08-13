import sys
import typing
import doctest

sys.setrecursionlimit(10_000)

def satisfying_assignment(formula):
    """
    Find a satisfying assignment for a given CNF formula.
    Returns that assignment if one exists, or None otherwise.

    >>> satisfying_assignment([])
    {}
    >>> x = satisfying_assignment([[('a', True), ('b', False), ('c', True)]])
    >>> x.get('a', None) is True or x.get('b', None) is False or x.get('c', 
                                                            None) is True
    True
    >>> satisfying_assignment([[('a', True)], [('a', False)]])
    """
    result = {}        
    if len(formula) == 0:
        # print('bc1')
        return {}
    
    if formula[0] == [] and len(formula) == 1:
        # print('bc2')
        return None
    
    for or_clause in formula:
        if len(or_clause) == 1:
            
            formula = update_formula(formula, or_clause[0][0], or_clause[0][1])
            result[or_clause[0][0]] = or_clause[0][1]
            # print('edited', formula)        

    first_var = get_next_var(formula)
    updated_form_true = update_formula(formula, first_var, True)
    updated_form_false = update_formula(formula, first_var, False)

    count = 0
    rec_result1 = satisfying_assignment(updated_form_true)
    if rec_result1 is not None:
        dic = {first_var: True}
        dic.update(rec_result1)
        result.update(dic)
        count = 1

    if count == 0:
        rec_result2 = satisfying_assignment(updated_form_false)
        if rec_result2 is not None:
            dic = {first_var: False}
            dic.update(rec_result2)
            result.update(dic)
            count = 1

    if count == 1:
        for var in get_vars(formula):
            if var not in result:
                result[var] = True
        return result
    
    return None                
    
def is_empty(formula):
    """
    Determines if formula is empty (has empty lists).
    """
    for or_clause in formula:
        if len(or_clause) != 0:
            return False
    return True

def get_vars(formula):
    """
    Returns all vars in formula.
    """
    varbs = set()
    for or_clause in formula:
        for tup in or_clause:
            if tup[0] not in varbs:
                varbs.add(tup[0])
    return varbs

def get_next_var(formula):
    """
    Returns first string var in formula
    """
    for or_clause in formula:
        if isinstance(or_clause, list):
            for tup in or_clause:
                return tup[0]
    return None

def update_formula(formula, var, boolean):
    """
    ex formula: [('a', True), ('b', False), ('c', True)]
    ex var: 'a'
    ex boolean: True
    Returns True/False if the statement evaluates to True/False, or else returns
    a simplified or_clause as a list of tuples.

    """
    updated = []
    for or_clause in formula:
        count= 0
        for tup in or_clause:
            if var == tup[0]:
                count = 1
                if (tup[1] and boolean) or (not tup[1] and not boolean): #yeet
                    pass
                else: #slim
                    if len(or_clause) == 1:
                        updated.append([])
                    else:
                        new_or = []
                        for tup2 in or_clause:
                            if tup2 != tup:
                                new_or.append(tup2)
                        updated.append(new_or)
        if count == 0:
            updated.append(or_clause)

    if [] in updated:
        return [[]]
    return updated                  

def sudoku_board_to_sat_formula(sudoku_board):
    """
    Generates a SAT formula that, when solved, represents a solution to the
    given sudoku board.  The result should be a formula of the right form to be
    passed to the satisfying_assignment function above.
    [ [1,0,3,4],
      [3,0,0,2],
      [0,3,4,1],
      [4,1,2,3] ]
    
    [ [1,2,3,4],
      [3,4,1,2],
      [2,3,4,1],
      [4,1,2,3] ]
    
    can't be same row: ! 1in00 or ! 1in01 or ! 1in02 or ! 1in03 up to n for every row
    can't be same col: ! 1in00 or ! 1in10 or ! 1in20 or ! 1in30 up to n for every col
    can't be same grid: ! 1in00 or ! 1in01 or ! 1in10 or ! 1in11
    non-0 squares: 1in00, True
    0 squares: ! 1in01 or ! 2in01 or ! 3in01 or ! 4in01
    """
    cnf = []
    length = len(sudoku_board[0])

    row_cnf = row_uniqueness(sudoku_board)    
    col_cnf = col_uniqueness(sudoku_board)       
    grid_cnf = grid_uniqueness(sudoku_board)    
    
    for row in range(length):
        for col in range(length):
            if sudoku_board[row][col] == 0:
                zero_cnf = []
                for val in range(1,length+1):
                    zero_cnf.append((str(val) + "." +  str(row) + "." + str(col), True))
                    for n2 in range(val+1,length+1):
                        cnf.append([(str(val) + "." + str(row) + "." + str(col), False),
                                    (str(n2) + "." + str(row) + "." + str(col), False)])
                cnf.append(zero_cnf)
            else:
                cnf.append([(str(sudoku_board[row][col]) + "." + str(row) + "." + str(col), True)])  
    
    return cnf+row_cnf+col_cnf+grid_cnf
    
def row_uniqueness(sudoku_board):
    """
    Returns the cnf stating all squares in a row must be unique given a board.
    """
    cnf = []
    length = len(sudoku_board[0])
    for row in range(length):
        for val in range(1,length+1):
            row_cnf = [] 
            for col in range(length):
                row_cnf.append((str(val) + "." + str(row) + "." + str(col), True))
                for col2 in range(col+1, length):
                    cnf.append([(str(val) + "." + str(row) + "." + str(col), False),
                                (str(val) + "." + str(row) + "." + str(col2), False)])                    
            cnf.append(row_cnf)
    return cnf

def col_uniqueness(sudoku_board):
    """
    Returns the cnf stating all squares in a column must be unique given a board.
    """
    cnf = []
    length = len(sudoku_board[0])
    for col in range(length):
        for val in range(1,length+1):
            col_cnf = []  
            for row in range(length):
                col_cnf.append((str(val) + "." + str(col) + "." + str(row), True))
                for row2 in range(row+1, length):
                    cnf.append([(str(val) + "." + str(row) + "." + str(col), False),
                                (str(val) + "." + str(row2) + "." + str(col), False)])
                    
            cnf.append(col_cnf)
    return cnf       

def grid_uniqueness(sudoku_board):
    """
    Returns the cnf stating all squares in a grid must be unique given a board.
    """
    cnf = []
    length = len(sudoku_board[0])
    for row in range(length):
        for col in range(length):
            if col%(length**(1/2)) == 0 and row%(length**(1/2)) == 0: 
                #if upper-left square of subgrid
                grid_vals = values_in_subgrid(sudoku_board, row, col)    
                for val in range(1,length+1):
                    grid_cnf = [] 
                    for i in range(len(grid_vals)):
                        grid_cnf.append((str(val) + "." +  
                                         str(grid_vals[i][0]) + "." +  
                                         str(grid_vals[i][1]), True))  
                        for i2 in range(i+1, len(grid_vals)):
                            cnf.append([(str(val) + "." + str(grid_vals[i][0]) 
                                         + "." + str(grid_vals[i][1]), False),
                                        (str(val) + "." + str(grid_vals[i2][0]) 
                                         + "." + str(grid_vals[i2][1]), False)])
                    cnf.append(grid_cnf)   
    return cnf 

def values_in_subgrid(board, row, col):
    """
    Returns all values in the subgrid of a board given the row and col index
    of its upper left hand square.
    """
    length = len(board[0])
    vals = []
    for row2 in range(row, row+int(length**0.5)):
        for col2 in range(col, col+int(length**0.5)):
            vals.append((row2, col2))

    return vals
    
def assignments_to_sudoku_board(assignments, n):
    """
    Given a variable assignment as given by satisfying_assignment, as well as a
    size n, construct an n-by-n 2-d array (list-of-lists) representing the
    solution given by the provided assignment of variables.

    If the given assignments correspond to an unsolvable board, return None
    instead.
    """
    if isinstance(assignments,type(None)):
        return None
    board = []
    for row in range(n):
        board.append([0]*n)
    for key in assignments:
        if assignments[key] == True and not isinstance((key),type(None)):
            vals = key.split(".")
            board[int(vals[1])][int(vals[2])] = int(vals[0])
    return board         

if __name__ == "__main__":
    #example usage
    # a = [[["b", True], ["a", True]],[["b", True]],[["b", False],["a", False]], 
    #[["c",True],["d",True]]]
    # b = [[["e", False], ["b", False]], [["f", False]], [["a", False], 
    #["e", True]], [["i", True]], [["a", True]]]
    # print(satisfying_assignment(b))
    
