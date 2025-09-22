import random

class RandomAgent:
    def move(self, board):
        available = [i for i, v in enumerate(board) if v == " "]
        return random.choice(available)