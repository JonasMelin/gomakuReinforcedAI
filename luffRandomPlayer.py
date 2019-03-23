import luffPlayer
import random

#####################################################
# Implements a luff player that plays totally random..
#####################################################
class luffRandomPlayer(luffPlayer.luffPlayer):

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
                                       benchmarkPlayer=benchmarkPlayer,
                                       prohibitLearn=prohibitLearn)

    #####################################################
    # Override this function from luffNeural
    #####################################################
    def calcOutputGetPos(self, board, availablePos, humanInvolved=False):
        maxIndex = len(availablePos) - 1
        randPos = random.randint(0, maxIndex)

        return availablePos[randPos]

