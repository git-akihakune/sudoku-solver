import java.util.*;
import java.util.concurrent.ThreadLocalRandom;
import java.util.function.Consumer;

interface SolverStrategy {
    boolean solve(Sudoku sudoku, Consumer<Void> displayFunction);
}

class Position {
    private final int row;
    private final int column;
    
    public Position(int row, int column) {
        this.row = row;
        this.column = column;
    }
    
    public int getRow() {
        return row;
    }
    
    public int getColumn() {
        return column;
    }
}

class Sudoku {
    private static final int DEFAULT_SIZE = 9;
    private static final double DEFAULT_DIFFICULTY = 0.7;
    private static final int VISUALIZATION_DELAY_MS = 100;
    private static final int BACKTRACK_DELAY_MS = 50;
    
    private final int size;
    private final int boxSize;
    private final int[][] board;
    private final int[][] solution;
    private final SolverStrategy solver;
    private final Random random;
    private int steps;
    
    public Sudoku(int size, SolverStrategy solver) {
        this.size = size;
        this.boxSize = (int) Math.sqrt(size);
        this.board = createEmptyBoard();
        this.solution = createEmptyBoard();
        this.solver = solver;
        this.random = ThreadLocalRandom.current();
        this.steps = 0;
        generatePuzzle();
    }
    
    public Sudoku(SolverStrategy solver) {
        this(DEFAULT_SIZE, solver);
    }
    
    public boolean solve() {
        if (solver == null) {
            throw new IllegalStateException("No solver strategy provided");
        }
        
        displayBoard();
        System.out.println("\nInitial board. Starting solver in 2 seconds...\n");
        sleep(2000);
        
        return solver.solve(this, ignored -> displayBoard());
    }
    
    public void displayBoard() {
        clearScreen();
        System.out.printf("\n  SUDOKU SOLVER v1.0  |  Steps: %d\n\n", steps);
        
        String horizontalLine = createHorizontalLine();
        
        for (int i = 0; i < size; i++) {
            if (i % boxSize == 0) {
                System.out.println(horizontalLine);
            }
            
            System.out.println(createRowString(i));
        }
        
        System.out.println(horizontalLine + "\n");
    }
    
    public int[][] getBoard() {
        return board;
    }
    
    public int getSize() {
        return size;
    }
    
    public int getSteps() {
        return steps;
    }
    
    public void incrementSteps() {
        steps++;
    }
    
    public boolean isValidPlacement(int row, int col, int num) {
        return isValidInRow(row, num) && 
               isValidInColumn(col, num) && 
               isValidInBox(row, col, num);
    }
    
    private int[][] createEmptyBoard() {
        return new int[size][size];
    }
    
    private void generatePuzzle() {
        fillDiagonalBoxes();
        solveBoard(board);
        copyBoard(board, solution);
        removeDigits(DEFAULT_DIFFICULTY);
    }
    
    private void fillDiagonalBoxes() {
        for (int i = 0; i < size; i += boxSize) {
            fillBox(i, i);
        }
    }
    
    private void fillBox(int startRow, int startCol) {
        List<Integer> numbers = new ArrayList<>();
        for (int i = 1; i <= size; i++) {
            numbers.add(i);
        }
        Collections.shuffle(numbers, random);
        
        int index = 0;
        for (int i = 0; i < boxSize; i++) {
            for (int j = 0; j < boxSize; j++) {
                board[startRow + i][startCol + j] = numbers.get(index++);
            }
        }
    }
    
    private boolean solveBoard(int[][] targetBoard) {
        Optional<Position> emptyCell = findEmptyCell(targetBoard);
        if (!emptyCell.isPresent()) {
            return true;
        }
        
        Position pos = emptyCell.get();
        int row = pos.getRow();
        int col = pos.getColumn();
        
        for (int num = 1; num <= size; num++) {
            if (isValidPlacement(targetBoard, row, col, num)) {
                targetBoard[row][col] = num;
                
                if (solveBoard(targetBoard)) {
                    copyBoard(targetBoard, board);
                    return true;
                }
                
                targetBoard[row][col] = 0;
            }
        }
        
        return false;
    }
    
    private void removeDigits(double difficulty) {
        int cellsToRemove = (int) (size * size * difficulty);
        
        List<Position> allCells = new ArrayList<>();
        for (int i = 0; i < size; i++) {
            for (int j = 0; j < size; j++) {
                allCells.add(new Position(i, j));
            }
        }
        
        Collections.shuffle(allCells, random);
        
        for (int i = 0; i < Math.min(cellsToRemove, allCells.size()); i++) {
            Position pos = allCells.get(i);
            board[pos.getRow()][pos.getColumn()] = 0;
        }
    }
    
    private Optional<Position> findEmptyCell(int[][] targetBoard) {
        for (int i = 0; i < size; i++) {
            for (int j = 0; j < size; j++) {
                if (targetBoard[i][j] == 0) {
                    return Optional.of(new Position(i, j));
                }
            }
        }
        return Optional.empty();
    }
    
