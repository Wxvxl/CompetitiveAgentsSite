import random

class Game:
    MOVES = ["rock", "paper", "scissors"]

    def __init__(self, agents):
        if len(agents) != 2:
            raise ValueError("Rock-Paper-Scissors requires exactly 2 agents.")
        self.agents = agents
        self.logs = []   # record round details
        self.board = []  # list form of match state (copyable)
        self.round = 0

    def update_board(self):
        """Update board list for consistent backend logging."""
        self.board = []
        for i, log in enumerate(self.logs, start=1):
            winner = (
                "Agent1" if log["winner"] == [0, 1]
                else "Agent2" if log["winner"] == [1, 0]
                else "Draw"
            )
            self.board.append(
                f"Round {i}: Agent1 -> {log['agent1']} | Agent2 -> {log['agent2']} | Winner: {winner}"
            )

    def play_round(self):
        """
        Plays a single round and returns [0,1], [1,0], or None for draw.
        """
        self.round += 1
        move1 = self.agents[0].move()
        move2 = self.agents[1].move()

        # Validate moves
        if move1 not in self.MOVES:
            self.logs.append({"agent1": move1, "agent2": move2, "winner": [1, 0]})
            self.update_board()
            return [1, 0]  # agent2 wins
        if move2 not in self.MOVES:
            self.logs.append({"agent1": move1, "agent2": move2, "winner": [0, 1]})
            self.update_board()
            return [0, 1]  # agent1 wins

        # Determine winner
        if move1 == move2:
            winner = None
        elif (move1 == "rock" and move2 == "scissors") or \
             (move1 == "scissors" and move2 == "paper") or \
             (move1 == "paper" and move2 == "rock"):
            winner = [0, 1]  # agent1 wins
        else:
            winner = [1, 0]  # agent2 wins

        self.logs.append({
            "agent1": move1,
            "agent2": move2,
            "winner": winner
        })
        self.update_board()
        return winner

    def play(self):
        """
        Plays best-of-3 rounds and returns overall result:
        [0,1] if agent1 wins, [1,0] if agent2 wins, None if draw.
        """
        score = [0, 0]  # [agent1, agent2]

        while score[0] < 2 and score[1] < 2:
            winner = self.play_round()
            if winner == [0, 1]:
                score[0] += 1
            elif winner == [1, 0]:
                score[1] += 1
            # tie = do nothing

        if score[0] == 2:
            final_winner = [0, 1]
        elif score[1] == 2:
            final_winner = [1, 0]
        else:
            final_winner = None

        print("Final score:", score)
        print("Match winner:", final_winner)
        print("Match history:")
        for line in self.board:
            print(line)

        return final_winner
