import time
import random
import json


# ################################################
# Holds some global config values, such as game board size.
# Also a timer function that ended up here....?
# ################################################
class definitions(object):

    boardSize = 17  # Use an odd number, like 25..
    characterNone = 0.0  # in the game board, if no one set a character.
    characterX = 1.0 # Character X
    characterO = -1.0  # Character Y
    characterInteresting = 2 #Used in the interesting positions matrix.
    characterInterestingThresh = 1.9 # Cannot quickly compare floats, but bigger than this value means characterInteresting
    patternRecOutputs = 400 # Number of outputs from the pattern recognition layer. This should
                            # really not be a definition here, but read from the actual value. ToDo: fix:

    def timeDiffStart(self):
        self.startTime = time.time()

    def timeDiffEnd(self):
        return time.time() - self.startTime

    # ################################################
    # rate = 1 yeald 1/2 times true
    # rate = 10 yealds 1/10 times true
    # ################################################
    def randomTrueFalse(self, rate):
        if random.randint(0, rate) == rate:
            return True
        else:
            return False

    #####################################################
    # Function
    #####################################################
    def dumpDataToDisk(self, data, folder, name):

        filename = folder + name

        try:
            os.mkdir(folder)
        except:
            pass
        try:
            os.remove(filename)
        except:
            pass

        with open(filename, 'w') as fp:
            json.dump(data, fp)

        #print("Dumped metadata to disk {}".format(filename))

    #####################################################
    # Function
    #####################################################
    def restoreDataFromDisk(self, folder, name):

        filename = folder + name
        try:
            json_data = open(filename).read()
            data = json.loads(json_data)
            print("Restored {}".format(filename))
            return True, data
        except:
            print("Failed to restore {}".format(filename))
            return False, None

