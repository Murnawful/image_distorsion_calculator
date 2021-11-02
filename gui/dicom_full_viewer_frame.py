from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
import tkinter as tk


class DicomFullViewerFrame(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
