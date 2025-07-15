import random
import time
import os
from collections.abc import Callable
from typing import List, Tuple, Optional
import copy

class Sudoku:
    def __init__(self, size=9, solver: Callable = None):
        self.size = size
        self.box_size = int(size ** 0.5)
        self.board = [[0 for _ in range(size)] for _ in range(size)]
        self.solver = solver
        self.steps = 0
        self.generate_puzzle()
    
    def generate_puzzle(self):
        """Generate a valid Sudoku puzzle with some cells filled"""
        # Start with a solved board and remove numbers
        self._fill_diagonal_boxes()
        self._solve_board(copy.deepcopy(self.board))
        solved_board = copy.deepcopy(self.board)
        
        # Remove numbers to create a puzzle
        self._remove_digits(solved_board)
    
    def _fill_diagonal_boxes(self):
        """Fill diagonal boxes with random valid numbers"""
        for i in range(0, self.size, self.box_size):
            self._fill_box(i, i)
    
    def _fill_box(self, row: int, col: int):
        """Fill a 3x3 box with random valid numbers"""
        nums = list(range(1, self.size + 1))
        random.shuffle(nums)
        
        index = 0
        for i in range(self.box_size):
            for j in range(self.box_size):
                self.board[row + i][col + j] = nums[index]
                index += 1
    
    def _solve_board(self, board: List[List[int]]) -> bool:
        """Solve the board using backtracking for generation purposes"""
        empty = self._find_empty(board)
        if not empty:
            return True
        
        row, col = empty
        for num in range(1, self.size + 1):
            if self._is_valid(board, row, col, num):
                board[row][col] = num
                
                if self._solve_board(board):
                    self.board = board
                    return True
                
                board[row][col] = 0
        
        return False
    
    def _remove_digits(self, solved_board: List[List[int]], difficulty: float = 0.7):
        """Remove digits from the solved board to create a puzzle
        
        Args:
            solved_board: A completely solved Sudoku board
            difficulty: A value between 0 and 1, higher means more cells removed
        """
        # Save the original solution
        self.solution = copy.deepcopy(solved_board)
        
        # Calculate how many cells to remove
        cells_to_remove = int(self.size * self.size * difficulty)
        
        # Randomly remove cells
        cells = [(i, j) for i in range(self.size) for j in range(self.size)]
        random.shuffle(cells)
        
        for i in range(cells_to_remove):
            if i < len(cells):
                row, col = cells[i]
                self.board[row][col] = 0
    
    def _find_empty(self, board: List[List[int]]) -> Optional[Tuple[int, int]]:
        """Find an empty cell in the board"""
        for i in range(self.size):
            for j in range(self.size):
                if board[i][j] == 0:
                    return (i, j)
        return None
    
    def _is_valid(self, board: List[List[int]], row: int, col: int, num: int) -> bool:
        """Check if placing num at board[row][col] is valid"""
        # Check row
        for j in range(self.size):
            if board[row][j] == num:
                return False
        
        # Check column
        for i in range(self.size):
            if board[i][col] == num:
                return False
        
        # Check box
        box_row, box_col = row - row % self.box_size, col - col % self.box_size
        for i in range(self.box_size):
            for j in range(self.box_size):
                if board[box_row + i][box_col + j] == num:
                    return False
        
        return True
    
    def pretty_print_board(self):
        """Print the board prettily for every iteration in solving"""
        # Clear the screen for better visualization
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print(f"\n  SUDOKU SOLVER v1.0  |  Steps: {self.steps}\n")
        
        # Print horizontal line
        h_line = "  " + "+".join(["-" * (self.box_size * 2 + 1)] * self.box_size)
        
        for i in range(self.size):
            # Print horizontal line at the beginning of each box
            if i % self.box_size == 0:
                print(h_line)
            
            # Print row
            row_str = "  "
            for j in range(self.size):
                # Add vertical separator at the beginning of each box
                if j % self.box_size == 0:
                    row_str += "| "
                
                # Add the number or a space if it's 0
                cell = self.board[i][j]
                if cell == 0:
                    row_str += ". "
                else:
                    # Use ANSI color codes to highlight numbers
                    # Original numbers are white, solved ones are green
                    color_code = "\033[97m"  # White
                    row_str += f"{color_code}{cell}\033[0m "
            
            # Close the box
            row_str += "|"
            print(row_str)
        
        # Print horizontal line at the end
        print(h_line + "\n")
    
    def solve(self):
        """Solve the Sudoku puzzle"""
        if not self.solver:
            raise ValueError("No solver function provided")
        
        # First, display the unsolved board
        self.pretty_print_board()
        print("\nInitial board. Starting solver in 2 seconds...\n")
        time.sleep(2)
        
        # Then solve it
        return self.solver(self, self.pretty_print_board)

def brute_force_sudoku_solver(sudoku: Sudoku, printer):
    """Solve the Sudoku board by brute force backtracking"""
    delay = 0.1  # Delay between steps for visualization
    
    def backtrack(row=0, col=0):
        sudoku.steps += 1
        
        # If we've gone through all columns, move to the next row
        if col == sudoku.size:
            return backtrack(row + 1, 0)
        
        # If we've gone through all rows, we're done
        if row == sudoku.size:
            return True
        
        # If the cell is already filled, move to the next cell
        if sudoku.board[row][col] != 0:
            return backtrack(row, col + 1)
        
        # Try each number from 1 to 9
        for num in range(1, sudoku.size + 1):
            if sudoku._is_valid(sudoku.board, row, col, num):
                # Place the number
                sudoku.board[row][col] = num
                
                # Visualize the current state
                printer()
                time.sleep(delay)
                
                # Recursively solve the rest of the board
                if backtrack(row, col + 1):
                    return True
                
                # If placing the number didn't lead to a solution, backtrack
                sudoku.board[row][col] = 0
                printer()
                time.sleep(delay / 2)  # Faster when backtracking
        
        # If no number worked, this board is unsolvable
        return False
    
    result = backtrack()
    
    if result:
        printer()
        print("\nSolved successfully in", sudoku.steps, "steps!")
    else:
        print("\nNo solution exists.")
    
    return result

def main():
    print("\nINITIALIZING SUDOKU SOLVER...\n")
    time.sleep(1)
    
    # Create and solve the Sudoku puzzle
    sudoku = Sudoku(solver=brute_force_sudoku_solver)
    sudoku.solve()

if __name__ == "__main__":
    main()