"""

    Collection of methods to perform DRC.

"""
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Magic.Cell import Cell

import os
import shutil

def DRC_collidates(cell : Cell, cells : list[Cell]) -> bool:
    """Checks if <cell> collidates with one of <cells>  

    Args:
        cell (Cell): Cell which gets checked.
        cells (list(Cell)): List of cells.

    Returns:
        bool: True if cell collidates with one of cells.
    """
    for c in cells:
        if cell.collidates(c):
            return True
        
    return False

def DRC_collidates_all(cells : list[Cell]) -> bool:
    """Checks if one of the cells collidates with another.

    Args:
        cells (list(Cell)): Cells which shall be checked

    Returns:
        bool: True if cells collidate.
    """

    for i in range(len(cells)-1):
        if DRC_collidates(cells[i], cells[i+1:]):
            return True
        
    return False


def DRC_magic_all(name : str) -> int:
    """Check if the placement with name <name>, has DRC errors.

    Args:
        name (str): Name of the placement.

    Raises:
        FileNotFoundError: If the .mag file of the placement can't be found.

    Returns:
        int: Number of DRC errors
    """
    #check if Placement exists
    if os.path.exists(f'Magic/Placement/{name}.mag'):
        #if DRC folder exists delete it
        if os.path.exists('Magic/Placement/DRC_Result'):
            shutil.rmtree('Magic/Placement/DRC_Result')

        #make the DRC folder
        os.makedirs('Magic/Placement/DRC_Result')
        act_dir = os.getcwd()
        os.chdir('Magic/Placement/DRC_Result')

        #perform the DRC check in magic.
        os.system(f'bash {act_dir}/Magic/magic_drc.sh ../{name}.mag')

        with open(f'{name}.magic.drc.rpt') as file:
            for line in file:
                pass
            last_line = line

        DRC_errors = eval(last_line)

        os.chdir(act_dir)        
        return DRC_errors
    else:
        raise FileNotFoundError
    
def DRC_magic_check_cell(layout_name : str, cell : Cell) -> int:
    """Check if the cell <cell> of placement with name <name>, has DRC errors.

    Args:
        name (str): Name of the placement.

    Raises:
        FileNotFoundError: If the .mag file of the placement can't be found.

    Returns:
        int: Number of DRC errors
    """
    #check if Placement exists
    if os.path.exists(f'Magic/Placement/{layout_name}.mag'):
        #if DRC folder exists delete it
        if os.path.exists('Magic/Placement/DRC_Result'):
            shutil.rmtree('Magic/Placement/DRC_Result')

        box = cell.get_bounding_box()

        #make the DRC folder
        os.makedirs('Magic/Placement/DRC_Result')
        act_dir = os.getcwd()
        os.chdir('Magic/Placement/DRC_Result')
        os.system(f'bash {act_dir}/Magic/magic_drc.sh -b {box[0]} -b {box[1]} -b {box[2]} -b {box[3]} ../{layout_name}.mag')

        with open(f'{layout_name}.magic.drc.rpt') as file:
            for line in file:
                pass
            last_line = line

        DRC_errors = eval(last_line)

        os.chdir(act_dir)        
        return DRC_errors
    else:
        raise FileNotFoundError