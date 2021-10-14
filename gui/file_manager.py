import tkinter as tk
from tkinter import ttk
import tkinter.filedialog as fd


class FileManager(tk.Frame):
    def __init__(self, container):
        super().__init__(container)

        self.filenames = []

        open_button = ttk.Button(self,
                                 text='Open DICOM files',
                                 command=self.select_file)
        open_button.grid(column=0, row=2, sticky='w', padx=10, pady=10)
        add_button = ttk.Button(self,
                                text='Add DICOM files',
                                command=self.add_file)
        add_button.grid(column=1, row=2, sticky='w', padx=10, pady=10)
        delete_button = ttk.Button(self,
                                   text='Delete DICOM files',
                                   command=self.add_file)
        delete_button.grid(column=2, row=2, sticky='w', padx=10, pady=10)

        self.listbox = tk.Listbox(self,
                                  listvariable=self.filenames,
                                  height=6,
                                  width=80,
                                  selectmode='extended')
        self.listbox.grid(columnspan=2,
                          row=0,
                          sticky='nwes')
        scrollbar_y = ttk.Scrollbar(self,
                                    orient='vertical',
                                    command=self.listbox.yview)
        self.listbox['yscrollcommand'] = scrollbar_y.set
        scrollbar_y.grid(column=3,
                         row=0,
                         sticky='ns')
        scrollbar_x = ttk.Scrollbar(self,
                                    orient='horizontal',
                                    command=self.listbox.xview)
        self.listbox['xscrollcommand'] = scrollbar_x.set
        scrollbar_x.grid(columnspan=3,
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

    def add_file(self):
        filetypes = (
            ('DICOM files', '*.dcm'),
            ('All files', '*.*')
        )

        new_files = fd.askopenfiles(filetypes=filetypes)
        for nf in new_files:
            self.filenames.append(nf)
            self.listbox.insert(tk.END, nf.name)

    def delete_file(self):
        pass
