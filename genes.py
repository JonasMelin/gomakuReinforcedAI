import random
import os
import json
import definitions

#####################################################
# Base class for all types of players.
# This is designed for evolutionary programming
# having all nice features for managing parameters,
# mutate them, mate them, store/restore to disk etc.
#####################################################
class genes(object):

    #####################################################
    # Function
    #####################################################
    def __init__(self, name="noname", genes=None, isHuman=False):

        self.isHuman = isHuman

        if genes is None:
            print("Creating new genes {}".format(name))
            self.data = {}
            self.initRandom(name)
        else:
            print("Using provided genes {}".format(name))
            self.data = genes
            self.data['name']['data'] = name
            self.data['name']['initialized'] = True

    #####################################################
    # Function
    #####################################################
    def getIsHuman(self):
        return self.isHuman

    #####################################################
    # Function
    #####################################################
    def initDictionary(self):

        assert False # You should implement this function in a child class

        """
        #Example implementation in child class
        return {'learnRate': {'data': 0.0, 'type': "float", 'min': 0.0000001, 'max': 0.001, 'const': False,
                                     'initialized': False},
                       'hiddenLayers': {'data': 0, 'type': "int", 'min': 0, 'max': 5, 'const': False,
                                        'initialized': False},
                       'epocs': {'data': 0, 'type': "int", 'min': 1, 'max': 6, 'const': False, 'initialized': False},
                       'NWSize': {'data': 0, 'type': "int", 'min': 2, 'max': 128, 'const': False, 'initialized': False},
                       'InvOutput': {'data': 0, 'type': "bool", 'min': 'NA', 'max': 'NA', 'const': False,
                                     'initialized': False},
                       'name': {'data': "TBD", 'type': "String", 'min': 'NA', 'max': 'NA', 'const': True,
                                'initialized': False}}
                                
                                
        This it a minimum example: 
        return {'name': {'data': "TBD", 'type': "String", 'min': 'NA', 'max': 'NA', 'const': True,'initialized': False}}
        """

    #####################################################
    # Function
    #####################################################
    def dumpDataToDisk(self, data, folder, name):

        definitions.definitions().dumpDataToDisk(data, folder, name)

    #####################################################
    # Function
    #####################################################
    def restoreDataFromDisk(self, folder, name):

        return definitions.definitions().restoreDataFromDisk(folder, name)

    #####################################################
    # Function
    #####################################################
    def initRandom(self, theName):

        self.data = self.initDictionary()

        self.data['name']['data'] = theName
        self.data['name']['initialized'] = True

        for key, values in self.data.items():

            if values['type'] == 'String':
                val=values['data']
            elif values['type'] == 'float':
                val=self.randomInitFloat(values)
            elif values['type'] == 'int':
                val=self.randomInitInt(values)
            elif values['type'] == 'bool':
                val=self.randomInitBool(values)
            else:
                print("ERROR. Unsupported type in genes.. ")
                exit(1)


    #####################################################
    # Function
    #####################################################
    def randomInitFloat(self, values):
        assert values['type'] == 'float'
        assert values['const'] is False

        values['data'] = random.uniform(values['min'], values['max'])
        values['initialized'] = True

        return values['data']

    #####################################################
    # Function
    #####################################################
    def randomInitInt(self, values):
        assert values['type'] == 'int'
        assert values['const'] is False

        values['data'] = int(random.uniform(values['min'], values['max']))
        values['initialized'] = True

        return values['data']

    #####################################################
    # Function
    #     # Manipulates randomly up / down with randomly
    #     # 1-10% of the allowed interval.  Will never go
    #     # above or under allowed interval.
    #####################################################
    def randomManipulateInt(self, values):
        assert values['type'] == 'int'
        assert values['const'] is False

        max = values['max']
        min = values['min']

        adjustLevel = int((max - min) / (int(random.uniform(1, 10))))

        if (adjustLevel < 1):
            adjustLevel = 1

        if self.randomZeroOne() == 1:
            values['data'] = values['data'] + adjustLevel
        else:
            values['data'] = values['data'] - adjustLevel

        if values['data'] > values['max']:
            values['data'] = values['max']
        if values['data'] < values['min']:
            values['data'] = values['min']

    #####################################################
    # Function
    # Manipulates randomly up / down with randomly
    # 1-10% of the allowed interval.  Will never go
    # above or under allowed interval.
    #####################################################
    def randomManipulateFloat(self, values):
        assert values['type'] == 'float'
        assert values['const'] is False

        max = values['max']
        min = values['min']

        adjustLevel = (max - min) / (int(random.uniform(1, 10)))

        if self.randomZeroOne() == 1:
            values['data'] = values['data'] + adjustLevel
        else:
            values['data'] = values['data'] - adjustLevel

        if values['data'] > values['max']:
            values['data'] = values['max']
        if values['data'] < values['min']:
            values['data'] = values['min']

    #####################################################
    # Function
    #####################################################
    def randomInitBool(self, values):
        assert values['type'] == 'bool'
        assert values['const'] is False

        values['data'] = bool(random.getrandbits(1))
        values['initialized'] = True

        return values['data']

    #####################################################
    # random value 1/0
    #####################################################
    def randomZeroOne(self):

        if bool(random.getrandbits(1)):
            return 0
        else:
            return 1

    #####################################################
    # Get all genes as a dict (of dicts..)
    #####################################################
    def getGenesAsDict(self):
        return self.data

    #####################################################
    # Print myself
    #####################################################
    def printGenes(self):

        print(" ------ Genes -- {} ------------------------ ".format(self.data['name']['data']))

        for key, values in self.data.items():

            print("{a}:{b}".format(a=key, b=values['data']))

        print("")

    #####################################################
    # modify slightly
    #####################################################
    def modifySlightly(self, numberOfModifications=1):

        assert (numberOfModifications >= 1)

        for i in range(numberOfModifications):

            value_to_manipulate = int(random.uniform(0, len(self.data)))
            counter = 0

            for key, value in self.data.items():
                if (counter is value_to_manipulate) and (value['const'] is False):
                    if value['type'] is 'int':
                        self.randomManipulateInt(value)
                    elif value['type'] is 'float':
                        self.randomManipulateFloat(value)
                    elif value['type'] is 'bool':
                        self.randomInitBool(value)
                    else:
                        #assert 0
                        pass

                    # Abort. Note that if a value is located after a const
                    # value they will be mutated slightly more often than other
                    # values..
                    break;

                counter += 1

    #####################################################
    # mutate a random number in the genes.
    # Mutation means the value is re-initialized according
    # to its ranges.
    #####################################################
    def genesMutate(self, numberOfMutations=1):

        assert (numberOfMutations >= 1)

        for i in range(numberOfMutations):


            value_to_manipulate = int(random.uniform(0, len(self.data)))
            counter = 0

            for key, value in self.data.items():
                if (counter is value_to_manipulate) and (value['const'] is False):
                    if value['type'] is 'int':
                        self.randomInitInt(value)
                    elif value['type'] is 'float':
                        self.randomInitFloat(value)
                    elif value['type'] is 'bool':
                        self.randomInitBool(value)
                    else:
                        #assert 0
                        pass

                    # Abort. Note that if a value is located after a const
                    # value they will be mutated slightly more often than other
                    # values..
                    break;

                counter += 1



    #####################################################
    # clone
    #####################################################
    def genesClone(self, name="noname"):

        newDict = self.data.copy()

        for key, values in self.data.items():

            newDict[key] = self.data[key].copy()


        return newDict


    #####################################################
    # Returns the genes of a new born chield that is the
    # product of the two parents.
    # Takes a genes object. not a dict..
    #####################################################
    def genesMateWithOther(self, other, nameOfChild = "noname"):

        #assert False # Verify that this still works..

        childDict = other.getGenesAsDict().copy()

        for key, values in self.data.items():

            if self.randomZeroOne() == 1:
                childDict[key] = other.getGenesAsDict()[key].copy()
                childDict[key]['data'] = other.getGenesAsDict()[key]['data']
            else:
                childDict[key] = self.data[key].copy()
                childDict[key]['data'] = self.data[key]['data']

        return childDict
