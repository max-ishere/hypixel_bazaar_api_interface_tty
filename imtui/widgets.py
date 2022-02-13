from enum import Enum, auto
from dataclasses import dataclass
from curses.textpad import rectangle
import curses


class Location(Enum):
    Center = auto()
    Top = auto()
    Bottom = auto()
    Left = auto()
    Right = auto()

@dataclass(kw_only=True)
class Frame:
    title: str = None
    vallign: Location = Location.Center
    voffset: int = 0
    height: int

    hallign: Location = Location.Center
    hoffset: int = 0
    width: int

    def CreateCursesWindow(self, stdscr):
        return curses.newwin(self.height, self.width, *WidgetCorner(stdscr, self))

@dataclass(kw_only=True)
class Label:
    text: str
    style: int = curses.A_NORMAL
    vallign: Location = Location.Top
    voffset: int = 0
    height: int

    hallign: Location = Location.Left
    hoffset: int = 0
    width: int

@dataclass(kw_only=True)
class Table:
    data: dict
    header_style: int = curses.A_BOLD
    data_style: int = curses.A_NORMAL
    lines_style: int =curses.A_DIM
    vallign: Location = Location.Top
    voffset: int = 0
    height: int

    hallign: Location = Location.Left
    hoffset: int = 0
    width: int

@dataclass(kw_only=True)
class InputField:
    prompt: str = ''
    prompt_style: int = curses.A_DIM
    look: str = '[ {} ]'
    look_style: int = curses.A_BOLD
    max_lenght: int
    text: str = ''
    password: bool = False

    vallign: Location = Location.Top
    voffset: int = 0
    height: int = 1

    hallign: Location = Location.Left
    hoffset: int = 0

    @property
    def width(self):
        return len(self.look.format(' ' * self.max_lenght))

    def GetInput(self, stdscr) -> str:
        selfy, selfx = WidgetCorner(stdscr, self)
        scry, scrx = stdscr.getbegyx()
        y = selfy + scry
        x = selfx + scrx

        win = curses.newwin(1, self.max_lenght, y, x + self.look.index('{'))
        textbox = curses.textpad.Textbox(win)

        if self.password:
            win.attron(curses.A_INVIS | curses.A_REVERSE | curses.A_DIM)

        curses.curs_set(1)
        textbox.edit()
        curses.curs_set(0)

        result =  str(textbox.gather()).strip('\n').rstrip()
        if self.password:
            win.clear()
            RenderLabel(stdscr, Label(text='*' * self.max_lenght,
                                      vallign=self.vallign,
                                      voffset=self.voffset,
                                      height=1,
                                      hallign=self.hallign,
                                      hoffset=self.hoffset + self.look.index('{'),
                                      width=self.max_lenght))

        return result

@dataclass(kw_only=True)
class ProgressBar:
    style_empty: int = curses.A_DIM | curses.A_STANDOUT
    style_completed: int = curses.A_STANDOUT
    progress_total: int
    progress: int = 1
    status: str

    vallign: Location = Location.Top
    voffset: int = 0

    @property
    def height(self):
        return 1

    hallign: Location = Location.Left
    hoffset: int = 0
    width: int

    def IncrementStatus(self, new_status:str, increment:int=1):
        self.status = new_status
        self.progress += 1
        if self.progress > self.progress_total:
            self.progress = self.progress_total

def WidgetCorner(stdscr, widget) -> tuple:
    scrheight, scrwidth = stdscr.getmaxyx()

    if widget.vallign == Location.Top:
        y = 0 + widget.voffset

    if widget.vallign == Location.Center:
        y = int(scrheight / 2 + widget.voffset - widget.height / 2 - 1)

    if widget.vallign == Location.Bottom:
        y = scrheight - widget.height + widget.voffset

    y = min(scrheight - widget.height, max(0, y))

    if widget.hallign == Location.Left:
        x = 0 + widget.hoffset

    if widget.hallign == Location.Center:
        x = int(scrwidth / 2 + widget.hoffset - widget.width / 2 + 1)

    if widget.hallign == Location.Right:
        x = scrwidth - widget.width + widget.hoffset

    x = min(scrwidth - widget.width, max(0, x))

    return (y, x)

def RenderBorder(stdscr, widget):
    y, x = WidgetCorner(stdscr, widget)

    rectangle(stdscr, y-1,x-1,
              y + widget.height,
              x + widget.width)
    stdscr.refresh()

def RenderTitle(stdsrc, widget, params = curses.A_NORMAL, full_width:bool=False, allignment:Location=Location.Left, offset:int=1):
    y, x = WidgetCorner(stdsrc, widget)
    assert x >= 1 and y >= 1

    title_offset = 0
    max_title_length = min(1 + widget.width + 1, len(widget.title))

    if allignment == Location.Left:
        title_offset += offset

    if allignment == Location.Center:
        title_offset += int(1 + widget.width / 2 - max_title_length / 2 + offset)

    if allignment == Location.Right:
        title_offset += 1 + widget.width + 1 + offset - max_title_length

    title_offset = max(0, min(1 + widget.width + 1 - 2, title_offset))

    if full_width:
        stdsrc.addstr(y - 1, x - 1, ' ' * (1 + widget.width + 1), params)

    renderable_characters = 1 + widget.width + 1 - title_offset

    title = widget.title[0:renderable_characters] if renderable_characters != 0 else ''
    stdsrc.addstr(y - 1, x - 1 + title_offset, title, params)
    stdsrc.refresh()

def RenderLabel(stdscr, label:Label):
    y, x = WidgetCorner(stdscr, label)
    stdscr.addstr(y, x, label.text, label.style)
    stdscr.refresh()

def RenderTable(stdscr, table:Table):
    y, x = WidgetCorner(stdscr, table)

    stdscr.addstr(y, x, ' | ' + ' | '.join([name for name in table.data]), table.header_style)

    key_lenghts = 0
    for key in table.data:
        row_num = 0
        for row in table.data.get(key, []):
            stdscr.addstr(y + 2 + row_num, x + key_lenghts, ' | ' + str(row), table.data_style)
            row_num += 1
        key_lenghts += len(key) + 3

    stdscr.refresh()

def RenderInputField(stdscr, field: InputField):
    y, x = WidgetCorner(stdscr, field)

    stdscr.addstr(y, x, field.look.format(' ' * field.max_lenght), field.look_style)
    stdscr.addstr(y, x, field.prompt, field.prompt_style)
    stdscr.refresh()

def RenderProgressBar(stdscr, progress_bar: ProgressBar):
    y, x = WidgetCorner(stdscr, progress_bar)

    filled_width = int(round(progress_bar.width / progress_bar.progress_total * progress_bar.progress))

    for ch in range(0, progress_bar.width):
        attr = progress_bar.style_completed if ch < filled_width else progress_bar.style_empty
        if ch < len(progress_bar.status):
            stdscr.addch(y, x + ch, progress_bar.status[ch], attr)
        else:
            stdscr.addch(y, x + ch, ' ', attr)

    stdscr.refresh()

def AskOptions(stdscr, options:str, default:str=None) -> str:
    while True:
        opt = stdscr.getch()
        for ch in options:
            if opt == ord(ch):
                return ch
        else:
            if default != None:
                return default
