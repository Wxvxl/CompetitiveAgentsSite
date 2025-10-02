class Game:
    def __init__(self, agents):
        if len(agents) != 2:
            raise ValueError("Tic Tac Toe requires exactly 2 agents.")
        self.board = [" "] * 9
        self.agents = agents
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
                move = self.agents[0].move(self.board[:])  # Use agents[0]
            else:
                move = self.agents[1].move(self.board[:])  # Use agents[1]

            if move not in range(9) or self.board[move] != " ":
                # Illegal move means opponent victory.
                if self.current_player == "X":
                    return [1, 0]  # agents[1] wins, agents[0] loses
                else:
                    return [0, 1]  # agents[0] wins, agents[1] loses
                
            
            self.board[move] = self.current_player
            self.print_board()
            
            if self.is_winner(self.current_player):
                if self.current_player == "X":
                    return [0, 1]  # agents[0] wins, agents[1] loses
                else:
                    return [1, 0]  # agents[1] wins, agents[0] loses
            if self.is_full():
                return None
            
            self.current_player = "O" if self.current_player == "X" else "X"