    private boolean isValidPlacement(int[][] targetBoard, int row, int col, int num) {
        return isValidInRow(targetBoard, row, num) && 
               isValidInColumn(targetBoard, col, num) && 
               isValidInBox(targetBoard, row, col, num);
    }
    
    private boolean isValidInRow(int[][] targetBoard, int row, int num) {
        for (int col = 0; col < size; col++) {
            if (targetBoard[row][col] == num) {
                return false;
            }
        }
        return true;
    }
    
    private boolean isValidInColumn(int[][] targetBoard, int col, int num) {
        for (int row = 0; row < size; row++) {
            if (targetBoard[row][col] == num) {
                return false;
            }
        }
        return true;
    }
    
    private boolean isValidInBox(int[][] targetBoard, int row, int col, int num) {
        int boxRow = row - row % boxSize;
        int boxCol = col - col % boxSize;
        
        for (int i = 0; i < boxSize; i++) {
            for (int j = 0; j < boxSize; j++) {
                if (targetBoard[boxRow + i][boxCol + j] == num) {
                    return false;
                }
            }
        }
        return true;
    }
    
    private boolean isValidInRow(int row, int num) {
        return isValidInRow(board, row, num);
    }
    
    private boolean isValidInColumn(int col, int num) {
        return isValidInColumn(board, col, num);
    }
    
    private boolean isValidInBox(int row, int col, int num) {
        return isValidInBox(board, row, col, num);
    }
    
    private void copyBoard(int[][] source, int[][] destination) {
        for (int i = 0; i < size; i++) {
            System.arraycopy(source[i], 0, destination[i], 0, size);
        }
    }
    
    private void clearScreen() {
        System.out.print("\033[H\033[2J\033[3J");
        System.out.flush();
    }
    
    private String createHorizontalLine() {
        StringBuilder line = new StringBuilder("  ");
        for (int i = 0; i < boxSize; i++) {
            if (i > 0) {
                line.append("+");
            }
            line.append("-".repeat(boxSize * 2 + 1));
        }
        return line.toString();
    }
    
    private String createRowString(int rowIndex) {
        StringBuilder rowStr = new StringBuilder("  ");
        
        for (int colIndex = 0; colIndex < size; colIndex++) {
            if (colIndex % boxSize == 0) {
                rowStr.append("| ");
            }
            
            int cellValue = board[rowIndex][colIndex];
            if (cellValue == 0) {
                rowStr.append(". ");
            } else {
                rowStr.append(String.format("\033[97m%d\033[0m ", cellValue));
            }
        }
        
        return rowStr.append("|").toString();
    }
    
    private void sleep(int milliseconds) {
        try {
            Thread.sleep(milliseconds);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new RuntimeException("Sleep interrupted", e);
        }
    }
}

class BruteForceSolver implements SolverStrategy {
    private static final int VISUALIZATION_DELAY_MS = 100;
    private static final int BACKTRACK_DELAY_MS = 50;
    
    @Override
    public boolean solve(Sudoku sudoku, Consumer<Void> displayFunction) {
        boolean isSolved = backtrack(sudoku, displayFunction, 0, 0);
        
        if (isSolved) {
            displayFunction.accept(null);
            System.out.printf("\nSolved successfully in %d steps!\n", sudoku.getSteps());
        } else {
            System.out.println("\nNo solution exists.");
        }
        
        return isSolved;
    }
    
    private boolean backtrack(Sudoku sudoku, Consumer<Void> displayFunction, int row, int col) {
        sudoku.incrementSteps();
        
        if (col == sudoku.getSize()) {
            return backtrack(sudoku, displayFunction, row + 1, 0);
        }
        
        if (row == sudoku.getSize()) {
            return true;
        }
        
        if (sudoku.getBoard()[row][col] != 0) {
            return backtrack(sudoku, displayFunction, row, col + 1);
        }
        
        for (int num = 1; num <= sudoku.getSize(); num++) {
            if (sudoku.isValidPlacement(row, col, num)) {
                sudoku.getBoard()[row][col] = num;
                
                displayFunction.accept(null);
                sleep(VISUALIZATION_DELAY_MS);
                
                if (backtrack(sudoku, displayFunction, row, col + 1)) {
                    return true;
                }
                
                sudoku.getBoard()[row][col] = 0;
                displayFunction.accept(null);
                sleep(BACKTRACK_DELAY_MS);
            }
        }
        
        return false;
    }
    
    private void sleep(int milliseconds) {
        try {
            Thread.sleep(milliseconds);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new RuntimeException("Sleep interrupted", e);
        }
    }
}

public class SudokuSolver {
    public static void main(String[] args) {
        System.out.println("\nINITIALIZING SUDOKU SOLVER...\n");
        sleep(1000);
        
        Sudoku sudoku = new Sudoku(new BruteForceSolver());
        sudoku.solve();
    }
    
    private static void sleep(int milliseconds) {
        try {
            Thread.sleep(milliseconds);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new RuntimeException("Sleep interrupted", e);
        }
    }
}