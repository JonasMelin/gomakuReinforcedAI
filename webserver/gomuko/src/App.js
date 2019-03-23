import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';
import ReactDOM from 'react-dom';

var characterNone = 0.0
var characterX = 1.0
var characterO = -1.0

/* ----------------------------------------------------------
/  TBD
   --------------------------------------------------------*/
class Square extends React.Component {

  /* ----------------------------------------------------------
  /  TBD
   --------------------------------------------------------*/
  constructor(props){
    super(props)
    this.status = {};
    this.status['callback'] = props.callback;
    this.status['myKeyX'] = props.myKeyX;
    this.status['myKeyY'] = props.myKeyY;
    this.status['globData'] = props.globData;
  }

  /* ----------------------------------------------------------
  /  TBD
   --------------------------------------------------------*/
  convertValueToDisplayValue(value){

    if (value <= (characterO+0.01)){
        return 'O';
    }
    if (value >= (characterX-0.01)){
        return 'X';
    }

    return '_';
  }

  /* ----------------------------------------------------------
  /  TBD
   --------------------------------------------------------*/
  render() {

    return (
      <button key="nisse" className="square" onClick={() => this.status.callback(this.status.myKeyX, this.status.myKeyY)}>
        {this.convertValueToDisplayValue(this.status.globData[this.status.myKeyX][this.status.myKeyY])}
      </button>
    );
  }
}

/* ----------------------------------------------------------
/  TBD
   --------------------------------------------------------*/
class Board extends React.Component {

  /* ----------------------------------------------------------
  /  TBD
   --------------------------------------------------------*/
  constructor(props){
      super(props);

       var matrix = [];
            for(var i=0; i<17; i++) {
                matrix[i] = [];
                for(var j=0; j<17; j++) {
                matrix[i][j] = characterNone;
            }
        }

        this.state = {'board' : {'theMatrix':  matrix, 'lastMove': [-1,-1]}};
        this.state['humanTurn'] = true;
        this.state['backendFailure'] = false;
        this.state['humanWinner'] = false;
        this.state['aiWinner'] = false;
  }

  /* ----------------------------------------------------------
  /  TBD
   --------------------------------------------------------*/
  isPosFree(X, Y){
    if ((this.state.board.theMatrix[X][Y] < (characterNone - 0.01))  ||
        (this.state.board.theMatrix[X][Y] > (characterNone + 0.01))){
            return false;
        }else{
            return true;
        }
  }

  /* ----------------------------------------------------------
  /  TBD
   --------------------------------------------------------*/
  onClick(X, Y){
    //console.log("X: " + X + " Y: "+Y)

    if(this.state.humanWinner || this.state.aiWinner){
        return
    }

    if(!this.state.humanTurn){
        console.log("Wait for  your turn..");
        return;
    }

    if (!this.isPosFree(X, Y)){
        console.log("Pos Already taken. X: "+X + " Y: "+ Y)
        return;
    }

    this.setState({'humanTurn' : false})

    this.state.board.theMatrix[X][Y]=characterX;
    this.state.board.lastMove[0]=X;
    this.state.board.lastMove[1]=Y;
    this.setState({'trigger' : 5})
    this.communicateWithAI()

  }

  /* ----------------------------------------------------------
  /  TBD
   --------------------------------------------------------*/
  renderSquares(){

    var rows = [];
        for (var i = 0; i < 15; i++) {
            for (var j = 0; j < 15; j++) {
                //console.log(counter)
                // note: we add a key prop here to allow react to uniquely identify each
                // element in this array. see: https://reactjs.org/docs/lists-and-keys.html
                rows.push(<Square globData={this.state.board.theMatrix} myKeyX={i} myKeyY={j} callback={this.onClick.bind(this)}/>);
            }
            rows.push(<br/>);
    }
     return rows;
  }

  /* ----------------------------------------------------------
  /  TBD
     --------------------------------------------------------*/
  communicateWithAI(){

    console.log(JSON.stringify(this.state.board))

        fetch('http://213.89.208.227:5000/'+JSON.stringify(this.state.board.theMatrix)+'/'+JSON.stringify(this.state.board.lastMove)).then(function(response) {
            //console.log("response "+response)
	        return response.json()
            }.bind(this)).then(function(returnedValue) {
                if ((returnedValue['result'] == undefined) ||
                    (returnedValue['result'] != "OK")){
                    console.log("Bad server response")
                    this.setState({'backendFailure' : true})
                    return
                }

                if (returnedValue['winner'] != undefined){
                    if (returnedValue['winner'] == "human"){
                        console.log("Human won")
                        this.setState({'humanWinner' : true})
                        return
                    }else{
                        console.log("AI won")
                        this.setState({'aiWinner' : true})
                    }

                }
                //console.log("retval "+returnedValue['result'])

                this.state.board.theMatrix[returnedValue['X']][returnedValue['Y']]=characterO;
                this.setState({'humanTurn' : true})
            }.bind(this)).catch(function(err) {
                console.log("ERROR")
                this.setState({'backendFailure' : true})
        }.bind(this));



  }

  /* ----------------------------------------------------------
  /  TBD
     --------------------------------------------------------*/
  render() {
    var status = '';

    if (this.state.humanTurn){
        status="Your turn!!"
    }else{
        status="Wait for AI to make move!!"
    }
    if(this.state.backendFailure){
        status="Something failed. Even AI has feelings!! Hit F5 or something.."
    }
    if(this.state.humanWinner){
        status="YOU WON!!! (press F5 to play again)"
    }
        if(this.state.aiWinner){
        status="AI WON!!! (press F5 to play again)"
    }

    return (
      <div>
        <div className="status">{status}</div>
        <div className="board-row">
          {this.renderSquares(this.state.board.theMatrix)}
        </div>
        <div >

        </div>
      </div>
    );
  }
}

/* ----------------------------------------------------------
/  TBD
   --------------------------------------------------------*/
class Game extends React.Component {


  /* ----------------------------------------------------------
  /  TBD
     --------------------------------------------------------*/
  render() {


    return (
      <div className="game">
        <div className="game-board">
          <Board />
        </div>
        <div className="game-info">
          <div>Gomuko AI game, by Jonas Melin 2018</div>
          <div>
          <p>Based on Tensorflow, unsupervised reinforcement learning.</p>
          <p>The computer has learned to play the game by itself by combining evolutionary algorithms with machine learning.</p>
          <p>This particular neural network has two hidden layers, and is built using fully connected layers, 6000 neurons per layer</p>
          <p>Full source code at Github <a href="https://github.com/JonasMelin/TensorFlowExperiments/tree/master/luff">here</a></p>

          </div>
          <ol>{/* TODO */}</ol>
        </div>
      </div>
    );
  }
}

/* ----------------------------------------------------------
/  TBD
   --------------------------------------------------------*/
ReactDOM.render(
  <Game />,
  document.getElementById('root')
);

export default Game;