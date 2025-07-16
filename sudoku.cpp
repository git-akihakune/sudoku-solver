#include <iostream>
#include <vector>
#include <random>
#include <algorithm>
#include <chrono>
#include <thread>
#include <functional>
#include <cstdlib>
#include <optional>
#include <numeric>

using namespace std;

class Sudoku {
private:
    static constexpr int DEFAULT_SIZE = 9;
    static constexpr double DEFAULT_DIFFICULTY = 0.7;
    static constexpr int VISUALIZATION_DELAY_MS = 100;
    static constexpr int BACKTRACK_DELAY_MS = 50;
    
    int size;
    int boxSize;
    vector<vector<int>> board;
    vector<vector<int>> solution;
    function<bool(Sudoku&, function<void()>)> solver;
    int steps;
    mt19937 rng;

public:
    explicit Sudoku(int boardSize = DEFAULT_SIZE, 
                   function<bool(Sudoku&, function<void()>)> solverFunc = nullptr)
        : size(boardSize), boxSize(static_cast<int>(sqrt(boardSize))), 
          board(createEmptyBoard()), solver(solverFunc), steps(0),
          rng(chrono::steady_clock::now().time_since_epoch().count()) {
        generatePuzzle();
    }

    bool solve() {
        if (!solver) {
            throw runtime_error("No solver function provided");
        }
        
        displayBoard();
        cout << "\nInitial board. Starting solver in 2 seconds...\n" << endl;
        this_thread::sleep_for(chrono::seconds(2));
        
        return solver(*this, [this]() { displayBoard(); });
    }

    void displayBoard() const {
        system("clear");
        cout << "\n  SUDOKU SOLVER v1.0  |  Steps: " << steps << "\n" << endl;
        
        string horizontalLine = createHorizontalLine();
        
        for (int i = 0; i < size; ++i) {
            if (i % boxSize == 0) {
                cout << horizontalLine << endl;
            }
            
            cout << createRowString(i) << endl;
        }
        
        cout << horizontalLine << "\n" << endl;
    }

    vector<vector<int>>& getBoard() { return board; }
    const vector<vector<int>>& getBoard() const { return board; }
    int getSize() const { return size; }
    int& getSteps() { return steps; }
    bool isValidPlacement(int row, int col, int num) const {
        return isValidInRow(row, num) && 
               isValidInColumn(col, num) && 
               isValidInBox(row, col, num);
    }

private:
    vector<vector<int>> createEmptyBoard() const {
        return vector<vector<int>>(size, vector<int>(size, 0));
    }

    void generatePuzzle() {
        fillDiagonalBoxes();
        solveBoard(board);
        solution = board;
        removeDigits(DEFAULT_DIFFICULTY);
    }

    void fillDiagonalBoxes() {
        for (int i = 0; i < size; i += boxSize) {
            fillBox(i, i);
        }
    }

    void fillBox(int startRow, int startCol) {
        vector<int> numbers(size);
        iota(numbers.begin(), numbers.end(), 1);
        shuffle(numbers.begin(), numbers.end(), rng);

        int index = 0;
        for (int i = 0; i < boxSize; ++i) {
            for (int j = 0; j < boxSize; ++j) {
                board[startRow + i][startCol + j] = numbers[index++];
            }
        }
    }

    bool solveBoard(vector<vector<int>>& targetBoard) {
        auto emptyCell = findEmptyCell(targetBoard);
        if (!emptyCell.has_value()) {
            return true;
        }

        auto [row, col] = emptyCell.value();
        for (int num = 1; num <= size; ++num) {
            if (isValidPlacement(targetBoard, row, col, num)) {
                targetBoard[row][col] = num;
                
                if (solveBoard(targetBoard)) {
                    board = targetBoard;
                    return true;
                }
                
                targetBoard[row][col] = 0;
            }
        }
        
        return false;
    }

    void removeDigits(double difficulty) {
        int cellsToRemove = static_cast<int>(size * size * difficulty);
        
        vector<pair<int, int>> allCells;
        for (int i = 0; i < size; ++i) {
            for (int j = 0; j < size; ++j) {
                allCells.emplace_back(i, j);
            }
        }
        
        shuffle(allCells.begin(), allCells.end(), rng);
        
        for (int i = 0; i < min(cellsToRemove, static_cast<int>(allCells.size())); ++i) {
            auto [row, col] = allCells[i];
            board[row][col] = 0;
        }
    }

