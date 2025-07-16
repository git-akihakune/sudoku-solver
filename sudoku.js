#!/usr/bin/env node

const { randomInt } = require('crypto');
const { promisify } = require('util');

const sleep = promisify(setTimeout);

class Position {
    constructor(row, column) {
        this.row = row;
        this.column = column;
    }

    static create(row, column) {
        return new Position(row, column);
    }
}

class SudokuConfig {
    static get DEFAULT_SIZE() { return 9; }
    static get DEFAULT_DIFFICULTY() { return 0.7; }
    static get VISUALIZATION_DELAY_MS() { return 100; }
    static get BACKTRACK_DELAY_MS() { return 50; }
    static get EMPTY_CELL() { return 0; }
    static get ANSI_WHITE() { return '\x1b[97m'; }
    static get ANSI_RESET() { return '\x1b[0m'; }
}

class BoardValidator {
    constructor(board, size, boxSize) {
        this.board = board;
        this.size = size;
        this.boxSize = boxSize;
    }

    isValidPlacement(row, col, num) {
        return this.isValidInRow(row, num) && 
               this.isValidInColumn(col, num) && 
               this.isValidInBox(row, col, num);
    }

    isValidInRow(row, num) {
        return !this.board[row].includes(num);
    }

    isValidInColumn(col, num) {
        return !this.board.some(row => row[col] === num);
    }

    isValidInBox(row, col, num) {
        const boxRow = Math.floor(row / this.boxSize) * this.boxSize;
        const boxCol = Math.floor(col / this.boxSize) * this.boxSize;
        
        for (let i = 0; i < this.boxSize; i++) {
            for (let j = 0; j < this.boxSize; j++) {
                if (this.board[boxRow + i][boxCol + j] === num) {
                    return false;
                }
            }
        }
        return true;
    }
}

class BoardGenerator {
    constructor(size) {
        this.size = size;
        this.boxSize = Math.sqrt(size);
        this.board = this.createEmptyBoard();
    }

    createEmptyBoard() {
        return Array.from({ length: this.size }, () => 
            Array(this.size).fill(SudokuConfig.EMPTY_CELL));
    }

    generatePuzzle() {
        this.fillDiagonalBoxes();
        this.solveBoard();
        const solution = this.copyBoard(this.board);
        this.removeDigits(SudokuConfig.DEFAULT_DIFFICULTY);
        return { puzzle: this.board, solution };
    }

    fillDiagonalBoxes() {
        for (let i = 0; i < this.size; i += this.boxSize) {
            this.fillBox(i, i);
        }
    }

    fillBox(startRow, startCol) {
        const numbers = Array.from({ length: this.size }, (_, i) => i + 1);
        this.shuffleArray(numbers);

        let index = 0;
        for (let i = 0; i < this.boxSize; i++) {
            for (let j = 0; j < this.boxSize; j++) {
                this.board[startRow + i][startCol + j] = numbers[index++];
            }
        }
    }

    solveBoard() {
        const emptyCell = this.findEmptyCell();
        if (!emptyCell) return true;

        const { row, column } = emptyCell;
        const validator = new BoardValidator(this.board, this.size, this.boxSize);

        for (let num = 1; num <= this.size; num++) {
            if (validator.isValidPlacement(row, column, num)) {
                this.board[row][column] = num;
                
                if (this.solveBoard()) {
                    return true;
                }
                
                this.board[row][column] = SudokuConfig.EMPTY_CELL;
            }
        }
        return false;
    }

    removeDigits(difficulty) {
        const cellsToRemove = Math.floor(this.size * this.size * difficulty);
        const allCells = [];
        
        for (let i = 0; i < this.size; i++) {
            for (let j = 0; j < this.size; j++) {
                allCells.push(Position.create(i, j));
            }
        }
        
        this.shuffleArray(allCells);
        
        for (let i = 0; i < Math.min(cellsToRemove, allCells.length); i++) {
            const { row, column } = allCells[i];
            this.board[row][column] = SudokuConfig.EMPTY_CELL;
        }
    }

    findEmptyCell() {
        for (let i = 0; i < this.size; i++) {
            for (let j = 0; j < this.size; j++) {
                if (this.board[i][j] === SudokuConfig.EMPTY_CELL) {
                    return Position.create(i, j);
                }
            }
        }
        return null;
    }

    copyBoard(board) {
        return board.map(row => [...row]);
    }

    shuffleArray(array) {
        for (let i = array.length - 1; i > 0; i--) {
            const j = randomInt(0, i + 1);
            [array[i], array[j]] = [array[j], array[i]];
        }
    }
}

class BoardDisplay {
    constructor(board, size, boxSize) {
        this.board = board;
        this.size = size;
        this.boxSize = boxSize;
    }

