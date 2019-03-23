import numpy
import definitions
import luffVisualizer as plt
import random


# ################################################################
# Class that holds the game board, and the entire history for it
# since it was created, and all types of support functions, such as rotate it
# look for a winner etc.
# The idea is that the game board data cannot be altered from
# outside of this class, only different copies can be retreived.
# The only way to update the board is by setting a character or
# by resetting it.
# ################################################################
class luffGameBoard(object):

    # ################################################################
    # Constructor
    # ################################################################
    def __init__(self, board=None):
        self.defs = definitions.definitions()

        self.resetBoard()

        if board is not None:
            self.board = board
            self.historyCounter = 2


    # ################################################################
    # Sets a character in the game board. Exception if already taken
    # or out of bounds. The history of the game board is incremented one
    # ################################################################
    def setCharacter(self, pos, character):

        #dont set an empty character, or out of bounds
        assert self.validPos(pos)
        assert not self.compareCharacter(character, self.defs.characterNone)

        # check that the position is free
        if not self.isFree(pos):
            raise Exception("position already taken!!")

        # set the character in the board
        self.board[pos[0], pos[1]] = character
        self._updateInterestingPos(pos)

        # Store the history
        nextEntry = {}
        nextEntry['board'] = self.getCopyOfBoard()
        nextEntry['movePos'] = pos
        nextEntry['characterSet'] = character
        nextEntry['moveNo'] = self.historyCounter
        nextEntry['WinningMove'] = False
        self.history.append(nextEntry)
        self.historyCounter += 1


        if self.countConsequentChars(pos, self.defs.characterX) >= 5:
            nextEntry['WinningMove'] = True
            return True
        if self.countConsequentChars(pos, self.defs.characterO) >= 5:
            nextEntry['WinningMove'] = True
            return True

        return False

    # ################################################################
    # Updates the matrix of the interesting positions, where interesting
    # positions are those that borderes to a set character.
    # ################################################################
    def _updateInterestingPos(self, pos, board=None):

        if board is None:
            board = self.board

        for a in range(3):
            for b in range(3):
                next_a = pos[0] + a - 1
                next_b = pos[1] + b - 1

                if not self.validPos([next_a, next_b]):
                    continue # Only if valid..
                if not self.isFree([next_a, next_b]):
                    continue # only if free
                board[next_a, next_b] = self.defs.characterInteresting

    # ################################################################
    # Return a copy of the current game board,
    # or optionally instead makes a copy of the provided board
    # ################################################################
    def getCopyOfBoard(self, board=None):

        if board is None:
            board = self.board

        return numpy.copy(board)

    # ################################################################
    # Return a copy of the current game board
    # ################################################################
    def getBoard(self):
        return numpy.copy(self.board)

    # ################################################################
    # Returns character in current position
    # ################################################################
    def getCharacter(self, pos, board=None):

        if board is None:
            board = self.board

        return board[pos[0], pos[1]]

    # ################################################################
    # Creates a new, empty board and returns it.
    # ################################################################
    def createEmptyBoard(self, initVal=None):
        # Create an empty board
        newBoard = numpy.empty(shape=[self.defs.boardSize, self.defs.boardSize])

        if initVal is None:
            newBoard.fill(self.defs.characterNone)
        else:
            newBoard.fill(initVal)
        return newBoard

    # ################################################################
    # Returns a random board...
    # ################################################################
    def getRandomBoard(self, lessNoise=False):
        newBoard = self.createEmptyBoard()

        if lessNoise:
            fillCount = random.randint(1, int(self.defs.boardSize * self.defs.boardSize / 3))
        else:
            fillCount = random.randint(1, self.defs.boardSize * self.defs.boardSize - 5)

        counter = 0

        for a in range(self.defs.boardSize):
            for b in range(self.defs.boardSize):
                counter += 1
                randomPos = self.getRandomValidPos()
                randomChar = self.getRandomCharacter()
                newBoard[randomPos[0], randomPos[1]] = randomChar

                if counter > fillCount:
                    return newBoard


    # ################################################################
    # return a random position in the board
    # ################################################################
    def getRandomValidPos(self):
        return [random.randint(0,self.defs.boardSize - 1),
                random.randint(0,self.defs.boardSize - 1)]

    # ################################################################
    # return a random character O/X
    # ################################################################
    def getRandomCharacter(self):
        if random.randint(0,1) == 1:
            return self.defs.characterX
        else:
            return self.defs.characterO

    # ################################################################
    # Resets the board to empty, and resets all recorded history
    # ################################################################
    def resetBoard(self):

        # create a list of history
        self.history = []
        nextEntry = {}
        self.historyCounter = 0

        # Create an empty board
        self.board = self.createEmptyBoard()

        nextEntry['board'] = self.getCopyOfBoard()
        nextEntry['movePos'] = [None, None]
        nextEntry['characterSet'] = self.defs.characterNone
        nextEntry['moveNo'] = self.historyCounter

        self.history.append(nextEntry)

        self.historyCounter += 1

    # ################################################################
    # Returns the entire history of the game since it was reset last
    # Returned as an array of np arrays. Note that the first, empty
    # board is included in the history..
    # ################################################################
    def getEntireGameHistory(self):
        return self.history

    # ################################################################
    # Return the lenght of the history, e.g. how many times has
    # setCharacter() been called
    # ################################################################
    def getHistoryLength(self):
        assert self.historyCounter == len(self.history)
        return self.historyCounter

    # ################################################################
    # True if characters are the same, False else.
    # ################################################################
    def compareCharacter(self, charA, charB):
        diff = 0.1
        return self.inrange(charA,charB-diff, charB+diff)

    # ################################################################
    # True if is in range of the low/high value
    # ################################################################
    def inrange(self, val, low, high):
        if (val >= low) and (val <= high):
            return True
        else:
            return False

    # ################################################################
    # True if the position is in valid range within the game board
    # ################################################################
    def validPos(self, pos):
        return self.inrange(pos[0], 0, self.defs.boardSize-1) and self.inrange(pos[1], 0, self.defs.boardSize-1)

    # ################################################################
    # True if the position is free
    # ################################################################
    def isFree(self, pos):

        return self.compareCharacter(self.getCharacter(pos), self.defs.characterNone) or \
               self.compareCharacter(self.getCharacter(pos), self.defs.characterInteresting)

    # ################################################################
    # True if pos touches a set position, e.g. where someone has set a
    # character already.
    # ################################################################
    def isPositionCloseToOther(self, pos):

        for a in range(3):
            for b in range(3):
                nextTestPos = [pos[0]+a-1, pos[1]+b-1]
                if not self.validPos(nextTestPos):
                    continue
                if (pos[0] == nextTestPos[0]) and (pos[1] == nextTestPos[1]):
                    # This is ourselves. Dont look at this position..
                    continue
                if not self.isFree(nextTestPos):
                    # We found a neighbour!
                    return True

        return False

    # ################################################################
    # Returns a coordinate list of interesting positions, those
    # are positions worth investigating as potential places to put
    # next character in. They boarder an already set character (except
    # if board is empty, then you get the center coordinate)
    # ################################################################
    def getInterestingPositions(self):

        retList = []

        if self.historyCounter == 1:
            retList.append(self.getCenterCoord())
            return retList

        for a in range(self.defs.boardSize):
            for b in range(self.defs.boardSize):
                if self.compareCharacter(self.getCharacter([a,b]),self.defs.characterInteresting):
                    retList.append([a, b])

        random.shuffle(retList)

        return retList

    # ################################################################
    # Returns a coordinate list of all free positions. If the board
    # is empty you will only get the center coordinate
    # ################################################################
    def getAllfreePositions(self):

        retList = []

        if self.historyCounter == 1:
            retList.append(self.getCenterCoord())
            return retList

        for a in range(self.defs.boardSize):
            for b in range(self.defs.boardSize):
                if self.isFree([a,b]):
                    retList.append([a, b])

        random.shuffle(retList)

        return retList

    # ################################################################
    # Returns a coordinate list of all free positions. If the board
    # is empty you will only get the center coordinate.
    # Raw means it will not use optimization to get the pos, it
    # will check through entire board from scratch
    # ################################################################
    def getInterestingPositionsRAW(self):

        retList = []

        if self.historyCounter == 1:
            retList.append(self.getCenterCoord())
            return retList

        for a in range(self.defs.boardSize):
            for b in range(self.defs.boardSize):
                if self.isFree([a,b]):
                    if self.isPositionCloseToOther([a,b]):
                        retList.append([a, b])

        random.shuffle(retList)

        return retList

    # ################################################################
    # Scans consequent characters in a row in a given position.
    # ToDo: yes, optimize all this..
    # ################################################################
    def countConsequentChars(self, pos, char):

        for r in range(4):
            conseqCounter = 0

            for a in range(9):

                if r is 0:
                    checkPos = [pos[0] + a - 4, pos[1]]
                if r is 1:
                    checkPos = [pos[0], pos[1] + a - 4]
                if r is 2:
                    checkPos = [pos[0] + a - 4, pos[1] + a - 4]
                if r is 3:
                    checkPos = [pos[0] - a + 4, pos[1] + a - 4]

                if not self.validPos(checkPos):
                    continue
                if self.compareCharacter(char, self.getCharacter(checkPos)):
                    conseqCounter += 1
                else:
                    conseqCounter = 0
                    continue

                if conseqCounter >= 5:
                    return conseqCounter

        return 0

    # ################################################################
    # Gives a rank of how good a position is for both players.
    # This algoritm is used for the QPlayer to select next move...
    # ################################################################
    def rankPosition(self, pos, board=None):

        if board is None:
            board = self.board

        totScoreX = 0
        totScoreO = 0

        for r in range(8):
            conseqCounterX = 0
            conseqCounterO = 0
            xCounterStop = False
            oCounterStop = False

            for a in range(4):

                if r is 0:
                    checkPos = [pos[0] + a + 1, pos[1]]
                if r is 1:
                    checkPos = [pos[0] - a - 1, pos[1]]
                if r is 2:
                    checkPos = [pos[0]        , pos[1] + a + 1]
                if r is 3:
                    checkPos = [pos[0]        , pos[1] - a - 1]
                if r is 4:
                    checkPos = [pos[0] + a + 1, pos[1] + a + 1]
                if r is 5:
                    checkPos = [pos[0] - a - 1, pos[1] - a - 1]
                if r is 6:
                    checkPos = [pos[0] + a + 1, pos[1] - a - 1]
                if r is 7:
                    checkPos = [pos[0] - a - 1, pos[1] + a + 1]

                if not self.validPos(checkPos):
                    continue
                if self.compareCharacter(self.defs.characterX, self.getCharacter(checkPos, board)):
                    if not xCounterStop:
                        conseqCounterX += 1
                    oCounterStop = True
                else:
                    xCounterStop = True

                if self.compareCharacter(self.defs.characterO, self.getCharacter(checkPos, board)):
                    if not oCounterStop:
                        conseqCounterO += 1
                    xCounterStop = True
                else:
                    oCounterStop = True

                if oCounterStop and xCounterStop is True:
                    break

            totScoreX += (conseqCounterX * conseqCounterX)  # Premiere long sequences. Square it
            totScoreO += (conseqCounterO * conseqCounterO)  # Premiere long sequences. Square it

        return totScoreX, totScoreO

    # ################################################################
    # Returns the coordinate of the center of the board
    # ################################################################
    def getCenterCoord(self):
        return [round((definitions.definitions().boardSize -1) / 2), round((definitions.definitions().boardSize -1) / 2)]

    # ################################################################
    # Offsets the inputted board to the offset position, e.g. the
    # offset position will be centered in the returned board.
    # Returns a copy of the board!!
    # ################################################################
    def offsetBoard(self, offsetToThisPos, board):

        centerCoord = self.getCenterCoord()

        newBoard = self.createEmptyBoard()
        offset_a = centerCoord[0] - offsetToThisPos[0]
        offset_b = centerCoord[1] - offsetToThisPos[1]

        for a in range(self.defs.boardSize):
            for b in range(self.defs.boardSize):
                posToSet = [a + offset_a, b + offset_b]
                posToPick = [a, b]

                if self.validPos(posToSet) and self.validPos(posToPick):
                    newBoard[posToSet[0], posToSet[1]] = board[posToPick[0], posToPick[1]]

        return newBoard

    # ################################################################
    # Returns a copy of the board, that is rotated 90 degrees
    # n number of times.
    # ################################################################
    def rotateBoard(self, board, n):

        copy = self.getCopyOfBoard(board=board)

        return numpy.rot90(copy, n)

    # ################################################################
    # Returns a copy of the board with all metadata cleaned, e.g.
    # interesting positions...
    # ################################################################
    def cleanupBoard(self, board):
        copy = self.getCopyOfBoard(board=board)

        for a in range(self.defs.boardSize):
            for b in range(self.defs.boardSize):
                if self.compareCharacter(copy[a, b], self.defs.characterInteresting):
                    copy[a,b] = self.defs.characterNone

        return copy

    # ################################################################
    # Returns a copy of the board with the characters inverted...
    # ################################################################
    def invertBoard(self, board):
        copy = self.getCopyOfBoard(board=board)

        for a in range(self.defs.boardSize):
            for b in range(self.defs.boardSize):
                if self.compareCharacter(copy[a, b], self.defs.characterO):
                    copy[a,b] = self.defs.characterX
                    continue
                if self.compareCharacter(copy[a, b], self.defs.characterX):
                    copy[a,b] = self.defs.characterO
                    continue

        return copy

    # ################################################################
    # Returns a copy of the board, that is flipped Horizontally
    # ################################################################
    def flipBoardH(self, board):

        copy = self.getCopyOfBoard(board=board)

        return numpy.fliplr(copy)

    # ################################################################
    # Returns a copy of the board, that is flipped Vertically
    # ################################################################
    def flipBoardV(self, board):

        copy = self.getCopyOfBoard(board=board)

        return numpy.flipud(copy)


