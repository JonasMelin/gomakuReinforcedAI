import luffGameEngine
import luffAIPlayer3
import luffRandomPlayer
import luffHumanPlayer as humanPlayer
import luffQValuePlayer as qPlayer
import definitions as defs
import luffVisualizer
import luffGameBoard
import threading
import multiprocessing
import time
import random
import os

metadataFileName = "tournamentMetaData.json"

printGraphEvery = 25

currentTrainStopThresh = 0.01
threshNotReachCount = 0
threshNotReachThresh = 300

# Before this amount of games it is only possible to set a character touching another character.
# This is a way to optimize the time it takes to learn the basics of the game.
switchToFullGameBoardAfterGames = 500000


# ################################################################
# Class that orchestrates tournaments of different playsers,
# AI players, teaching playes, random players and human players.
# The purpose of teaching the AI players to be as good as possible.
# ################################################################
class luffTournamentManager(threading.Thread):

    # ################################################################
    # Constructor
    # ################################################################
    def __init__(self, human=False):
        self.gameEngine = luffGameEngine.luffGameEngine()
        self.defs = defs.definitions()
        self.viss = luffVisualizer.luffVisualizer()
        self.boardOperations = luffGameBoard.luffGameBoard()
        self.criticalSection = threading.Lock()
        self.ongoingGames = 0
        self.CPUs = 1

        self.players = {}
        self.fullPathToMetaData = os.getcwd() + '/'

        if human:
            # This means there will be a human player, hence, we don't need
            # to create all these AI players that is used to train AI..
            return

        result, data = self.defs.restoreDataFromDisk(self.fullPathToMetaData, metadataFileName)

        if result:
            self.players = data
            self.restorePlayerObjects()

    # ################################################################
    # Creates the player objects from names stored to disk
    # ################################################################
    def restorePlayerObjects(self):

        for nextPlayerName, p in self.players.items():

            try:
                p.getTotTrained()
                # Player object already exists...
            except:
                # No matching object. create it..
                self.players[nextPlayerName] = luffAIPlayer3.luffAIPlayer3(self.defs.characterX, nextPlayerName)

    # ################################################################
    # Just store the names of all players, remove the object
    # as they are not serializable. They will be re-created
    # when program re-starts.
    # ################################################################
    def storeMetaDataToDisk(self):
        copyOfPlayers = {}

        for playerName, p in self.players.items():

            if p.getPlayerType() == "AI":
                # Only storeAI players to disk..  And remove the actual player instance
                copyOfPlayers[playerName] = ""

        self.defs.dumpDataToDisk(copyOfPlayers, self.fullPathToMetaData, metadataFileName)

    # ################################################################
    # Adds the benchmark players, those players that are used for
    # benchmarking and not for teaching other players. e.g. validators
    # ################################################################
    def addBenchmarkPlayers(self):
        nextPlayer = qPlayer.luffQValuePlayer(self.defs.characterX, "QPlayer", benchmarkPlayer=True)
        self.players[nextPlayer.getName()] = nextPlayer

    # ################################################################
    # Adds a player that will participate in the tournament
    # ################################################################
    def addPlayer(self, player):
        self.players[player.getName()] = player

    # ################################################################
    # Adds a player that will participate in the tournament
    # ################################################################
    def removePlayer(self, player):

        keyToRemove = ""

        for playerName in self.players:
            if playerName == player.getName():
                keyToRemove = playerName

        self.players[keyToRemove].clearAllDataFromDisk()
        self.players.pop(keyToRemove)

    # ################################################################
    # run tournament
    # ################################################################
    def runTournament(self, loops=5000000, abortAtWinRate=False, statsFromAllMatches=True, verbose=True):

        global printGraphEvery
        totGames = 0

        for totTournament in range(loops):
            winner = self.getMostSuccessfulPlayer()
            print("Starting new tournament. Tot tournaments: {a}. Tot games: {b}. Best {c}. Winrate {d}"
                  .format(a=totTournament,
                          b=totGames,
                          c=winner.getName(),
                          d=winner.getWinRate()))
            for homePlayer, hp in self.players.items():

                for awayPlayer, ap in self.players.items():

                    if homePlayer == awayPlayer:
                        continue # We don't play against ourselves.

                    if hp.isBenchmark() and ap.isBenchmark():
                        continue # Benchmark players dont meet each other

                    if (hp.getPlayerType() == "AI" or ap.getPlayerType() == "AI"):
                        # We only launch a game if there it at least one AI player playing
                        hp.setPlayerChar(self.defs.characterX)
                        ap.setPlayerChar(self.defs.characterO)

                        if totGames > switchToFullGameBoardAfterGames:
                            useAllAvailPos = True
                        else:
                            useAllAvailPos = False

                        self.gameEngine.runNewGame(
                            hp,
                            ap,
                            useAllAvailPos=useAllAvailPos,
                            randomRate=0,
                            startRandom=0,
                            statsFromAllMatches = statsFromAllMatches,
                            verbose=verbose)

                        totGames += 1

            self.handleTournamentFinished(totTournament)

            if totTournament % printGraphEvery == 0:
                self.storeMetaDataToDisk()
                self.saveAllGraphsToDisk()
                self.visualize(self.players)

        return False

    # ################################################################
    # ...
    # ################################################################
    def reElectLeader(self):

        global currentTrainStopThresh

        for playerName, p in self.players.items():
            p.setProhibitLearn(False)

        best = self.getMostSuccessfulPlayer()
        best.setProhibitLearn(True)
        currentTrainStopThresh = best.getWinRate() + 0.001


    # ################################################################
    # ...
    # ################################################################
    def handleTournamentFinished(self, totTournament):

        global currentTrainStopThresh
        global threshNotReachCount
        global threshNotReachThresh

        if totTournament > 15:
            # Start this check when the statistics have stabalized,
            # To avoid throing out good players in the beginning of a
            self.removeWorstPlayerIfnotYoungest()

        best = self.getMostSuccessfulPlayer()

        if best.getWinRate() > currentTrainStopThresh:
            threshNotReachCount = 0

            print("New record by: " + best.getName() + "new Thresh: {}".format(best.getWinRate()))
            self.reElectLeader()
        else:
            threshNotReachCount += 1

            if threshNotReachCount > threshNotReachThresh:
                print("No one reached currentTrainStopThresh: " + str(currentTrainStopThresh) + " after " + str(threshNotReachThresh) + "Attempts.")
                threshNotReachCount = 0
                self.killOldLoosers()

    # ################################################################
    # TBD
    # ################################################################
    def removeWorstPlayerIfnotYoungest(self):
        worst = self.getWorstPlayer()
        youngest = self.getYoungestPlayer()

        if worst.getName() != youngest.getName():
            if (worst.getWinRate() + 0.01) < youngest.getWinRate():
                reElect = False
                # So, the worst player is also older than the youngest player..
                # Simply through out this player and inject a new one
                print("Throwing out {a} that was worse than a younger player! winrate worst: {b} winrate younger: {c}".format(a=worst.getName(), b=worst.getWinRate(), c=youngest.getWinRate()))
                if worst.getProhibitLearn():
                    # The worst player was the leader. Need to select a new leader.
                    reElect = True
                self.removePlayer(worst)
                self.addPlayer(luffAIPlayer3.luffAIPlayer3(self.defs.characterX, "W" + str(random.randint(0, 10000))))

                if reElect:
                    self.reElectLeader()

    # ################################################################
    # TBD
    # ################################################################
    def killOldLoosers(self):

        maxAgeWinQuota = -5000
        worstPlayer = None

        # if under this level, you might get killed
        thresh = self.getMostSuccessfulPlayer().getWinRate() * 0.4

        if thresh < 0.05:
            return    # not even best player can really play.  dont run algorithm


        for playerName, p in self.players.items():

            #p.setProhibitLearn(False)
            pass

            if p.getTotTrained() < 500:
                continue # dont kill to young players

            if p.getWinRate() < 0.02:  # Such bad player, with this age. simply kill it!
                print("Killing a really bad player {a}. trained {b}, winrate {c}".format(a=p.getName(), b=p.getTotTrained(), c=p.getWinRate()))
                self.removePlayer(worstPlayer)
                self.addPlayer(luffAIPlayer3.luffAIPlayer3(self.defs.characterX, "B" + str(random.randint(0, 10000))))
                self.reElectLeader()
                return

            if p.getWinRate() > thresh: # This player is above the thresh. This is OK!
                continue

            ageWinQuota = p.getTotTrained() / p.getWinRate()

            if ageWinQuota > maxAgeWinQuota:
                maxAgeWinQuota = ageWinQuota
                worstPlayer = p


        if worstPlayer is not None:
            print("Throwing out old, bad player {a}. trained {b}, winrate {c}".format(a=worstPlayer.getName(), b=worstPlayer.getTotTrained(), c=worstPlayer.getWinRate()))
            self.removePlayer(worstPlayer)
            self.addPlayer(luffAIPlayer3.luffAIPlayer3(self.defs.characterX, "G" + str(random.randint(0, 10000))))
            self.reElectLeader()



    # ################################################################
    # TBD
    # ################################################################
    def trainPlayer(self):

        if len(self.players) == 0:
            self.addPlayer(luffAIPlayer3.luffAIPlayer3(self.defs.characterX, "i1"))  # PUT
            self.addPlayer(luffAIPlayer3.luffAIPlayer3(self.defs.characterX, "i2"))  # PUT
            self.addPlayer(luffAIPlayer3.luffAIPlayer3(self.defs.characterX, "i3"))  # PUT
            self.addPlayer(luffAIPlayer3.luffAIPlayer3(self.defs.characterX, "i4"))  # PUT

        self.addBenchmarkPlayers()
        self.runTournament(statsFromAllMatches=False, verbose=False)

    # ################################################################
    # Save all trained AI networks to disk...
    # ################################################################
    def saveAllGraphsToDisk(self):

        for playerName, p in self.players.items():
            p.saveGraphtoDisk()

    # ################################################################
    # Save all trained AI networks to disk...
    # ################################################################
    def getMostSuccessfulPlayer(self):

        highScore = -100
        bestPlayer = None

        for playerName, p in self.players.items():

            if p.getPlayerType() != "AI":
                continue #Only get stats for AI players...

            if p.isBenchmark():
                continue # Dont count benchmark players

            if p.getWinRate() > highScore:
                highScore = p.getWinRate()
                bestPlayer = p

        return bestPlayer

    # ################################################################
    # Save all trained AI networks to disk...
    # ################################################################
    def getWorstPlayer(self):

        lowScore = 50000
        worstPlayer = None


        for playerName, p in self.players.items():

            if p.getPlayerType() != "AI":
                continue #Only get stats for AI players...

            if p.isBenchmark():
                continue # Dont count benchmark players

            if p.getWinRate() <= (lowScore + 0.0001):  # if equal bad score on several, always return the last one..
                lowScore = p.getWinRate()
                worstPlayer = p

        return worstPlayer

    # ################################################################
    # Save all trained AI networks to disk...
    # ################################################################
    def getYoungestPlayer(self):

        lowScore = 50000000
        youngestPlayer = None


        for playerName, p in self.players.items():

            if p.getPlayerType() != "AI":
                continue #Only get stats for AI players...

            if p.isBenchmark():
                continue # Dont count benchmark players

            if p.getTotTrained() <= (lowScore + 1):  # if equal number, always return the last one..
                lowScore = p.getTotTrained()
                youngestPlayer = p

        return youngestPlayer


    # ################################################################
    # visualize progress
    # ################################################################
    def visualize(self, players):

        self.viss.plotReset(dimx=len(players), dimy=2)

        for playerName, p in players.items():

            genes = p.getGenesAsDict()
            benchmark = ''

            if p.isBenchmark() :
                benchmark = '(benchmark)'

            self.viss.plotAddForMultiple(p.getWinRateOverTime(),
                                         name=p.getName() + " Winrate {a:.02f} train# {b} NS {c} HL {d} LR {e:.0000006f} ".format(
                                             a=p.getWinRate(),
                                             b=p.getTotTrained(),
                                             c=p.getNWSize(),
                                             d=p.getHiddenLayerCount(),
                                             e=p.getLearnRate()) + benchmark)
            self.viss.plotAddForMultiple(p.getGameLengthOverTime(),
                                         name=p.getName() + " tot played {a}, prohibit learn {b}".format(
                                             a=p.getMatchesPlayed(),
                                             b=p.getProhibitLearn()) )

        self.viss.render(sleep=0.2)


    # ################################################################
    # Launch a game between AIPlayer and a human
    # ################################################################
    def humanGame(self, AIPlayer):
        human = humanPlayer.luffHumanPlayer(defs.definitions().characterO, "playerHumanO")
        AIPlayer = luffAIPlayer3.luffAIPlayer3(self.defs.characterX, AIPlayer)

        while True:
            self.gameEngine.runNewGame(human, AIPlayer, useAllAvailPos=False, verbose=True)


# ################################################################
# Main function...
# Trains a AI player, launches a game with the AI winner towards a human
# ################################################################

TM = luffTournamentManager()
TM.trainPlayer()

luffTournamentManager(human=True).humanGame('R883')









