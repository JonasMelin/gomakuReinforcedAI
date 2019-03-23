import luffPlayer
import luffVisualizer
import time


#####################################################
# Class that implements a human player, that clicks with
# a mouse in a gui..
#####################################################
class luffHumanPlayer(luffPlayer.luffPlayer):

    def __init__(self,
                 character,
                 name="noname",
                 genes=None,
                 benchmarkPlayer=False,
                 prohibitLearn=True):
        luffPlayer.luffPlayer.__init__(self,
                                       character=character,
                                       name=name,
                                       genes=genes,
                                       isHuman=True,
                                       benchmarkPlayer=benchmarkPlayer,
                                       prohibitLearn=prohibitLearn)

        self.pos = None
        self.viss = luffVisualizer.luffVisualizer()
        print("Human player created {}".format(name))

    #####################################################
    # Override this function from luffNeural
    #####################################################
    def calcOutputGetPos(self, board, availablePos, humanInvolved=False):

        self.pos = None
        self.board = board

        # This is a work-around cause in some versions it is impossible
        # to terminate the matplotlib window. Ugly as ***, but it works...
        while True:
            self.viss.plotBoard(board.cleanupBoard(board.getBoard()), sleep=2,
            name="Please click in board to make your move...", callback=self.onclick)

            if self.pos is not None:
                self.board = None
                return self.pos


    #####################################################
    # Callback when the game board is clicked by mouse
    #####################################################
    def onclick(self, event):

        if event.xdata is None or  event.ydata is None or self.board is None:
            return

        x = int(round(event.xdata))
        y = int(round(event.ydata))

        if x < 0 or y < 0:
            return

        pos = [y, x]

        if not self.board.isFree(pos):
            print("Click a free position...")
            return

        self.pos = pos







