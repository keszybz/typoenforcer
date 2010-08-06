#!/usr/bin/python
# -*- coding:utf-8; -*-

import sys
import Tkinter as tk, tkFileDialog, tkFont
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
        self.quitButton.grid(column=0, row=0)

        self.fileButton = tk.Button(self, text='Load file',
                                    command=self.fileHandler)
        self.fileButton.grid(column=1, row=0)

        self.targetButton = tk.Button(self, text='Set target',
                                      command=self.targetHandler)
        self.targetButton.grid(column=2, row=0)

        self.ppfontButton = tk.Button(self, text='Bigger font',
                command=self.biggerfontHandler)
        self.ppfontButton.grid(column=3, row=0)

        self.ppfontButton = tk.Button(self, text='Smaller font',
                command=self.smallerfontHandler)
        self.ppfontButton.grid(column=4, row=0)

        self.textFont = tkFont.Font(size=15)

        self.theText = tk.Listbox(self, height=50, width=72,
                                  selectmode=tk.EXTENDED, font=self.textFont)
        self.theText.bind('<KeyPress-Return>', self.keyHandler)
        self.theText.focus_set()
        self.theText.grid(sticky='nesw', columnspan=5)

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

    def changeFont(self, increase):
        font_size = self.textFont.cget("size")
        font_size = font_size + 1 if increase else font_size - 1
        self.textFont.config(size=font_size)

    def biggerfontHandler(self):
        self.changeFont(True)

    def smallerfontHandler(self):
        self.changeFont(False)

app = Application()

filename = sys.argv[1] if len(sys.argv)==2 else None
app.fileHandler(filename=filename)
app.targetHandler(windowid=None)

app.mainloop()
