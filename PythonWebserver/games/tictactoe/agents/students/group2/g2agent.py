class TTTAgent:
    def move(self, board):
        for i, v in enumerate(board):
            if v == " ":
                return i