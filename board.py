from enum import Enum
import unittest

class Color(Enum):
    """ Enumeration of possible colors """
    NONE = 0
    RED = 1
    BLACK = 2

class Board:
    """
    Implementation of the game board.

    The contents of the board can be accessed using array notation. The
    board is 6 rows x 7 cols. Each cell is a Color enum.
    board = Board()
    print(board[3][2])
    board[4][1] = Color.RED
    """

    def __init__(self):
        """ Initialize and clear the board """
        self.clear()

    def __getitem__(self, index):
        """ Allows use of array indices, for example board[2][4] to get row 2 col 4 """
        return self.state[index]

    def clear(self):
        """ Clear the board """
        self.state = []
        for i in range(6):
            self.state.append([Color.NONE] * 7)

    def save(self):
        """
        Save state to a string output of 7x6=42 characters
        Each character is one of the following
        0 None
        1 Red
        2 Black
        Each cell is saved top to bottom, left to right
        """
        s = ['0'] * 42
        pos = 0
        for row in self.state:
            for col in row:
                if col is Color.RED:
                    s[pos] = '1'
                elif col is Color.BLACK:
                    s[pos] = '2'
                pos = pos + 1
        return ''.join(s)

    def load(self,str):
        """
        Loads state from string of 7x6=42 characters
        See comment on save() for string format
        """
        self.clear()
        row = 0
        col = 0
        for val in list(str):
            if val == '1':
                self.state[row][col] = Color.RED
            elif val == '2':
                self.state[row][col] = Color.BLACK
            col = col + 1
            if col>6:
                row = row + 1
                col = 0

    def drop(self,color,column):
        """ Drops the given color cookie into the given column """
        row = 5
        while row>=0 and not(self.state[row][column] is Color.NONE):
            row = row - 1
        if row>=0:
            self.state[row][column] = color

    def isFull(self,column):
        """ Returns true if the column is full """
        return not(self.state[0][column] is Color.NONE) # top cookie is colored

    def isDraw(self):
        """ Returns true if there are no more moves """
        return all(not(x is Color.NONE) for x in self.state[0]) # top row is colored

    def __consecutiveLists(self):
        """ Returns a list of lists of all consecutive cells in a line, to use for counting how many in a row """
        lines = []
        # all rows
        lines.extend(self.state)
        # all columns
        for col in range(7):
            line = []
            for row in range(6):
                line.append(self.state[row][col])
            lines.append(line)
        # top left to bottom right diagonals
        for col in range(3,9):
            line = []
            curcol = col
            currow = 5
            while currow>=0:
                if curcol>=0 and curcol<7:
                    line.append(self.state[currow][curcol])
                curcol = curcol-1
                currow = currow-1
            lines.append(line)
        # top right to bottom left diagonals
        for col in range(-2,4):
            line = []
            curcol = col
            currow = 5
            while currow>=0:
                if curcol>=0 and curcol<7:
                    line.append(self.state[currow][curcol])
                curcol = curcol+1
                currow = currow-1
            lines.append(line)
        return lines        

    def winner(self):
        """ Returns the color of the winner (Color.NONE if no one has won) """
        # Create list of lists of all consecutive cells in a line, then check each one
        lines = self.__consecutiveLists()
        # Now check each line for a winner
        for line in lines:
            prior = Color.NONE
            runlength = 0
            for color in line:
                if color is prior:
                    runlength = runlength + 1
                else:
                    runlength = 1
                if runlength>3 and color!=Color.NONE:
                    return color # winner
                prior = color
        return Color.NONE # no winner

    def __calcMove(self,depth,color):
        """ Calculate's color's move using the given search depth. Returns tuple (move,value) """
        def undrop(col):
            """ Helper function to remove topmost cookie """
            for row in range(6):
                if not(self.state[row][col] is Color.NONE):
                    self.state[row][col] = Color.NONE
                    return
        def boardVal():
            """ Helper function to calculate board value in current state """
            # Get largest run length across rows, cols, and diagonals where we can add more
            lines = self.__consecutiveLists()
            maxlength = 0
            for line in lines:
                runlength = 0
                for color in line:
                    if color is Color.BLACK:
                        runlength = runlength + 1
                    elif color is Color.RED:
                        break
                    if runlength>maxlength:
                        maxlength = runlength
            return maxlength

        bestVal = -1
        if color is Color.RED:
            bestVal = 99
        bestCol = 3
        for col in range(7):
            if not(self.isFull(col)):
                self.drop(color, col)
                val = 0
                winner = self.winner()
                if winner is Color.RED:
                    val = 0
                elif winner is Color.BLACK:
                    val = 4
                elif depth<1:
                    val = boardVal()
                elif color is Color.RED:
                    (val,_) = self.__calcMove(depth-1,Color.BLACK)
                else:
                    (val,_) = self.__calcMove(depth-1,Color.RED)
                #self.print()
                #print(str(color) + ' col=' + str(col) + ' val=' + str(val))
                undrop(col)
                if (color is Color.RED and val<bestVal) or (color is Color.BLACK and val>bestVal) or (val==bestVal and abs(col-3)<abs(bestCol-3)):
                    bestVal = val
                    bestCol = col
                if not(winner is Color.NONE):
                    return (val,col) # on win, return
        #print('best col=' + str(bestCol) + ' val=' + str(bestVal))
        return (bestVal,bestCol)

    def blackMove(self,depth):
        """ Calculate's black's move using the given search depth. Returns column to drop in """
        (v,m) = self.__calcMove(depth,Color.BLACK)
        return m

    def redMove(self,depth):
        """ Calculate's red's move using the given search depth. Returns column to drop in """
        (v,m) = self.__calcMove(depth,Color.RED)
        return m

    def emojiPrint(self):
        """ Prints the board to a string using emojis """
        whitecircle = '\U000026AA'
        redcircle = '\U0001F534'
        blackcircle = '\U000026AB'
        str = ""
        for row in self.state:
            for col in row:
                if col is Color.NONE:
                    str = str + whitecircle
                elif col is Color.RED:
                    str = str + redcircle
                elif col is Color.BLACK:
                    str = str + blackcircle
            str = str + "\n"
        return str

    def print(self):
        """ Prints the board to stdout """
        print(' ------------- ')
        for row in self.state:
            for col in row:
                print('|',end='')
                if col is Color.NONE:
                    print(" ", end='')
                elif col is Color.RED:
                    print("R", end='')
                elif col is Color.BLACK:
                    print("B", end='')
            print('|')
            print(' ------------- ')

