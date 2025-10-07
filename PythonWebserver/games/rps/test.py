from game import Game
from agents.test.rockagent import RockAgent
from agents.test.random import RandomAgent

if __name__ == "__main__":
    agents = [
        ("RockAgent", RockAgent),
        ("RandomAgent", RandomAgent)
    ]

    for i in range(len(agents)):
        for j in range(len(agents)):
            if i == j:
                continue
            name1, agent1 = agents[i]
            name2, agent2 = agents[j]
            print(f"Match: {name1} (agent1) vs {name2} (agent2)")
            game = Game([agent1(), agent2()])
            result = game.play()
            if result is None:
                print("Result: Draw")
            elif result == [0, 1]:
                print(f"Winner: {name1}")
            else:
                print(f"Winner: {name2}")
            print("Logs:", game.logs, "\n")
