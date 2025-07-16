import random
import time
import os
import copy
from collections.abc import Callable
from typing import List, Tuple, Optional


class Sudoku:
    def __init__(self, size=9, solver: Callable = None):
        self.size = size
        self.box_size = int(size ** 0.5)
        self.board = self._create_empty_board()
        self.solver = solver
        self.steps = 0
        self.solution = None
        self.generate_puzzle()
    
    def _create_empty_board(self) -> List[List[int]]:
        return [[0 for _ in range(self.size)] for _ in range(self.size)]
    
    def generate_puzzle(self):
        self._fill_diagonal_boxes()
        self._solve_board(copy.deepcopy(self.board))
        solved_board = copy.deepcopy(self.board)
        self._remove_digits(solved_board)
    
    def _fill_diagonal_boxes(self):
        for i in range(0, self.size, self.box_size):
            self._fill_box(i, i)
    
    def _fill_box(self, row: int, col: int):
        numbers = list(range(1, self.size + 1))
        random.shuffle(numbers)
        
        index = 0
        for i in range(self.box_size):
            for j in range(self.box_size):
                self.board[row + i][col + j] = numbers[index]
                index += 1
    
    def _solve_board(self, board: List[List[int]]) -> bool:
        empty_cell = self._find_empty_cell(board)
        if not empty_cell:
            return True
        
        row, col = empty_cell
        for num in range(1, self.size + 1):
            if self._is_valid_placement(board, row, col, num):
                board[row][col] = num
                
                if self._solve_board(board):
                    self.board = board
                    return True
                
                board[row][col] = 0
        
        return False
    
    def _remove_digits(self, solved_board: List[List[int]], difficulty: float = 0.7):
        self.solution = copy.deepcopy(solved_board)
        cells_to_remove = int(self.size * self.size * difficulty)
        
        all_cells = [(i, j) for i in range(self.size) for j in range(self.size)]
        random.shuffle(all_cells)
        
        for i in range(min(cells_to_remove, len(all_cells))):
            row, col = all_cells[i]
            self.board[row][col] = 0
    
    def _find_empty_cell(self, board: List[List[int]]) -> Optional[Tuple[int, int]]:
        for i in range(self.size):
            for j in range(self.size):
                if board[i][j] == 0:
                    return (i, j)
        return None
    
    def _is_valid_placement(self, board: List[List[int]], row: int, col: int, num: int) -> bool:
        return (self._is_valid_in_row(board, row, num) and
                self._is_valid_in_column(board, col, num) and
                self._is_valid_in_box(board, row, col, num))
    
    def _is_valid_in_row(self, board: List[List[int]], row: int, num: int) -> bool:
        return num not in board[row]
    
    def _is_valid_in_column(self, board: List[List[int]], col: int, num: int) -> bool:
        return num not in [board[i][col] for i in range(self.size)]
    
    def _is_valid_in_box(self, board: List[List[int]], row: int, col: int, num: int) -> bool:
        box_row = row - row % self.box_size
        box_col = col - col % self.box_size
        
        for i in range(self.box_size):
            for j in range(self.box_size):
                if board[box_row + i][box_col + j] == num:
                    return False
        return True
    
    def display_board(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"\n  SUDOKU SOLVER v1.0  |  Steps: {self.steps}\n")
        
        horizontal_line = self._create_horizontal_line()
        
        for i in range(self.size):
            if i % self.box_size == 0:
                print(horizontal_line)
            
            row_string = self._create_row_string(i)
            print(row_string)
        
        print(horizontal_line + "\n")
    
    def _create_horizontal_line(self) -> str:
        return "  " + "+".join(["-" * (self.box_size * 2 + 1)] * self.box_size)
    
    def _create_row_string(self, row_index: int) -> str:
        row_string = "  "
        
        for col_index in range(self.size):
            if col_index % self.box_size == 0:
                row_string += "| "
            
            cell_value = self.board[row_index][col_index]
            if cell_value == 0:
                row_string += ". "
            else:
                row_string += f"\033[97m{cell_value}\033[0m "
        
        return row_string + "|"
    
    def solve(self):
        if not self.solver:
            raise ValueError("No solver function provided")
        
        self.display_board()
        print("\nInitial board. Starting solver in 2 seconds...\n")
        time.sleep(2)
        
        return self.solver(self, self.display_board)


def brute_force_solver(sudoku: Sudoku, display_function):
    VISUALIZATION_DELAY = 0.1
    BACKTRACK_DELAY = 0.05
    
    def backtrack(row=0, col=0):
        sudoku.steps += 1
        
        if col == sudoku.size:
            return backtrack(row + 1, 0)
        
        if row == sudoku.size:
            return True
        
        if sudoku.board[row][col] != 0:
            return backtrack(row, col + 1)
        
        for num in range(1, sudoku.size + 1):
            if sudoku._is_valid_placement(sudoku.board, row, col, num):
                sudoku.board[row][col] = num
                
                display_function()
                time.sleep(VISUALIZATION_DELAY)
                
                if backtrack(row, col + 1):
                    return True
                
                sudoku.board[row][col] = 0
                display_function()
                time.sleep(BACKTRACK_DELAY)
        
        return False
    
    is_solved = backtrack()
    
    if is_solved:
        display_function()
        print(f"\nSolved successfully in {sudoku.steps} steps!")
    else:
        print("\nNo solution exists.")
    
    return is_solved


def main():
    print("\nINITIALIZING SUDOKU SOLVER...\n")
    time.sleep(1)
    
    sudoku = Sudoku(solver=brute_force_solver)
    sudoku.solve()


if __name__ == "__main__":
    main()