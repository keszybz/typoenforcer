#!/usr/bin/python
# -*- coding:utf-8; -*-

import sys
import Tkinter as tk, tkFileDialog
import pykey

LONG_TITLE = 'TypoEnforcer'
SHORT_TITLE = 'TE: {0}'

class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.grid(sticky='nesw')
        self.createWidgets()
        self.outputHandlers = [self.debugOutputHandler,
                               self.windowOutputHandler]
        self.master.title(LONG_TITLE)
        self.target = None

    def set_text(self, *lines):
        self.theText.delete(0, tk.END)
        for line in lines:
            self.theText.insert(tk.END, line)
        self.gotoLine(0)

    def createWidgets(self):
        top = self.winfo_toplevel()
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        self.quitButton = tk.Button(self, text='Quit', command=self.quit)
        self.quitButton.grid()

        self.fileButton = tk.Button(self, text='Load file',
                                    command=self.fileHandler)
        self.fileButton.grid()

        self.targetButton = tk.Button(self, text='Set target',
                                      command=self.targetHandler)
        self.targetButton.grid()

        self.theText = tk.Listbox(self, height=50, width=72,
                                  selectmode=tk.EXTENDED)
        self.theText.bind('<KeyPress-Return>', self.keyHandler)
        self.theText.focus_set()
        self.theText.grid(sticky='nesw')

    def debugOutputHandler(self, *lines):
        for line in lines:
            print 'output ->', line

    def windowOutputHandler(self, *lines):
        if self.target is None:
            return
        for line in lines:
            print 'sending line:', line
            pykey.send_string(self.target, line + '\n')
            pykey.display.sync()

    def gotoLine(self, index):
        self.theText.see(index)
        self.theText.activate(index)
        self.theText.selection_set(index)

    def keyHandler(self, event):
        print 'got:', event
        selected = [int(index) for index in self.theText.curselection()]
        print 'selected:', selected
        if not selected:
            return
        first, last = min(selected), max(selected)
        lines = self.theText.get(first, last)

        # fix for get(0, 0) returning justs a single string
        if isinstance(lines, basestring):
            lines = [lines]
        for handler in self.outputHandlers:
            handler(*lines)
        self.theText.selection_clear(first, last)
        self.gotoLine(last + 1)

    def fileHandler(self, filename=None):
        if filename is None:
            filename = tkFileDialog.askopenfilename()
        input = open(filename).read()
        self.master.title(SHORT_TITLE.format(filename))
        self.set_text(*input.split('\n'))

    def targetHandler(self, windowid=None):
        self.target = pykey.get_window(windowid)
        print 'target set to', self.target

app = Application()

filename = sys.argv[1] if len(sys.argv)==2 else None
app.fileHandler(filename=filename)
app.targetHandler(windowid=None)

app.mainloop()
