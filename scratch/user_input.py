#!/usr/bin/env python3
# last updated on 2019/10/26

import curses

class Twod2small(object):

    def __init__(self, stdwin):

        curses.init_pair(1, 40, 0) # save green
        curses.init_pair(2, 9, 0) # red
        curses.init_pair(3, 255, 0) # white
        self.green = curses.color_pair(1)
        self.red = curses.color_pair(2)
        self.white = curses.color_pair(3)

        self.stdwin = stdwin

        # set the main window's rows and columns
        self.winheight = 29
        self.winwidth = 120

        # two 2d lists containing the input rows and cols for each part of the main window
        self.inputrow = [[5, 9, 13, 16, 18, 21, 23], [5, 9, 12, 14, 17, 19]]
        self.inputcol = [[36, 50], [int(self.winwidth/2) + 36, int(self.winwidth/2) + 50]]

        # measures is the list in which I store all the data inputed
        self.measures = [[["----", "----"] for i in range(7)], [["----", "----"] for i in range(6)]]
        self.kcell = "----"

        # current input side (ciside) is either 0 or 1, respectively for the left and right
        # part of the screen
        self.ciside = 0

        self.cirow = 0
        self.cicol = 0

        self.initScreen()
        self.inputMeasures()

    def initScreen(self):

        # don't show the screen until the terminal has the minimal dimensions
        while True:
            self.stdwin.erase()
            rows, cols = self.stdwin.getmaxyx()
            if rows < 35 or cols < 134:
                msg = "Make terminal at least 134x35"
                if rows > 3 and cols > len(msg):
                    self.stdwin.addstr(int(rows/2) - 1 + rows%2, int((cols - len(msg))/2), msg)
                ch = self.stdwin.getch()
            else:
                break

        self.stdwin.refresh()

        # draw the command window
        self.commandwin = curses.newwin(3, cols, rows - 3, 0)
        msg = "Press 'S' to save, 'Q' to quit."
        self.commandwin.addstr(1, int((cols - len(msg))/2), msg, curses.A_BOLD)
        self.commandwin.chgat(1, int((cols - len(msg))/2) + 7, 1, self.green|curses.A_BOLD)
        self.commandwin.chgat(1, int((cols - len(msg))/2) + 20, 1, self.red|curses.A_BOLD)
        self.commandwin.refresh()

        # set the y and x coordinates for the upper left corner of the measure window
        uly = int((rows - 2 - self.winheight)/2)
        ulx = int((cols - self.winwidth)/2)

        # create the window and enable the keypad
        self.measurewin = curses.newwin(self.winheight, self.winwidth, uly, ulx)
        self.measurewin.keypad(True)
        self.measurewin.border()

        # print the vertical bar separating the two areas of the window
        for i in range(self.winheight - 6):
            self.measurewin.addch(i + 2, int(self.winwidth/2), curses.ACS_VLINE)

        # print the horizontal bar at the bottom of the window
        for i in range(self.winwidth - 1):
            self.measurewin.addch(self.winheight - 3, i, curses.ACS_HLINE)

        # make the corners seamless
        self.measurewin.addch(self.winheight - 3, 0, curses.ACS_LTEE)
        self.measurewin.addch(self.winheight - 3, self.winwidth - 1, curses.ACS_RTEE)

        # print the windows entry points
        self.measurewin.addstr(2, self.inputcol[0][0] - 3, "1", self.white)
        self.measurewin.addstr(2, self.inputcol[0][1] - 3, "2", self.white)
        self.measurewin.addstr(2, self.inputcol[1][0] - 3, "1", self.white)
        self.measurewin.addstr(2, self.inputcol[1][1] - 3, "2", self.white)

        self.measurewin.addstr(5, 5, "A")
        self.measurewin.addstr(9, 5, "B")
        self.measurewin.addstr(13, 5, "C")
        self.measurewin.addstr(17, 5, "D")
        self.measurewin.addstr(16, 20, "D.I")
        self.measurewin.addstr(18, 20, "D.II")
        self.measurewin.addstr(22, 5, "E")
        self.measurewin.addstr(21, 20, "E.I")
        self.measurewin.addstr(23, 20, "E.II")

        self.measurewin.addstr(5, int(self.winwidth/2) + 5, "F")
        self.measurewin.addstr(9, int(self.winwidth/2) + 5, "G")
        self.measurewin.addstr(13, int(self.winwidth/2) + 5, "H")
        self.measurewin.addstr(12, int(self.winwidth/2) + 20, "H.I")
        self.measurewin.addstr(14, int(self.winwidth/2) + 20, "H.II")
        self.measurewin.addstr(18, int(self.winwidth/2) + 5, "J")
        self.measurewin.addstr(17, int(self.winwidth/2) + 20, "J.I")
        self.measurewin.addstr(19, int(self.winwidth/2) + 20, "J.II")

        # print each value of measures at the proper place
        for i, side in enumerate(self.measures):
            for j, row in enumerate(side):
                for k, measure in enumerate(row):
                    self.measurewin.addstr(self.inputrow[i][j], self.inputcol[i][k] - 4,
                                                                 "{} \"".format(measure))

        self.measurewin.addstr(self.winheight - 2, int(self.winwidth/2) - 2, "{} K".format(self.kcell))
        self.measurewin.refresh()

    def inputMeasures(self):

        # if kcell is True I'm in the 11th cell
        kcell = False

        # I only display the cursor when its counter is a multiple of 2
        cursorcntr = 0

        while True:

            i = self.ciside
            j = self.cirow
            k = self.cicol

            if kcell == False:
                row = self.inputrow[i][j]
                col = self.inputcol[i][k]
            else:
                row = self.winheight - 2
                col = int(self.winwidth/2) + 2

            # If the current cell is empty a blank space is added
            if (((kcell == False and self.measures[i][j][k] == "----")
            or (kcell == True and self.kcell == "----")) and cursorcntr%2 == 0):
                self.measurewin.addstr(row, col - 4, "    ")
                chars = []

            # if it isn't, I save the current characters of the entry of the cell
            # in a list called chars
            else:
                if kcell == False:
                    chars = list(self.measures[i][j][k])
                else:
                    chars = list(self.kcell)

            while True:

                # display the cursor only if cursorcntr is even
                if cursorcntr%2 == 0:
                    curses.curs_set(1)
                ch = self.measurewin.getch(row, col)
                curses.curs_set(0)

                # If the user hits the enter key, the cursor counter's value is flipped and
                # I exit the main loop
                if ch == 10:
                    cursorcntr += 1
                    break

                # I also exit the loop if one of the following conditions if verified
                if ((ch == curses.KEY_UP and j > 0)
                or (ch == curses.KEY_DOWN and kcell == False)
                or (ch == curses.KEY_LEFT and (i != 0 or k != 0) and kcell == False)
                or (ch == curses.KEY_RIGHT and (i != 1 or k != 1) and kcell == False)
                or (ch in [ord("s"), ord("S")])
                or (ch in [ord("q"), ord("Q")])):
                    break

                # If the user hits the backspace key and there are characters to be removed,
                # they are removed
                elif ch == 127 and len(chars) > 0 and cursorcntr%2 == 0:
                    chars.pop(len(chars) - 1)
                    self.measurewin.addstr(row, col - len(chars) - 1, " " + "".join(chars))

                # If the user resizes the screen I call the initScreen method and reprint the
                # whole screen
                elif ch == curses.KEY_RESIZE:
                    self.initScreen()
                    self.measurewin.addstr(row, col - 4, " "*4)
                    if len(chars) > 0:
                        self.measurewin.addstr(row, col - len(chars), "".join(chars))

                # if the key entered is none of the above I try to see if it's a number (or the
                # character '.'). If it is, I add it to the chars list and print it on screen
                else:
                    try:
                        if (chr(ch).isdigit() or ch == ord(".")) and len(chars) < 6 and cursorcntr%2 == 0:
                            chars.append(chr(ch))
                            self.measurewin.addstr(row, col - len(chars), "".join(chars))
                    except ValueError:
                        pass

            # At this point I have exited the main loop and I check whether or not chars is empty or
            if len(chars) > 0:
                if kcell == False:
                    self.measures[i][j][k] = "".join(chars)
                else:
                    self.kcell = "".join(chars)
            else:
                if kcell == False:
                    self.measures[i][j][k] = "----"
                else:
                    self.kcell = "----"
                self.measurewin.addstr(row, col - 4, "----")

            # here I check which key has been entered that caused me to exit the loop, and
            # perform actions accordingly for every option
            if ch == curses.KEY_UP:
                if kcell == True:
                    kcell = False
                else:
                    self.cirow -= 1
                # If I pressed an arrow key the value of the cursor counter is always set to a
                # multiple of two (which means that when an arrow key is entered I will always
                # get a blinking cursos in the destination cell)
                cursorcntr *= 2

            elif ch == curses.KEY_DOWN:
                if (i == 0 and j == 6) or (i == 1 and j == 5):
                    kcell = True
                else:
                    self.cirow += 1
                cursorcntr *= 2

            elif ch == curses.KEY_LEFT:
                self.cicol -= 1
                if i == 1 and k == 0:
                    self.ciside -= 1
                    self.cicol += 2
                cursorcntr *= 2

            elif ch == curses.KEY_RIGHT:
                self.cicol += 1
                if i == 0 and k == 1:
                    self.ciside += 1
                    self.cicol -= 2
                    if self.cirow == 6:
                        self.cirow -= 1
                cursorcntr *= 2

            # check If the user wants to save/quit
            elif ch in [ord("s"), ord("S")]:
                self.exit("save")

            elif ch in [ord("q"), ord("Q")]:
                self.exit("quit")

    def exit(self, saveorquit):

        if saveorquit == "save":
            self.save()

        raise SystemExit

    def save(self):
        pass

if __name__ == "__main__":
    curses.wrapper(Twod2small)