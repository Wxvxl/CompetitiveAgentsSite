
from game import Game
import random

# Define some agents
class RandomAgent:
    def move(self, board):
        available = [i for i, v in enumerate(board) if v == " "]
        return random.choice(available)

class FirstAvailableAgent:
    def move(self, board):
        for i, v in enumerate(board):
            if v == " ":
                return i

class CenterFirstAgent:
    def move(self, board):
        if board[4] == " ":
            return 4
        for i, v in enumerate(board):
            if v == " ":
                return i

# Run Tic Tac Toe Tests
if __name__ == "__main__":
    print("Testing Tic Tac Toe game\n")

    agents = [
        ("Random", RandomAgent()),
        ("FirstAvailable", FirstAvailableAgent()),
        ("CenterFirst", CenterFirstAgent())
    ]

    # Play each agent vs each other
    for i in range(len(agents)):
        for j in range(len(agents)):
            if i == j:
                continue  # skip mirror matches
            name1, agent1 = agents[i]
            name2, agent2 = agents[j]
            print(f"{name1} (X) vs {name2} (O)")
            game = Game(agent1, agent2)
            winner = game.play()
            print("Winner:", winner, "\n")