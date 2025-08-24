from baseclass import Agents
import random

class RandomAgents(Agents):
    choices = ["r", "p", "s"]
    def __init__(self):
        super().__init__()
    
    def getAction(self):
        return self.choices[random.randint(0,2)]