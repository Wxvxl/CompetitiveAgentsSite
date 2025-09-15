import random
class C4MinimaxAgent:

    def move(self, symbol, board, last_move):
         '''
         symbol is the character that represents the agents moves in the board.
         symbol will be consistent throughout the game
         board is an array of 7 strings each describing a column of the board
         last_move is the column that the opponent last droped a piece into (or -1 if it is the firts move of the game).
         This method should return the column the agent would like to drop their token into.
         '''
         return self.minimax(symbol,board,2)[0]

    def minimax(self, symbol, board, ply):
        '''
        return a pair (move, value), 
        where move is the optimal move, that gives value.
        '''
        val = self.evaluate(symbol,board)
        if ply == 0 or val > 2**12 or val < -2**12:#terminal position
            return (None, val)
        best_move = 0
        best_value = -2**32
        for move in range(7):
            if len(board[move]) < 6:
                board[move] = board[move]+symbol
                (_,value) = self.maximin(symbol, board, ply-1)
                if value > best_value or (value == best_value and random.random() < 0.5):
                    best_value = value
                    best_move = move
                board[move] = board[move][:-1]
        return (best_move, best_value)        

    def maximin(self, symbol, board, ply):
        '''
        symbol is the symbol of this agent, (i.e. not the agent being maximized)
        '''
        val = self.evaluate(symbol, board)
        if ply == 0 or val > 2**12 or val < -2**12:#terminal position
            return (None, val)
        best_move = 0
        best_value = 2**32
        for move in range(7):
            if len(board[move]) < 6:
                board[move] = board[move]+chr(ord(symbol)+1)
                (_,value) = self.minimax(symbol, board, ply-1)
                if value < best_value or (value == best_value and random.random() < 0.5):
                    best_value = value
                    best_move = move
                board[move] = board[move][:-1]
        return (best_move, best_value)        

    def evaluate(self, symbol, board):
        '''
        evaluates the quality of the board for the agent represented by symbol.
        The evaluation metric is: 
        sum_{viable symb fours: f} e(f) - sum_viable opp fours:f} e(f), 
        where e(f) is 1,3,6,400 if there are 1,2,3,4 tokens on the four.
        Higher values are better.
        '''
        dirs = [(0,1),(1,1),(1,0),(1,-1)]
        payoffs = [0,1,3,6,2**16]
        (sym_val,other_val) = (0,0)
        for i in range(7):
            for j in range(6):
                for (x,y) in dirs:
                    (sym_count,other_count) = (0,0)
                    k = 0
                    while i+k*x < 7 and j+k*y < 6 and j+k*y >= 0 and k < 4: 
                        if j+k*y < len(board[i+k*x]):
                            if board[i+k*x][j+k*y] == symbol: sym_count = sym_count+1
                            else: other_count = other_count+1
                        k += 1
                    if k == 4 and other_count == 0: sym_val += payoffs[sym_count]
                    if k == 4 and sym_count == 0: other_val += payoffs[other_count]
        return sym_val - other_val