import random
class C4Agent:
     def move(self, symbol, board, last_move):
         '''
         symbol is the character that represents the agents moves in the board.
         symbol will be consistent throughout the game
         board is an array of 7 strings each describing a column of the board
         last_move is the column that the opponent last droped a piece into (or -1 if it is the firts move of the game).
         This method should return the column the agent would like to drop their token into.
         '''
         col = -1
         while col<0  or len(board[col])>5:
             col = random.randint(0,6) 
         return col
