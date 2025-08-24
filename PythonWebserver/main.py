import random

class RockPaperScissorGame:
    result_dict = {
        "r" : "s",
        "s" : "p",
        "p" : "r"
    }
    
    def __init__(self):
        pass
    
    def assignPlayers(self, player1, player2):
        self.agent1 = player1
        self.agent2 = player2
    
    def startGame(self, roundCount):
        agent1_score = 0
        agent2_score = 0
        for i in range(roundCount):
            round_result = 0
            agent1_action = self.agent1.getAction()
            agent2_action = self.agent2.getAction()

            if self.result_dict[agent1_action] == agent2_action:
                agent1_score += 1
            elif self.result_dict[agent2_action] == agent1_action:
                agent2_score += 1
            else:
                pass
        if agent1_score > agent2_score:
            print("agent 1 win")
        elif agent1_score < agent2_score:
            print("agent 2 win")
        else:
            print('tie')
    
def main():
    agent1 = RandomAgents()
    agent2 = RandomAgents()
    game = RockPaperScissorGame()
    
    game.assignPlayers(agent1, agent2)
    game.startGame(5)
main()
    