    displayBoard(steps = 0) {
        this.clearScreen();
        console.log(`\n  SUDOKU SOLVER v1.0  |  Steps: ${steps}\n`);
        
        const horizontalLine = this.createHorizontalLine();
        
        for (let i = 0; i < this.size; i++) {
            if (i % this.boxSize === 0) {
                console.log(horizontalLine);
            }
            console.log(this.createRowString(i));
        }
        
        console.log(horizontalLine + '\n');
    }

    clearScreen() {
        process.stdout.write('\x1b[H\x1b[2J\x1b[3J');
    }

    createHorizontalLine() {
        const segments = Array(this.boxSize).fill('-'.repeat(this.boxSize * 2 + 1));
        return '  ' + segments.join('+');
    }

    createRowString(rowIndex) {
        let rowStr = '  ';
        
        for (let colIndex = 0; colIndex < this.size; colIndex++) {
            if (colIndex % this.boxSize === 0) {
                rowStr += '| ';
            }
            
            const cellValue = this.board[rowIndex][colIndex];
            if (cellValue === SudokuConfig.EMPTY_CELL) {
                rowStr += '. ';
            } else {
                rowStr += `${SudokuConfig.ANSI_WHITE}${cellValue}${SudokuConfig.ANSI_RESET} `;
            }
        }
        
        return rowStr + '|';
    }
}

class BruteForceSolver {
    constructor(sudoku) {
        this.sudoku = sudoku;
        this.steps = 0;
    }

    async solve() {
        const solved = await this.backtrack(0, 0);
        
        if (solved) {
            this.sudoku.displayBoard(this.steps);
            console.log(`\nSolved successfully in ${this.steps} steps!`);
        } else {
            console.log('\nNo solution exists.');
        }
        
        return solved;
    }

    async backtrack(row, col) {
        this.steps++;
        
        if (col === this.sudoku.size) {
            return this.backtrack(row + 1, 0);
        }
        
        if (row === this.sudoku.size) {
            return true;
        }
        
        if (this.sudoku.board[row][col] !== SudokuConfig.EMPTY_CELL) {
            return this.backtrack(row, col + 1);
        }
        
        for (let num = 1; num <= this.sudoku.size; num++) {
            if (this.sudoku.isValidPlacement(row, col, num)) {
                this.sudoku.board[row][col] = num;
                
                this.sudoku.displayBoard(this.steps);
                await sleep(SudokuConfig.VISUALIZATION_DELAY_MS);
                
                if (await this.backtrack(row, col + 1)) {
                    return true;
                }
                
                this.sudoku.board[row][col] = SudokuConfig.EMPTY_CELL;
                this.sudoku.displayBoard(this.steps);
                await sleep(SudokuConfig.BACKTRACK_DELAY_MS);
            }
        }
        
        return false;
    }
}

class Sudoku {
    constructor(size = SudokuConfig.DEFAULT_SIZE, solverClass = BruteForceSolver) {
        this.size = size;
        this.boxSize = Math.sqrt(size);
        this.solverClass = solverClass;
        this.steps = 0;
        
        this.initializePuzzle();
        this.setupValidator();
        this.setupDisplay();
    }

    initializePuzzle() {
        const generator = new BoardGenerator(this.size);
        const { puzzle, solution } = generator.generatePuzzle();
        this.board = puzzle;
        this.solution = solution;
    }

    setupValidator() {
        this.validator = new BoardValidator(this.board, this.size, this.boxSize);
    }

    setupDisplay() {
        this.display = new BoardDisplay(this.board, this.size, this.boxSize);
    }

    async solve() {
        if (!this.solverClass) {
            throw new Error('No solver class provided');
        }
        
        this.displayBoard();
        console.log('\nInitial board. Starting solver in 2 seconds...\n');
        await sleep(2000);
        
        const solver = new this.solverClass(this);
        return solver.solve();
    }

    displayBoard(steps = this.steps) {
        this.display.displayBoard(steps);
    }

    isValidPlacement(row, col, num) {
        return this.validator.isValidPlacement(row, col, num);
    }

    getBoard() {
        return this.board;
    }

    getSolution() {
        return this.solution;
    }

    getSize() {
        return this.size;
    }

    incrementSteps() {
        this.steps++;
    }

    getSteps() {
        return this.steps;
    }
}

class SudokuApp {
    static async main() {
        try {
            console.log('\nINITIALIZING SUDOKU SOLVER...\n');
            await sleep(1000);
            
            const sudoku = new Sudoku();
            await sudoku.solve();
        } catch (error) {
            console.error('Error:', error.message);
            process.exit(1);
        }
    }
}

if (require.main === module) {
    SudokuApp.main().catch(console.error);
}

module.exports = {
    Sudoku,
    BruteForceSolver,
    Position,
    SudokuConfig,
    BoardValidator,
    BoardGenerator,
    BoardDisplay,
    SudokuApp
};