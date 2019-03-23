from flask import Flask
from flask import jsonify
from flask_cors import CORS
import json
import numpy
import luffAIPlayer3
import definitions as defs
import luffGameBoard

app = Flask(__name__)
cors = CORS(app)

AIPlayerName="W8277"
AIPlayer = luffAIPlayer3.luffAIPlayer3(defs.definitions().characterX, AIPlayerName)



# ################################################################
# TBD
# ################################################################
@app.route("/")
def hello():
    return "Gomuko server is running!"


# ################################################################
# TBD
# ################################################################
@app.route("/<string:gameBoard>/<string:lastMove>")
def hello2(gameBoard, lastMove):

    try:
        incomingGameBoard = numpy.asarray(json.loads(gameBoard))

        if incomingGameBoard.ndim is not 2:
            print("Wrong dimensions 1")
            raise Exception("wrong diemnsion of matrix")

        if incomingGameBoard.size  != defs.definitions().boardSize * defs.definitions().boardSize:
            print("Wrong dimensions. incoming {a} expected {b}".format(a=len(incomingGameBoard), b=defs.definitions().boardSize * defs.definitions().boardSize))
            raise Exception("wrong diemnsion of matrix")

    except:
        print("Wrong syntax")
        ErrorResponse = {'result' : "NOK"}
        return jsonify(ErrorResponse)

    okResp = {'result': "OK"}
    gb = luffGameBoard.luffGameBoard(incomingGameBoard)

    if gb.countConsequentChars(json.loads(lastMove), defs.definitions().characterX) >= 5:
        print("WINNER X")
        okResp['winner'] = "human"
        return jsonify(okResp)

    selPos = AIPlayer.calcOutputGetPos(gb, gb.getInterestingPositionsRAW())

    if gb.setCharacter(selPos, defs.definitions().characterO):
        print("WINNER O")
        okResp['winner'] = "ai"

    okResp['X'] = selPos[0]
    okResp['Y'] = selPos[1]
    return jsonify(okResp)

# ################################################################
# RUN the server!
# ################################################################
app.run(host='0.0.0.0')