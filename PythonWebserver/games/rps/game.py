import random

class Game:
    MOVES = ["rock", "paper", "scissors"]

    def __init__(self, agent1, agent2):
        self.agent1 = agent1
        self.agent2 = agent2
        self.symbols = {"agent1": "X", "agent2": "O"}
        self.logs = []  # Store moves and winner for each round

    def play_round(self):
        """
        Plays a single round and returns 'X' if agent1 wins,
        'O' if agent2 wins, or None for tie.
        """
        move1 = self.agent1.move()
        move2 = self.agent2.move()

        # Validate moves, if the player makes invalid move, the component wins
        if move1 not in self.MOVES:
            self.logs.append({"agent1": move1, "agent2": move2, "winner": "O"})
            return "O"
        if move2 not in self.MOVES:
            self.logs.append({"agent1": move1, "agent2": move2, "winner": "X"})
            return "X"

        # Determine winner
        if move1 == move2:
            winner_symbol = None
        elif (move1 == "rock" and move2 == "scissors") or \
             (move1 == "scissors" and move2 == "paper") or \
             (move1 == "paper" and move2 == "rock"):
            winner_symbol = "X"
        else:
            winner_symbol = "O"

        # Log the round
        self.logs.append({
            "agent1": move1,
            "agent2": move2,
            "winner": winner_symbol
        })

        return winner_symbol

    def play(self):
        """
        Plays best-of-3 rounds and returns the overall winner ('X' or 'O').
        """
        score = {"X": 0, "O": 0}
        while score["X"] < 2 and score["O"] < 2:
            winner = self.play_round()
            if winner:
                score[winner] += 1

        # Determine overall winner
        overall_winner = "X" if score["X"] == 2 else "O"
        return overall_winner
