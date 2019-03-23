import luffPlayer

#####################################################
# Implements a player that plays strictrly according
# to the "Q-rule", pritty much a simple algortim
# that builds tokens in a straight line or close
# to other similar tokens.
#####################################################
class luffQValuePlayer(luffPlayer.luffPlayer):

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

        assert len(availablePos) > 0

        highestVal = 0
        bestPos = availablePos[0]

        for nextPos in availablePos:
            rankX, rankO = board.rankPosition(nextPos, board.getBoard())
            totScore = rankX + rankO

            if totScore > highestVal:
                highestVal = totScore
                bestPos = nextPos

        return bestPos