# ################################################################
# Function to test my own functions...
# ################################################################
def testMyself():
    board = luffGameBoard()
    plot = plt.luffVisualizer()

    assert board.getHistoryLength() == 1 # Note: The first empty board is the first entry in history..

    interestingPos = board.getInterestingPositions()

    # Because game board is empty, only the center position should be returned.
    assert len(interestingPos) == 1
    assert interestingPos[0][0] == round(board.getCenterCoord()[0])
    assert interestingPos[0][1] == round(board.getCenterCoord()[1])

    board.setCharacter([0,0],definitions.definitions().characterX)
    assert board.getHistoryLength() == 2

    interestingPos = board.getInterestingPositions()
    assert len(interestingPos) == 3

    try:
        board.setCharacter([0, 0], definitions.definitions().characterY)
        print("FAILED 1. setting same position twice should fail")
        exit(1)
    except:
        print("Pass 1")
    assert board.getHistoryLength() == 2

    try:
        board.setCharacter([definitions.definitions().boardSize, 0], definitions.definitions().characterX)
        print("FAILED 2:. out of bounds should fail")
        exit(2)
    except:
        print("Pass 2")
    assert board.getHistoryLength() == 2

    if board.compareCharacter(definitions.definitions().characterX, board.getCharacter([0,0])):
        print("Pass 3")
    else:
        print("FAILED 3: ")
        exit(3)

    board.setCharacter([0, 1], definitions.definitions().characterO)
    assert board.getHistoryLength() == 3

    interestingPos = board.getInterestingPositions()
    assert len(interestingPos) == 4

    # Make sure there has been two moves
    history = board.getEntireGameHistory()
    assert len(history) == 3

    # Check history, before any moves..
    assert board.compareCharacter(history[0]['board'][0][0], definitions.definitions().characterNone)
    assert board.compareCharacter(history[0]['board'][0][1], definitions.definitions().characterNone)
    assert board.compareCharacter(history[0]['board'][1][0], definitions.definitions().characterNone)

    # Check history, after first move
    assert board.compareCharacter(history[1]['board'][0][0], definitions.definitions().characterX)
    assert board.compareCharacter(history[1]['board'][0][1], definitions.definitions().characterNone) or \
           board.compareCharacter(history[1]['board'][0][1], definitions.definitions().characterInteresting)
    assert board.compareCharacter(history[1]['board'][1][0], definitions.definitions().characterNone) or \
           board.compareCharacter(history[1]['board'][1][0], definitions.definitions().characterInteresting)

    # Check history, after second move
    assert board.compareCharacter(history[2]['board'][0][0], definitions.definitions().characterX)
    assert board.compareCharacter(history[2]['board'][0][1], definitions.definitions().characterO)
    assert board.compareCharacter(history[2]['board'][1][0], definitions.definitions().characterNone) or \
           board.compareCharacter(history[2]['board'][1][0], definitions.definitions().characterInteresting)

    plot.plotBoard(history[0]['board'], name="History: move # {a} pos {b} char {c}".format(a=history[0]['moveNo'], b=history[0]['movePos'], c=history[0]['characterSet']))
    plot.plotBoard(history[1]['board'], name="History: move # {a} pos {b} char {c}".format(a=history[1]['moveNo'], b=history[1]['movePos'], c=history[1]['characterSet']))
    plot.plotBoard(history[2]['board'], name="History: move # {a} pos {b} char {c}".format(a=history[2]['moveNo'], b=history[2]['movePos'], c=history[2]['characterSet']))

    print("Pass 4")

    # Test offsetting
    offsetArroundHere = [0,0]
    nextToOffset = [0, 1]

    offsettedBoard = board.offsetBoard(offsetArroundHere, board.getBoard())
    board.rotateBoard(offsettedBoard, 1)  # Shall not affect the board!! It works on a copy

    assert board.compareCharacter(offsettedBoard[board.getCenterCoord()[0],board.getCenterCoord()[1]],
                                  board.getCharacter(offsetArroundHere))
    assert board.compareCharacter(offsettedBoard[board.getCenterCoord()[0],board.getCenterCoord()[1]],
                                  definitions.definitions().characterX)
    assert board.compareCharacter(offsettedBoard[board.getCenterCoord()[0] + nextToOffset[0], board.getCenterCoord()[1] + nextToOffset[1]],
                                  board.getCharacter(nextToOffset))
    assert board.compareCharacter(offsettedBoard[board.getCenterCoord()[0] + nextToOffset[0], board.getCenterCoord()[1] + nextToOffset[1]],
                                  definitions.definitions().characterO)

    plot.plotBoard(offsettedBoard, name="offset")


    print("Pass 5")

    # Rotate the offcentered board arround its center.
    rotatedBoard = board.rotateBoard(offsettedBoard, 1)
    nextToOffsetAfterRotate = [-1, 0]

    # The center should be unchanged!
    assert board.compareCharacter(rotatedBoard[board.getCenterCoord()[0],board.getCenterCoord()[1]],
                                  board.getCharacter(offsetArroundHere))
    assert board.compareCharacter(rotatedBoard[board.getCenterCoord()[0],board.getCenterCoord()[1]],
                                  definitions.definitions().characterX)
    # But the O character should have been rotated 90deg around the center
    assert board.compareCharacter(rotatedBoard[board.getCenterCoord()[0] + nextToOffsetAfterRotate[0], board.getCenterCoord()[1] + nextToOffsetAfterRotate[1]],
                                  board.getCharacter(nextToOffset))
    assert board.compareCharacter(rotatedBoard[board.getCenterCoord()[0] + nextToOffsetAfterRotate[0], board.getCenterCoord()[1] + nextToOffsetAfterRotate[1]],
                                  definitions.definitions().characterO)

    plot.plotBoard(rotatedBoard, name="rotated 90")


    print("Pass 6")

    flippedBoard = board.flipBoardV(rotatedBoard)
    nextToOffsetAfterFlipH = [1, 0]

    # The center should be unchanged!
    assert board.compareCharacter(flippedBoard[board.getCenterCoord()[0],board.getCenterCoord()[1]],
                                  board.getCharacter(offsetArroundHere))
    assert board.compareCharacter(flippedBoard[board.getCenterCoord()[0],board.getCenterCoord()[1]],
                                  definitions.definitions().characterX)
    # But the O character should have been flipped horizontally around the center
    assert board.compareCharacter(flippedBoard[board.getCenterCoord()[0] + nextToOffsetAfterFlipH[0], board.getCenterCoord()[1] + nextToOffsetAfterFlipH[1]],
                                  board.getCharacter(nextToOffset))
    assert board.compareCharacter(flippedBoard[board.getCenterCoord()[0] + nextToOffsetAfterFlipH[0], board.getCenterCoord()[1] + nextToOffsetAfterFlipH[1]],
                                  definitions.definitions().characterO)

    plot.plotBoard(flippedBoard, name="flipped Vertical")

    print("Pass 7")

    flippedBoard = board.flipBoardH(rotatedBoard)
    plot.plotBoard(flippedBoard, name="flipped Horizontal")

    print("Pass 8")

    board.resetBoard()

    assert board.getHistoryLength() == 1

    # Make sure there has been two moves
    history = board.getEntireGameHistory()
    assert len(history) == 1

    # Check history, after first move
    assert board.compareCharacter(history[0]['board'][0][0], definitions.definitions().characterNone)
    assert board.compareCharacter(history[0]['board'][0][1], definitions.definitions().characterNone)
    assert board.compareCharacter(history[0]['board'][1][0], definitions.definitions().characterNone)
    plot.plotBoard(history[0]['board'], name="reset board")

    print("Pass 9")

    board.setCharacter([3, 4], definitions.definitions().characterX)
    board.setCharacter([3, 5], definitions.definitions().characterX)
    board.setCharacter([3, 6], definitions.definitions().characterX)
    winner, who = board.setCharacter([3, 7], definitions.definitions().characterX)
    assert not winner
    winner, who = board.setCharacter([3, 8], definitions.definitions().characterX)

    plot.plotBoard(board.getBoard())
    assert winner
    assert board.compareCharacter(who, definitions.definitions().characterX)

    print("Pass 10")
    board.resetBoard()

    board.setCharacter([1, 4], definitions.definitions().characterO)
    board.setCharacter([2, 4], definitions.definitions().characterO)
    board.setCharacter([3, 4], definitions.definitions().characterO)
    winner, who = board.setCharacter([4, 4], definitions.definitions().characterO)
    assert not winner
    winner, who = board.setCharacter([5, 4], definitions.definitions().characterO)

    plot.plotBoard(board.getBoard())
    assert winner
    assert board.compareCharacter(who, definitions.definitions().characterO)
    print("Pass 11")

    board.resetBoard()

    # FIX
    board.setCharacter([4, 4], definitions.definitions().characterO)
    board.setCharacter([5, 5], definitions.definitions().characterO)
    board.setCharacter([6, 6], definitions.definitions().characterO)
    winner, who = board.setCharacter([7, 7], definitions.definitions().characterO)
    assert not winner
    winner, who = board.setCharacter([8, 8], definitions.definitions().characterO)

    plot.plotBoard(board.getBoard())
    assert winner
    assert board.compareCharacter(who, definitions.definitions().characterO)
    print("Pass 12")

    board.resetBoard()

    # FIX
    board.setCharacter([8, 8], definitions.definitions().characterO)
    board.setCharacter([7, 9], definitions.definitions().characterO)
    board.setCharacter([6, 10], definitions.definitions().characterO)
    winner, who = board.setCharacter([5, 11], definitions.definitions().characterO)
    assert not winner
    winner, who = board.setCharacter([4, 12], definitions.definitions().characterO)

    plot.plotBoard(board.getBoard())

    assert winner
    assert board.compareCharacter(who, definitions.definitions().characterO)
    print("Pass 13")

    board.setCharacter([3, 5], definitions.definitions().characterX)
    board.setCharacter([3, 6], definitions.definitions().characterX)
    board.setCharacter([3, 7], definitions.definitions().characterX)
    board.setCharacter([3, 8], definitions.definitions().characterX)
    plot.plotBoard(board.getBoard())

    cleaned = board.cleanupBoard(board.getBoard())

    plot.plotBoard(cleaned)

    print("Pass 14")




# ################################################################
# Will test this class
# ################################################################
#testMyself()