import genes as gs
import numpy as np
import os
import shutil

statSlidingWinLen = 100
maxHistoryResolution = 600

graphStorePath="graphCheckpoints"

statsFileName = "statsFile.json"

#####################################################
# Base class for a luff player. To be inherited by
# a proper player implementation class.
# Inherits from the top base class: genes
#####################################################
class luffPlayer(gs.genes):

    #####################################################
    # Constructor
    # benchmarkPlayer, e.g. validator, this means the opponent may not learn from this player
    # prohibit Learn means this player will not learn, but others may learn from it
    #####################################################
    def __init__(self,
                 character,
                 name="noname",
                 genes=None,
                 isHuman=False,
                 benchmarkPlayer=False,
                 prohibitLearn=False):

        self.FCGraphFolder = graphStorePath + name + '_FC/'
        self.FCGraphNameFile = self.FCGraphFolder + "_FC"
        self.fullPathFCGraphFolder = os.getcwd() + '/' + self.FCGraphFolder
        self.benchmarkPlayer = benchmarkPlayer
        self.bestScore = 0
        self.lastScore = 0
        self.character = character
        self.name = name
        self.varianceHistory = []
        self.varianceLastGame = []
        self.winRatioHistory = []
        self.winRatioSlidingWin = []
        self.gameLengthHistory = []
        self.gameLengthSlidingWin = []

        self.allData = {}
        self.allData['totTrained'] = 0
        self.allData['matchesPlayed'] = 0
        self.allData['age'] = 0
        self.allData['prohibitLearn'] = prohibitLearn

        result, data = self.restoreDataFromDisk(self.fullPathFCGraphFolder, statsFileName)

        if result:
            self.allData = data

        gs.genes.__init__(self, name=name, genes=genes, isHuman=isHuman)
        print("Player created... {}".format(name))


    #####################################################
    # Functions to be implemented in your inheriting classes!
    #####################################################
    def initDictionary(self):
        return {'name': {'data': "TBD", 'type': "String", 'min': 'NA', 'max': 'NA', 'const': True,'initialized': False}}

    def learnHistory2(self, board, trainBoard=None, goodMove=True, QValue=15.0):
        pass

    def learnHistory(self, boardHistory, winningPlayerChar):
        pass

    def saveGraphtoDisk(self):
        pass

    def getNWSize(self):
        return 0

    def getHiddenLayerCount(self):
        return 0

    def getLearnRate(self):
        return 0.0

    #####################################################
    # Function
    #####################################################
    def clearAllDataFromDisk(self):

        print("Cleaning data on disk: {}".format(self.fullPathFCGraphFolder))
        try:
            shutil.rmtree(self.fullPathFCGraphFolder)
        except:
            pass

        print("Done cleaning")

    #####################################################
    # Function
    #####################################################
    def savePlayerStatsToDisk(self):
        self.dumpDataToDisk(self.allData, self.fullPathFCGraphFolder, statsFileName)

    #####################################################
    # Function
    #####################################################
    def getTotTrained(self):
        return self.allData['totTrained']

    #####################################################
    # Function
    #####################################################
    def increaseTotTrained(self):
        self.allData['totTrained'] += 1

    #####################################################
    # Function
    #####################################################
    def isBenchmark(self):
        return self.benchmarkPlayer

    #####################################################
    # Function
    #####################################################
    def storeVictorySliding(self, value):
        self.winRatioSlidingWin.append(value)
        self.trimAllSlidingWindows()

    #####################################################
    # Function
    #####################################################
    def storeGameLengthSliding(self, value):
        self.gameLengthSlidingWin.append(value)
        self.trimAllSlidingWindows()

    #####################################################
    # Function
    #####################################################
    def trimAllSlidingWindows(self):
        global statSlidingWinLen

        if len(self.winRatioSlidingWin) > statSlidingWinLen:
            self.winRatioSlidingWin.pop(0)
        if len(self.gameLengthSlidingWin) > statSlidingWinLen:
            self.gameLengthSlidingWin.pop(0)

    #####################################################
    # Function
    #####################################################
    def getGenes(self):
        return self.data

    #####################################################
    # Function
    #####################################################
    def getName(self):
        return self.name

    #####################################################
    # Function
    #####################################################
    def getPlayerChar(self):
        return self.character

    #####################################################
    # Function
    #####################################################
    def setPlayerChar(self, newCharacter):
        self.character = newCharacter

    #####################################################
    # Function
    # Todo implement modify/mutate in this call
    #####################################################
    def clone(self, name="clone", mutate=False, modifySlightly=False):
        player = luffPlayer(name=name, genes=self.genesClone())

        if mutate:
            player.genesMutate()
        if modifySlightly:
            player.modifySlightly()

        return player

    #####################################################
    # Function
    #####################################################
    def mateWithOther(self, other, name="Bengt"):
        return luffPlayer(name=name+"sson", genes=self.genesMateWithOther(other))

    #####################################################
    # Function
    #####################################################
    def returnAllData(self):
        return self.data, self.lastScore, self.bestScore, self.age

    def getMatchesPlayed(self):
        return self.allData['matchesPlayed']

    #####################################################
    # Function
    #####################################################
    def setNewScore(self, score):
        if score > self.bestScore:
            self.bestScore = score
        self.lastScore = score

    #####################################################
    # A game engine can here report a complete game
    #####################################################
    def gameFinished(self, won):

        self.allData['matchesPlayed'] += 1
        self.storeVictorySliding(won)
        self.winRatioHistory.append(self.getWinRate())
        self.winRatioHistory = self.shortenHistory(self.winRatioHistory)
        self.varianceHistory.append(np.average(self.varianceLastGame))
        self.lowPassFilter(self.varianceHistory, windowLen=5)
        self.varianceLastGame = []
        self.increaseAge()

    #####################################################
    # Get array with win rate over time
    #####################################################
    def getWinRateOverTime(self):
        return self.winRatioHistory

    #####################################################
    # Get last win rate over time value
    #####################################################
    def getWinRate(self):
        wins = 0

        if len(self.winRatioSlidingWin) < (statSlidingWinLen / 2):
            return 0.001

        for res in self.winRatioSlidingWin:
            if res:
                wins += 1

        loss = len(self.winRatioSlidingWin) - wins

        if loss <= 0:
            return wins

        return wins / loss

    #####################################################
    # get last game length average value
    #####################################################
    def getGameLength(self):
        length = 0

        if len(self.gameLengthSlidingWin) < (statSlidingWinLen / 10):
            return 20

        for l in self.gameLengthSlidingWin:
            length += l

        return length / len(self.gameLengthSlidingWin)

    #####################################################
    # ToDo: Implement variance average or similar..
    #####################################################
    def storeVariance(self, variance):
        self.varianceLastGame.append(variance)
        self.varianceLastGame = self.shortenHistory(self.varianceLastGame)

    #####################################################
    # store the game length for statistical purpose
    #####################################################
    def storeGameLength(self, length):
        self.storeGameLengthSliding(length)
        self.gameLengthHistory.append(self.getGameLength())

        self.gameLengthHistory = self.shortenHistory(self.gameLengthHistory)

    #####################################################
    # Function
    #####################################################
    def getGameLengthOverTime(self):
        return self.gameLengthHistory

    #####################################################
    # Function that keeps the recorded history to
    # less than maxHistoryResolution entries.
    # The history may be longer, but the resolution will be lower
    #####################################################
    def shortenHistory(self, data):

        global maxHistoryResolution
        lastElement = None

        if len(data) < maxHistoryResolution:
            return data

        shorterData = []
        counter = 0

        for element in data:
            if counter % 2 == 0:
                if lastElement is not None:
                    value = (lastElement + element) / 2
                else:
                    value = element

                shorterData.append(value)

            counter += 1
            lastElement = element

        return shorterData

    #####################################################
    # Function
    #####################################################
    def getVarianceOverTime(self):
        return self.varianceHistory

    #####################################################
    # Function
    #####################################################
    def increaseAge(self):
        self.allData['age'] += 1

    #####################################################
    # Function
    #####################################################
    def getPlayerType(self):
        return "dummy"

    #####################################################
    # Function
    #####################################################
    def setProhibitLearn(self, value):
        self.allData['prohibitLearn'] = value

    #####################################################
    # Function
    #####################################################
    def getProhibitLearn(self):
        return self.allData['prohibitLearn']

    #####################################################
    # Function
    #####################################################
    def lowPassFilter(self, input, windowLen=5):
        windowLength = windowLen
        sum = 0
        count = 0

        lenr = len(input)
        startIndex = lenr - windowLength

        if(startIndex < 0):
            startIndex = 0

        for value in input[startIndex:]:
            sum += value
            count += 1

        if count < 1:
            count = 0

        average = sum / count

        input[len(input) - 1] = average

    #####################################################
    # Function
    #####################################################
    def print(self):
        print("-------------------------")
        print("lastScore: {a:.2f}, bestScore: {b:.2f}, age: {c}".format(a=self.lastScore, b=self.bestScore, c=self.allData['age']))
        self.printGenes()

    #####################################################
    # Function
    #####################################################
    def test(self):
        self.print()
        self.genesMutate()
        self.increaseAge()
        self.returnAllData()
        self.setNewScore(12)
        clone = self.clone("Dolly", True, True)
        child = self.mateWithOther(clone, "Bengt")

#luffPlayer(name="Bengt").test()