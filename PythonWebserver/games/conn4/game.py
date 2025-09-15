import random
class Game:
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