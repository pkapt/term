import curses 

class CursesString():
    '''
    @param stdscr curses obj
    @param text string to display
    @param x, y coordinates of string (can negative index)
    @param fill fill the rest of the line with spaces
    '''
    def __init__(self, window, text, color, x, y, fill=None, vis=True):
        self.text = text
        self.color = color
        self.x = x
        self.y = y
        self.fill = fill
        self.window = window
        self.vis = vis
        self._render()
    
    def _render(self):
        if self.vis:
            height, width = self.window.getmaxyx()
            if self.y < 0:
                self.y = height + self.y
            if self.x < 0:
                self.x = width + self.x
            self.window.attron(curses.color_pair(self.color))
            self.window.addstr(self.y, self.x, self.text)
            if self.fill == -1:
                self.window.addstr(self.y, len(self.text)+self.x, " " * 10)
            self.window.attroff(curses.color_pair(self.color))
            self.window.refresh()