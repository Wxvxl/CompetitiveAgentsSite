import unittest, random

from connect4 import C4Agent

class TestConnect4(unittest.TestCase):
    def test1(self):
        print("--------------------------------------------")
        print("TEST 1: Your Agent VS Random Agent")
        for i in range(4):
            print("----------------------")
            print("Round {}:".format(i+1))
            agent1 = C4Agent() # X
            agent2 = C4RandomAgent() # O
            game = Connect4Game(agent1,agent2)
            winner = game.play()
            message = "?"
            if winner == 'O':
                message = 'Random agent won. Test Failed'
                print(message)
                print("----------------------")
            elif winner == None:
                message = 'Game Drawn. Test Failed'
                print(message)
                print("----------------------")
            self.assertEqual(winner, "X", message)
        print("----------------------")
        print('Won 4/4. Test Passed')
     
    def test2(self):
        print()
        print("--------------------------------------------")
        print("TEST 2: Your Agent VS 2-Ply Minimax Agent")
        won = 0
        for i in range(2):
            print("----------------------")
            print("Round {}:".format(i+1))
            agent1 = C4Agent() # X
            agent2 = C4MinimaxAgent() # O
            game = Connect4Game(agent1,agent2)
            if game.play() == 'O':
                print('Agent Lost.')
            elif game.winner==None:
                print('Game Drawn.')
                won += 0.5
            else: 
                print('Agent Won.')
                won += 1
        print("----------------------")
        self.assertGreaterEqual(won, 1, "Agent lost. Test Failed")
        print('Test Passed')

class Connect4Game:

    def __init__(self, agent1, agent2):
        '''
        Creates a new game with an instances of agent1_cls and agents2_cls
        '''
        self.agents = [agent1, agent2]
        self.board = ['','','','','','','']
        self.move_order = ['','','','','','','']
        self.winner = None

    def play(self):
        '''
        Plays the game by interleaving moves from agent1 and agent2
        '''
        current = 0 if random.random() < 0.5 else 1
        symbols = ['X','O']
        counters = ['A','a']
        last_move = -1 
        while not self.game_over():
            last_move = self.agents[current].move(symbols[current], self.board.copy(), last_move)
              
            if last_move < 7 and last_move >= 0 and len(self.board[last_move]) < 6:
                #legit move
                self.board[last_move] = self.board[last_move] + symbols[current]
                self.move_order[last_move] = self.move_order[last_move] + counters[current]
                counters[current] = chr(ord(counters[current])+1)
                current = (current + 1) %2
            else:
                print('Illegal move. Game over')
                self.winner = symbols[(current + 1) %2]
        if self.winner==None:
            print('Game Drawn')
        else:    
            print('Game over,', self.winner, 'won.')
        print('Final board\n', self.board_string())
        return self.winner

    def board_string(self):
        s = ''
        for j in range(6,-1,-1):
            for i in range(7):
                s +=  ' ' if j>=len(self.move_order[i]) else self.move_order[i][j]
            s+='\n'
        return s        

    def game_over(self):
        '''Tests winning condition'''
        if self.winner is not None:
            return True
        dirs = [(0,1),(1,1),(1,0),(1,-1)]
        for i in range(7):
            for j in range(len(self.board[i])):
                symb = self.board[i][j]
                for (x,y) in dirs:
                    k = 1
                    while i+k*x < 7 and j+k*y < len(self.board[i+k*x]) and j+k*y>=0 and self.board[i+k*x][j+k*y]==symb:
                        k += 1
                        if k == 4: 
                            self.winner = symb
                            return True
        if all([len(col)==6 for col in self.board]):
            return True
        return False

class C4RandomAgent:
     
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

########################################################################
# SPOILERS!!!                                                          #
# Do not read the code below here until you have finished this lab.    #
# You should solve the problem yourself without reading this solution. #
########################################################################

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

if __name__ == "__main__":
    unittest.main()
