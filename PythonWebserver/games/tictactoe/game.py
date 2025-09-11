class Game:
    def __init__(self, agent1, agent2):
        self.board = [" "] * 9
        self.agent1 = agent1
        self.agent2 = agent2
        self.current_player = "X"
        
    def print_board(self):
        for i in range(0, 9, 3):
            print(self.board[i:i+3])
        print()

    def is_winner(self, player):
        wins = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # columns
            [0, 4, 8], [2, 4, 6]              # diagonals
        ]
        for combo in wins:
            winner = True
            for i in combo:
                if self.board[i] != player:
                    winner = False
                    break
            if winner:
                return True
        return False
    def is_full(self):
        return all(cell != " " for cell in self.board)

    def play(self):
        while True:
            if self.current_player == "X":
                # Pass a copy for the move command so agents dont mutate the original board. 
                move = self.agent1.move(self.board[:], "X")
            else:
                move = self.agent2.move(self.board[:], "O")

            if move not in range(9) or self.board[move] != " ":
                # Illegal move means opponent victory.
                return "O" if self.current_player == "X" else "X"
            
            self.board[move] = self.current_player
            self.print_board()
            
            if self.is_winner(self.current_player):
                return self.current_player
            if self.is_full():
                return None
            
            self.current_player = "O" if self.current_player == "X" else "X"