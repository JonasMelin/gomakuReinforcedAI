import luffPlayer
import definitions
import luffGameBoard
import tensorflow as tf
import math
import numpy as np
import os

genesFileName = "geneseFCMetadata.json"

# ################################################
# Tensorflow bsaed AI player that upon a given game board
# will return the best position for next move. Possible to
# train this player upon loosing a game..
# ################################################
class luffAIPlayer3(luffPlayer.luffPlayer):

    # ################################################
    # Constructor
    # ################################################
    def __init__(self,
                 character,
                 name="noname",
                 genes=None,
                 benchmarkPlayer=False,
                 prohibitLearn=False):
        luffPlayer.luffPlayer.__init__(self,
                                       character=character,
                                       name=name,
                                       genes=genes,
                                       isHuman=False,
                                       benchmarkPlayer=benchmarkPlayer,
                                       prohibitLearn=prohibitLearn)


        self.defs = definitions.definitions()
        self.gameBoardOperations = luffGameBoard.luffGameBoard()
        result, data = self.restoreDataFromDisk(self.fullPathFCGraphFolder, genesFileName)

        if result:
            self.data = data

        self.initVariables()
        self.printGenes()

        self.defineFCModel(self.defs.boardSize, 2)

        print("AI player created {}".format(name))

    #####################################################
    # @override from genes
    #####################################################
    def initDictionary(self):
        return {
            'learnRate': {'data': 0.0, 'type': "float", 'min': 0.0001, 'max': 0.000001, 'const': False, 'initialized': False},
            'hiddenLayers': {'data': 0, 'type': "int", 'min': 1, 'max': 3, 'const': False, 'initialized': False},
            'NWSize': {'data': 0, 'type': "int", 'min': 1000, 'max': 8000, 'const': False, 'initialized': False},
            'historyDepthDiv': {'data': 0, 'type': "int", 'min': 2, 'max': 2, 'const': False, 'initialized': False},
            'NWOutputValue': {'data': 0, 'type': "int", 'min': 1, 'max': 10, 'const': False, 'initialized': False},
            'name': {'data': "TBD", 'type': "String", 'min': 'NA', 'max': 'NA', 'const': True, 'initialized': False}
        }

    #####################################################
    # store the genes variables in my self for easy access
    #####################################################
    def initVariables(self):
        self.learning_rate = self.data['learnRate']['data']
        self.NWSize = self.data['NWSize']['data']
        self.hiddenLayers = self.data['hiddenLayers']['data']
        self.historyDepthDiv = self.data['historyDepthDiv']['data']
        self.NWOutputValue = self.data['NWOutputValue']['data']



    #####################################################
    # Define the fully connected neural network layers.
    # Just raw, pure nerual network. No convolution etc.
    #####################################################
    def defineFCModel(self, boardSize, num_outputs):

        self.graphFC = tf.Graph()
        self.sessionFC = tf.Session(graph=self.graphFC)

        with self.graphFC.as_default() as g:

            print("Creating Fully connected AI 3.0 model")

            self.xFC = tf.placeholder(tf.float32, shape=[None, boardSize * boardSize], name='xFC')
            self.y_modelFC = self.new_fc_layer(input=self.xFC,
                                                      num_inputs=boardSize * boardSize,
                                                      num_outputs=self.NWSize,
                                                      use_relu=True)

            for a in range(self.hiddenLayers):
                self.y_modelFC = self.new_fc_layer(input=self.y_modelFC,
                                                   num_inputs=self.NWSize,
                                                   num_outputs=self.NWSize,
                                                   use_relu=True)

            self.y_modelFC = self.new_fc_layer(input=self.y_modelFC,
                                               num_inputs=self.NWSize,
                                               num_outputs=num_outputs,
                                               use_relu=True)

            # y_true is where you put the training value.. e.g. [1, 0]

            self.y_true_FC = tf.placeholder(tf.float32, shape=[None, num_outputs], name='y_trueFC')
            cross_entropy = tf.nn.softmax_cross_entropy_with_logits_v2(logits=self.y_modelFC, labels=self.y_true_FC)
            cost = tf.reduce_mean(cross_entropy)
            self.optimizerFC = tf.train.AdamOptimizer(learning_rate=self.learning_rate).minimize(cost)

            try:
                tf.train.Saver().restore(self.sessionFC, self.FCGraphNameFile)
                print("Successfully restored FC variables from disk! {}".format(self.FCGraphNameFile))
            except:
                print("Failed to restore FC variables. Training a new one.. {}".format(self.FCGraphNameFile))
                self.sessionFC.run(tf.global_variables_initializer())

    #####################################################
    # Save FC graph to disk
    #####################################################
    def saveGraphtoDisk(self):

        if self.benchmarkPlayer or self.allData['prohibitLearn']:
            return

        with self.graphFC.as_default() as g:
            saver = tf.train.Saver()
            save_path = saver.save(self.sessionFC, self.FCGraphNameFile)
            #print("Saved FC graph weights here: {}".format(save_path))

        self.dumpDataToDisk(self.data, self.fullPathFCGraphFolder, genesFileName)
        self.savePlayerStatsToDisk()

    #####################################################
    # Calculates the output from the FC network
    #####################################################
    def getFCOutput(self, dataX):
        assert self.sessionFC is not None and self.graphFC is not None

        feed_dict = {self.xFC: dataX}

        with self.graphFC.as_default() as g:
            return self.sessionFC.run(self.y_modelFC, feed_dict=feed_dict)

    #####################################################
    # Returns a position given an input board
    #####################################################
    def calcOutputGetPos(self, board, availablePos, humanInvolved=False):

        scoreListOffensive = []
        X_data = []
        highestScore = -5000
        highestScorePos = None

        cleanBoard = board.cleanupBoard(board.getBoard())

        if board.compareCharacter(self.getPlayerChar(), self.defs.characterO):
            # This is a trick. All players will always see the game board
            # as if they were playing with the X character. So it will be simpler to train.
            cleanBoard = board.invertBoard(cleanBoard)

        for pos in availablePos:
            offsetBoard = board.offsetBoard(pos, cleanBoard)

            # Test To set an X here in this position. What will the network think about that
            # Remember always to set an X as we are always seing the board as an X
            # The board is offcentered to the interesting position, so we always set the
            # X in the center.
            center = board.getCenterCoord()

            offsetBoard[center[0], center[1]] = self.defs.characterX

            flatBoard = offsetBoard.flatten(len(offsetBoard))
            X_data.append(flatBoard)

        scoreList = self.getFCOutput(X_data)

        counter = 0
        for score in scoreList:
            score = math.fabs(score[0] - score[1])
            scoreListOffensive.append(score)

            if score > highestScore:
                highestScore = score
                highestScorePos = availablePos[counter]

            counter += 1

        self.storeVariance(np.var(scoreListOffensive))

        assert highestScorePos is not None
        return highestScorePos

    #####################################################
    # learn by history
    #####################################################
    def learnHistory2(self, X_training, Y_training):

        assert self.sessionFC is not None and self.graphFC is not None

        feed_dict_batch = {self.xFC: X_training, self.y_true_FC: Y_training}

        with self.graphFC.as_default() as g:
            self.sessionFC.run(self.optimizerFC, feed_dict=feed_dict_batch)

    #####################################################
    # learn by history
    # ToDo: Batches of learning data
    #####################################################
    def learnHistory(self, boardHistory, winningPlayerChar):

        if self.benchmarkPlayer or self.allData['prohibitLearn']:
            return

        self.increaseTotTrained()

        X_TrainingData = []
        Y_TrainingData = []

        goodTrainingValue = [self.NWOutputValue, 0]
        badTrainingValue = [0, self.NWOutputValue]

        totMoves = int(len(boardHistory) / 2)
        counter = 0.0
        counterIncrementer = 1 / float(totMoves)
        startIndex = int(len(boardHistory) / (self.historyDepthDiv)) - 2
        startIndex = 0
        if startIndex < 0:
            startIndex = 0

        for nextMove in boardHistory[startIndex:]:

            if not self.gameBoardOperations.compareCharacter(nextMove['characterSet'], winningPlayerChar):
                # ignore the loosing players move
                continue

            counter += counterIncrementer
            cleanBoard = self.gameBoardOperations.cleanupBoard(nextMove['board'])

            # This was a winning move.
            # Shall char be inverted?
            if self.gameBoardOperations.compareCharacter(winningPlayerChar, self.defs.characterO):
                cleanBoard = self.gameBoardOperations.invertBoard(cleanBoard)

            # Offset the board to where the winner set the move
            offsetBoard = self.gameBoardOperations.offsetBoard(nextMove['movePos'], cleanBoard)
            center = self.gameBoardOperations.getCenterCoord()

            for n in range(4):

                X_TrainingData.append(offsetBoard.flatten(len(offsetBoard)))
                Y_TrainingData.append(goodTrainingValue)

                ##### to see it from the other players persepctive
                # Teach the network to recognize this and block
                ## Invert the board
                inverted = self.gameBoardOperations.invertBoard(offsetBoard)
                inverted[center[0], center[1]] = self.defs.characterX

                X_TrainingData.append(inverted.flatten(len(inverted)))
                Y_TrainingData.append(goodTrainingValue)

                offsetBoard = self.gameBoardOperations.rotateBoard(offsetBoard, 1)

            # Learn the network what a bad move means..
            randomPos = self.gameBoardOperations.getRandomValidPos()
            randomPosBoard = self.gameBoardOperations.offsetBoard(randomPos, offsetBoard)
            # Dont forget to set your own caracter in the middle, so it looks real ;-)
            randomPosBoard[center[0], center[1]] = self.defs.characterX

            X_TrainingData.append(randomPosBoard.flatten(len(randomPosBoard)))
            Y_TrainingData.append(badTrainingValue)

        self.learnHistory2(X_TrainingData, Y_TrainingData)


    #####################################################
    # Function
    #####################################################
    def new_fc_layer(self,
                     input,          # The previous layer.
                     num_inputs,     # Num. inputs from prev. layer.
                     num_outputs,    # Num. outputs.
                     use_relu=True): # Use Rectified Linear Unit (ReLU)?

        # Create new weights and biases.
        weights = self.new_weights(shape=[num_inputs, num_outputs])
        biases = self.new_biases(length=num_outputs)

        # Calculate the layer as the matrix multiplication of
        # the input and weights, and then add the bias-values.
        layer = tf.matmul(input, weights) + biases

        # Use ReLU?
        if use_relu:
            layer = tf.nn.relu(layer)

        return layer

    #####################################################
    # Function
    #####################################################
    def new_conv_layer(self,
                       input,  # The previous layer.
                       num_input_channels,  # Num. channels in prev. layer.
                       filter_size,  # Width and height of each filter.
                       num_filters,  # Number of filters.
                       use_pooling=True):  # Use 2x2 max-pooling.

        # Shape of the filter-weights for the convolution.
        # This format is determined by the TensorFlow API.
        shape = [filter_size, filter_size, num_input_channels, num_filters]

        # Create new weights aka. filters with the given shape.
        weights = self.new_weights(shape=shape)

        # Create new biases, one for each filter.
        biases = self.new_biases(length=num_filters)

        # Create the TensorFlow operation for convolution.
        # Note the strides are set to 1 in all dimensions.
        # The first and last stride must always be 1,
        # because the first is for the image-number and
        # the last is for the input-channel.
        # But e.g. strides=[1, 2, 2, 1] would mean that the filter
        # is moved 2 pixels across the x- and y-axis of the image.
        # The padding is set to 'SAME' which means the input image
        # is padded with zeroes so the size of the output is the same.
        layer = tf.nn.conv2d(input=input,
                             filter=weights,
                             strides=[1, 1, 1, 1],
                             padding='SAME')

        # Add the biases to the results of the convolution.
        # A bias-value is added to each filter-channel.
        layer += biases

        # Use pooling to down-sample the image resolution?
        if use_pooling:
            # This is 2x2 max-pooling, which means that we
            # consider 2x2 windows and select the largest value
            # in each window. Then we move 2 pixels to the next window.
            layer = tf.nn.max_pool(value=layer,
                                   ksize=[1, 2, 2, 1],
                                   strides=[1, 2, 2, 1],
                                   padding='SAME')

        # Rectified Linear Unit (ReLU).
        # It calculates max(x, 0) for each input pixel x.
        # This adds some non-linearity to the formula and allows us
        # to learn more complicated functions.
        layer = tf.nn.relu(layer)

        # Note that ReLU is normally executed before the pooling,
        # but since relu(max_pool(x)) == max_pool(relu(x)) we can
        # save 75% of the relu-operations by max-pooling first.

        # We return both the resulting layer and the filter-weights
        # because we will plot the weights later.
        return layer, weights

    #####################################################
    # Function
    #####################################################
    def flatten_layer(self,
                      layer):
        # Get the shape of the input layer.
        layer_shape = layer.get_shape()

        # The shape of the input layer is assumed to be:
        # layer_shape == [num_images, img_height, img_width, num_channels]

        # The number of features is: img_height * img_width * num_channels
        # We can use a function from TensorFlow to calculate this.
        num_features = layer_shape[1:4].num_elements()

        # Reshape the layer to [num_images, num_features].
        # Note that we just set the size of the second dimension
        # to num_features and the size of the first dimension to -1
        # which means the size in that dimension is calculated
        # so the total size of the tensor is unchanged from the reshaping.
        layer_flat = tf.reshape(layer, [-1, num_features])

        # The shape of the flattened layer is now:
        # [num_images, img_height * img_width * num_channels]

        # Return both the flattened layer and the number of features.
        return layer_flat, num_features

    #####################################################
    # Function
    #####################################################
    def new_weights(self, shape):
        return tf.Variable(tf.truncated_normal(shape, stddev=0.05))

    #####################################################
    # Function
    #####################################################
    def new_biases(self, length):
        return tf.Variable(tf.constant(0.05, shape=[length]))

    #####################################################
    # Function
    #####################################################
    def getPlayerType(self):
        return "AI"

    #####################################################
    # Function
    #####################################################
    def getNWSize(self):
        return self.data['NWSize']['data']

    #####################################################
    # Function
    #####################################################
    def getHiddenLayerCount(self):
        return self.data['hiddenLayers']['data']

    #####################################################
    # Function
    #####################################################
    def getLearnRate(self):
        return self.data['learnRate']['data']
