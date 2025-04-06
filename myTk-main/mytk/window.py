from tkinter import *
from tkinter import filedialog
import tkinter.ttk as ttk
import tkinter.font as tkFont
from tkinter.messagebox import askyesno

from .base import *


class Window(Base):
    def __init__(self, geometry=None, title="Untitled"):
        super().__init__()

        self.widget = Tk()
        self.widget.geometry(geometry)
        self.title = title

    @property
    def on_close(self, title, message):
        print('on_close')
        ans = askyesno(title, message)
        if ans:
            self.widget.destroy()
        return ans
    
    @on_close.setter
    def on_close(self, value):
        self.widget.protocol("WM_DELETE_WINDOW", value)

    @property
    def title(self):
        return self.widget.title()

    @title.setter
    def title(self, value):
        self.widget.title(value)

    @property
    def resizable(self):
        (width, height) = self.widget.resizable()
        return (width or height) != 0

    @resizable.setter
    def is_resizable(self, value):
        self.widget.resizable(value, value)
