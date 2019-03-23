### Reinforcment learning 5 in a Row - Gomoku
This project implements a program that will perform un-supervised learning, e.g. reinforcement learning,
in order to master the game Gomoku. The project is based on the raw tensorflow API, and the algoritm will
train so the AI will play the game quite ok.  The purpose, however, has never been to create the most
skilled game, but to truly understand reinforcement learning by writing this program.  And, what everyone
that truly knows reinforcement learning knows is: It is impossible to truly understand reinforcement learning.

The code is out-of-the-box runable if you have the proper python environment setup. It will start from nothing 
and train a number of AI players, the only thing available for them to learn is that a referee will tell who wins
every game, and the loosing player will have the chance to learn from the player that just won. There will be one
player that is the best at all times, and this player is not allowed to train (in order not to over train it), its
only purpose is to train other new AI players how to play, and hopefully the new players will eventually beat the
current master. When a master is beaten it is allowed to start training again and the new master will stop train.
This means the best player of a tournament can only get better or stay the same, never become worse. 

In order to get a measure to see what player shall be elected master, a "Q-player", or a validation player, or a benchmark 
player is playing all AI players to see who wins. The Q-player is a very simple algortim that plays the game. But, no AI
player is never allowed to learn from the Q-player.

