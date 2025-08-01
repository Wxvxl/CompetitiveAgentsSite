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
        for i in range(roundCount):
            round_result = 0
            agent1_action = self.agent1.getAction()
            agent2_action = self.agent2.getAction()

            if self.result_dict[agent1_action] == agent2_action:
                round_result = 1
            elif self.result_dict[agent2_action] == agent1_action:
                round_result = 2
            else:
                round_result = 3
            