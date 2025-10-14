class RPSAgent:
    name = "RPSAgent"

    def __init__(self):
        # Optional: you could use this to cycle through moves
        self.moves = ["scissors","rock", "paper"]
        self.index = 0

    def move(self):

         move = self.moves[self.index]
         self.index = (self.index + 1) % len(self.moves)
         return move
