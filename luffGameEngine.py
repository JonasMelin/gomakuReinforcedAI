import luffGameBoard
import definitions as defs
import luffPlayer as player
import numpy as np
import sys
import random


# ################################################################
# Class that executes one game of luff with two players.
# It also makes sure to train the loosing player after the game
# so it gets better for future games.
# ################################################################
class luffGameEngine(object):

    # ################################################################
    # Constructor
    # ################################################################
    def __init__(self):
        self.defs = defs.definitions()
        pass

    # ################################################################
    # Performs one game between player 1 and 2.
    # ################################################################
    def runNewGame(self,
                   player1,
                   player2,
                   useAllAvailPos=False,
                   randomRate=0,
                   startRandom=0,
                   statsFromAllMatches=True,
                   verbose=True):


        self.defs.timeDiffStart()

        board = luffGameBoard.luffGameBoard()
        currentPlayer = player1
        gameStepCounter = 0
        benchmark = False

        if player1.isBenchmark() or player2.isBenchmark():
            benchmark = True

        while True:

            gameStepCounter += 1
            currentPlayer, notCurrentPlayer = self.getNextPlayer(currentPlayer, player1, player2)
            if useAllAvailPos:
                availablePos = board.getAllfreePositions()
            else:
                availablePos = board.getInterestingPositions()

            if len(availablePos) == 0:
                print("BOARD FULL!!")
                board.resetBoard()
                return

            if len(availablePos) == 1:
                board.setCharacter(availablePos[0], currentPlayer.getPlayerChar())
                continue

            if self.doRandMove(randomRate) or (gameStepCounter < startRandom):
                pos = availablePos[random.randint(0, len(availablePos) -1)]
            else:
                pos = currentPlayer.calcOutputGetPos(board, availablePos)

            winner = board.setCharacter(pos, currentPlayer.getPlayerChar())

            if winner:
                # The current player just won. So, train the looser according to the winning game
                # But only train if not a benchmark match..
                if not benchmark:
                    notCurrentPlayer.learnHistory(board.getEntireGameHistory(), currentPlayer.getPlayerChar())

                # statsFromAllMatches == False, means only stats when we meet
                # a benchmark player is recorded
                if statsFromAllMatches or benchmark:
                    notCurrentPlayer.gameFinished(won=False)
                    currentPlayer.gameFinished(won=True)
                    currentPlayer.storeGameLength(gameStepCounter)
                    notCurrentPlayer.storeGameLength(gameStepCounter)

                board.resetBoard()

                if verbose:
                    print("Game: {a:<8} vs {b:<8} Winner: {c:<8} GameLength: {d: 3d}, WinRatio: {e:.2f}, randomRate: {g: 3d}, startRandom: {h: 3d}, allAvail: {f}, playTime: {i:.2f}s".format(
                        a=player1.getName(),
                        b=player2.getName(),
                        c=currentPlayer.getName(),
                        d=gameStepCounter,
                        e=currentPlayer.getWinRate(),
                        f=useAllAvailPos,
                        g=randomRate,
                        h=startRandom,
                        i=self.defs.timeDiffEnd()))
                    sys.stdout.flush()
                return

    # ################################################################
    # True/False if we shall do a random move
    # ################################################################
    def doRandMove(self, randomRate):

        if randomRate == 0:
            return False

        if random.randint(0,randomRate) == 0:
            return True
        else:
            return False



    # ################################################################
    # Toggles the current player X/O
    # ################################################################
    def getNextPlayer(self, currentPlayer, player1, player2):

        if currentPlayer == player1:
            currentPlayer = player2
            notCurrentPlayer = player1
        else:
            currentPlayer = player1
            notCurrentPlayer = player2

        return currentPlayer, notCurrentPlayer
