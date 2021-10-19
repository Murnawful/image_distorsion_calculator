import tkinter as tk
from tkinter import ttk
import tkinter.filedialog as fd
import os
from tkinter.messagebox import showerror


class FileManager(tk.Frame):

    def __init__(self, container):
        super().__init__(container)

        self.filenames = []
        self.files_directory = None
        self.selected_files = None
        self.listbox = None

        self.parent = container

        self.init_filemanager_frame()

    def init_filemanager_frame(self):
        open_button = ttk.Button(self, text='Open DICOM files', command=self.select_file)
        open_button.grid(column=0, row=2, sticky='ew', padx=0, pady=0)
        add_button = ttk.Button(self, text='Add DICOM files', command=self.add_file)
        add_button.grid(column=1, row=2, sticky='ew', padx=0, pady=0)
        delete_button = ttk.Button(self, text='Delete DICOM files', command=self.delete_file)
        delete_button.grid(column=2, row=2, sticky='ew', padx=0, pady=0)

        self.listbox = tk.Listbox(self, listvariable=self.filenames, height=6, width=50, selectmode='extended')
        self.listbox.grid(columnspan=3, row=0, sticky='nwes')

        scrollbar_y = ttk.Scrollbar(self, orient='vertical', command=self.listbox.yview)
        self.listbox['yscrollcommand'] = scrollbar_y.set
        scrollbar_y.grid(column=4, row=0, sticky='ns')
        scrollbar_x = ttk.Scrollbar(self, orient='horizontal', command=self.listbox.xview)
        self.listbox['xscrollcommand'] = scrollbar_x.set
        scrollbar_x.grid(columnspan=3, row=1, sticky='ew')
        self.listbox.bind('<<ListboxSelect>>', self.select_files_in_frame)

    def select_file(self):
        filetypes = (
            ('DICOM files', '*.dcm'),
            ('All files', '*.*')
        )

        self.filenames = fd.askopenfiles(filetypes=filetypes)
        self.files_directory = os.path.split(self.filenames[0].name)[0]
        for f in self.filenames:
            self.listbox.insert(tk.END, f.name.replace(self.files_directory, ''))

    def add_file(self):
        filetypes = (('DICOM files', '*.dcm'),
                     ('All files', '*.*'))

        new_files = fd.askopenfiles(initialdir=self.files_directory, filetypes=filetypes)
        for nf in new_files:
            self.filenames.append(nf)
            self.listbox.insert(tk.END, nf.name.replace(self.files_directory, ''))

    def delete_file(self):
        try:
            for index in self.selected_files[::-1]:
                self.listbox.delete(index)
                self.filenames.pop(index)
        except TypeError:
            showerror(title='Error', message="No file was selected")

    def select_files_in_frame(self, event):
        self.selected_files = self.listbox.curselection()
