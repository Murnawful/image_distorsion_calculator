import tkinter as tk
from tkinter import ttk
import tkinter.filedialog as fd


class FileManager(tk.Frame):
    def __init__(self):
        super().__init__()

        self.filenames = None

        open_button = ttk.Button(self,
                                 text='Open DICOM files',
                                 command=self.select_file)

        open_button.grid(column=0, row=2, sticky='w', padx=10, pady=10)

        self.listbox = tk.Listbox(self,
                                  listvariable=self.filenames,
                                  height=6,
                                  width=100,
                                  selectmode='extended')
        self.listbox.grid(column=0,
                          row=0,
                          sticky='nwes')
        scrollbar_y = ttk.Scrollbar(self,
                                    orient='vertical',
                                    command=self.listbox.yview)
        self.listbox['yscrollcommand'] = scrollbar_y.set
        scrollbar_y.grid(column=1,
                         row=0,
                         sticky='ns')
        scrollbar_x = ttk.Scrollbar(self,
                                    orient='horizontal',
                                    command=self.listbox.xview)
        self.listbox['xscrollcommand'] = scrollbar_x.set
        scrollbar_x.grid(column=0,
                         row=1,
                         sticky='ew')

    def select_file(self):
        filetypes = (
            ('DICOM files', '*.dcm'),
            ('All files', '*.*')
        )

        self.filenames = fd.askopenfiles(filetypes=filetypes)

        for f in self.filenames:
            self.listbox.insert(tk.END, f.name)