    optional<pair<int, int>> findEmptyCell(const vector<vector<int>>& targetBoard) const {
        for (int i = 0; i < size; ++i) {
            for (int j = 0; j < size; ++j) {
                if (targetBoard[i][j] == 0) {
                    return make_pair(i, j);
                }
            }
        }
        return nullopt;
    }

    bool isValidPlacement(const vector<vector<int>>& targetBoard, int row, int col, int num) const {
        return isValidInRow(targetBoard, row, num) && 
               isValidInColumn(targetBoard, col, num) && 
               isValidInBox(targetBoard, row, col, num);
    }

    bool isValidInRow(const vector<vector<int>>& targetBoard, int row, int num) const {
        return find(targetBoard[row].begin(), targetBoard[row].end(), num) == targetBoard[row].end();
    }

    bool isValidInColumn(const vector<vector<int>>& targetBoard, int col, int num) const {
        for (int i = 0; i < size; ++i) {
            if (targetBoard[i][col] == num) {
                return false;
            }
        }
        return true;
    }

    bool isValidInBox(const vector<vector<int>>& targetBoard, int row, int col, int num) const {
        int boxRow = row - row % boxSize;
        int boxCol = col - col % boxSize;
        
        for (int i = 0; i < boxSize; ++i) {
            for (int j = 0; j < boxSize; ++j) {
                if (targetBoard[boxRow + i][boxCol + j] == num) {
                    return false;
                }
            }
        }
        return true;
    }

    bool isValidInRow(int row, int num) const {
        return isValidInRow(board, row, num);
    }

    bool isValidInColumn(int col, int num) const {
        return isValidInColumn(board, col, num);
    }

    bool isValidInBox(int row, int col, int num) const {
        return isValidInBox(board, row, col, num);
    }

    string createHorizontalLine() const {
        string line = "  ";
        for (int i = 0; i < boxSize; ++i) {
            if (i > 0) line += "+";
            line += string(boxSize * 2 + 1, '-');
        }
        return line;
    }

    string createRowString(int rowIndex) const {
        string rowStr = "  ";
        
        for (int colIndex = 0; colIndex < size; ++colIndex) {
            if (colIndex % boxSize == 0) {
                rowStr += "| ";
            }
            
            int cellValue = board[rowIndex][colIndex];
            if (cellValue == 0) {
                rowStr += ". ";
            } else {
                rowStr += "\033[97m" + to_string(cellValue) + "\033[0m ";
            }
        }
        
        return rowStr + "|";
    }
};

bool bruteForceSolver(Sudoku& sudoku, function<void()> displayFunction) {
    function<bool(int, int)> backtrack = [&](int row, int col) -> bool {
        sudoku.getSteps()++;
        
        if (col == sudoku.getSize()) {
            return backtrack(row + 1, 0);
        }
        
        if (row == sudoku.getSize()) {
            return true;
        }
        
        if (sudoku.getBoard()[row][col] != 0) {
            return backtrack(row, col + 1);
        }
        
        for (int num = 1; num <= sudoku.getSize(); ++num) {
            if (sudoku.isValidPlacement(row, col, num)) {
                sudoku.getBoard()[row][col] = num;
                
                displayFunction();
                this_thread::sleep_for(chrono::milliseconds(100));
                
                if (backtrack(row, col + 1)) {
                    return true;
                }
                
                sudoku.getBoard()[row][col] = 0;
                displayFunction();
                this_thread::sleep_for(chrono::milliseconds(50));
            }
        }
        
        return false;
    };
    
    bool isSolved = backtrack(0, 0);
    
    if (isSolved) {
        displayFunction();
        cout << "\nSolved successfully in " << sudoku.getSteps() << " steps!" << endl;
    } else {
        cout << "\nNo solution exists." << endl;
    }
    
    return isSolved;
}

int main() {
    cout << "\nINITIALIZING SUDOKU SOLVER...\n" << endl;
    this_thread::sleep_for(chrono::seconds(1));
    
    Sudoku sudoku(9, bruteForceSolver);
    sudoku.solve();
    
    return 0;
}