class BoardTest(unittest.TestCase):
    """ Unit testing of Board class """
    
    def testLoadSave(self):
        """ Test load and save methods as well as array access """
        board = Board()
        board[5][4] = Color.RED
        board[5][3] = Color.BLACK
        board[4][3] = Color.RED
        board[3][3] = Color.BLACK
        board[2][3] = Color.BLACK
        board[1][3] = Color.RED
        self.assertEqual('000000000010000002000000200000010000002100', board.save(), 'Incorrect save value')
        board.load('122100000100000122000100020000000000002100')
        self.assertListEqual([[Color.RED, Color.BLACK, Color.BLACK, Color.RED, Color.NONE, Color.NONE, Color.NONE], [Color.NONE, Color.NONE, Color.RED, Color.NONE, Color.NONE, Color.NONE, Color.NONE], [Color.NONE, Color.RED, Color.BLACK, Color.BLACK, Color.NONE, Color.NONE, Color.NONE], [Color.RED, Color.NONE, Color.NONE, Color.NONE, Color.BLACK, Color.NONE, Color.NONE], [Color.NONE, Color.NONE, Color.NONE, Color.NONE, Color.NONE, Color.NONE, Color.NONE], [Color.NONE, Color.NONE, Color.NONE, Color.BLACK, Color.RED, Color.NONE, Color.NONE]]
                             , board.state, 'Incorrect load')

    def testDrop(self):
        """ Test dropping in a column and checking if full """
        board = Board()
        board.drop(Color.RED, 2)
        self.assertEqual('000000000000000000000000000000000000010000', board.save(), 'Incorrect board on drop')
        board.drop(Color.RED, 2)
        self.assertEqual('000000000000000000000000000000100000010000', board.save(), 'Incorrect board on drop')
        self.assertFalse(board.isFull(2))
        board.drop(Color.RED, 2)
        board.drop(Color.RED, 2)
        board.drop(Color.RED, 2)
        self.assertFalse(board.isFull(2))
        board.drop(Color.RED, 2)
        self.assertTrue(board.isFull(2))

    def testWinner(self):
        """ Test win and draw scenarios """
        board = Board()
        # row
        board[5][1] = Color.BLACK
        board[5][2] = Color.BLACK
        board[5][3] = Color.BLACK
        self.assertEqual(Color.NONE, board.winner())
        board[5][4] = Color.BLACK
        self.assertEqual(Color.BLACK, board.winner())
        # column
        board[5][2] = Color.RED
        board[4][2] = Color.RED
        board[3][2] = Color.RED
        self.assertEqual(Color.NONE, board.winner())
        board[2][2] = Color.RED
        self.assertEqual(Color.RED, board.winner())
        # diagonals
        board.clear()
        board[1][0] = Color.RED
        board[2][1] = Color.RED
        board[3][2] = Color.RED
        self.assertEqual(Color.NONE, board.winner())
        board[4][3] = Color.RED
        self.assertEqual(Color.RED, board.winner())
        board[4][3] = Color.BLACK
        self.assertEqual(Color.NONE, board.winner())
        board[5][2] = Color.BLACK
        board[3][4] = Color.BLACK
        self.assertEqual(Color.NONE, board.winner())
        board[2][5] = Color.BLACK
        self.assertEqual(Color.BLACK, board.winner())

if __name__ == "__main__":
    unittest.main()
