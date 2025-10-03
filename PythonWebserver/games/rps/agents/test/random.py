import random

class RandomAgent:
    name = "RandomAgent"

    def move(self):
        return random.choice(["rock", "paper", "scissors"])
