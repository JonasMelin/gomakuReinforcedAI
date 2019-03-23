import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import time

# ##################################################################
# Class for visuzalizing to user, e.g. game board, array plots..
# ##################################################################
class luffVisualizer(object):
    def __init__(self):
        plt.ylim(ymin=-1, ymax=2)
        self.addedSubplots = 0

        font = {'size': 5}

        matplotlib.rc('font', **font)

    # ##################################################################
    # Plots and displays matrix.. typically a game board.
    # ##################################################################
    def plotBoard(self, board, sleep=1, name="no name", callback=None):

        plt.close()
        fig, ax = plt.subplots()

        if callback is not None:
            fig.canvas.mpl_connect('button_press_event', callback)

        ax.grid(color='r', linestyle='-', linewidth=1, which='both')

        ax.matshow(board)
        self.render(sleep, name)


    # ##################################################################
    # Plots and display an array.. it will be a 2d graph..
    # ##################################################################
    def plotArray(self, array, sleep=1, name="no name"):
        plt.close()
        plt.plot(array)
        self.render(sleep, name)

    # ##################################################################
    # render
    # ##################################################################
    def render(self, sleep = 1, name = "no name"):

        plt.ion()
        plt.show()
        plt.draw()
        plt.gcf().canvas.set_window_title(name)
        plt.pause(sleep)

    # ##################################################################
    # reset. So you can start adding new plots.
    # ##################################################################
    def plotReset(self, dimx=2, dimy=2):
        plt.close()
        self.addedSubplots = 0
        self.dimx=dimx
        self.dimy=dimy

    # ##################################################################
    # Plots a array.. it will be a 2d graph..
    # ##################################################################
    def plotAddForMultiple(self, array, name="no name"):
        self.addedSubplots += 1
        if self.addedSubplots > (self.dimx * self.dimy):
            print("Only place for {} plots. call plotReset() to start over".format(self.dimx * self.dimy))
            return

        plt.subplot(self.dimx,self.dimy,self.addedSubplots).title.set_text(name)
        plt.plot(array)
        plt.tight_layout()

    def tensorBoard(self):
        from tensorboardX import SummaryWriter
        writer = SummaryWriter("./tmp/")
        for i in range(50):
            writer.add_histogram("moving_gauss", np.random.normal(i, i, 1000), i, bins="auto")
        writer.close()

    # ##################################################################
    # Self tests
    # ##################################################################
    def testMyself(self):

        self.tensorBoard()

        self.plotReset(dimx=4, dimy=2)
        plot1 = [6,5,4,3,2,1,9]
        plot2 = [1, 2, 3, 4, 4, 4, 5, 6]
        plot3 = [[0.1, 0.2],[0.2, 0.5]]  # Multiple in once
        plot4 = [1,1,1,45,46,43,47]
        plot5 = [6,5,4,3,2,1,9]
        plot6 = [1, 2, 3, 4, 4, 4, 5, 6]
        plot7 = [[0.1, 0.2],[0.2, 0.5]]  # Multiple in once
        plot8 = [1,1,1,45,46,43,47]
        self.plotAddForMultiple(plot1, name="plot1")
        self.plotAddForMultiple(plot2, name="plot2")
        self.plotAddForMultiple(plot3, name="plot3")
        self.plotAddForMultiple(plot4, name="plot4")
        self.plotAddForMultiple(plot1, name="plot5")
        self.plotAddForMultiple(plot2, name="plot6")
        self.plotAddForMultiple(plot3, name="plot7")
        self.plotAddForMultiple(plot4, name="plot8")
        self.render()

        plot5= np.zeros(shape=[3,3])
        plot5[0,0] = 3
        self.plotBoard(plot5, sleep=3, name="NAMN")

        self.plotReset()
        plot1 = [6,5,4,3,2,1,9]
        plot2 = [1, 2, 3, 4, 4, 4, 5, 6]
        plot3 = [[0.1, 0.2],[0.2, 0.5]]  # Multiple in once
        plot4 = [1,1,1,45,46,43,47]
        self.plotAddForMultiple(plot1, name="plot1")
        self.plotAddForMultiple(plot2, name="plot2")
        self.plotAddForMultiple(plot3, name="plot3")
        self.plotAddForMultiple(plot4, name="plot4")
        self.render()




#luffVisualizer().testMyself()

