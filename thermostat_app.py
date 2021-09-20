import tkinter as tk
from tkinter import BooleanVar, DoubleVar, StringVar, font
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import random

class Thermostat(tk.Tk):
    PADX = 20
    PADY = 5
    CANVASPAD = 30
    MSINTERVAL = 1000
    PLOTVALS = 20
    SETPOINT_START = 70

    def __init__(self):
        super().__init__()

        self.title('Thermostat')
        # self.geometry('300x200')

        self._createGui()
        # self.start()

    def _createGui(self):
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)

        controlFrame = tk.Frame(self)
        controlFrame.configure(borderwidth=2, relief='sunken')
        controlFrame.grid(row=0, column=0, rowspan=2, columnspan=1, sticky='NSEW')

        labelFont = font.Font(family='Helvetica', size=16, weight='bold')
        numberFont = font.Font(family='Helvetica', size=40)

        self.auto = BooleanVar()
        autoCheck = tk.Checkbutton(controlFrame, text='AUTO', variable=self.auto,
            onvalue=True, offvalue=False, command=self._autoChanged)
        autoCheck.configure(font=labelFont)
        autoCheck.grid(row=0, column=0, padx=self.PADX, pady=self.PADY)

        self.state = BooleanVar()
        stateCheck = tk.Checkbutton(controlFrame, text='STATE', variable=self.state,
            onvalue=True, offvalue=False, command=self._stateChanged)
        stateCheck.configure(font=labelFont)
        stateCheck.grid(row=1, column=0, padx=self.PADX, pady=self.PADY)

        setpointLabel = tk.Label(controlFrame, text='SETPOINT:')
        setpointLabel.configure(font=labelFont)
        setpointLabel.grid(row=2, column=0, padx=self.PADX, pady=self.PADY)

        self.strSetpoint = StringVar()
        self.strSetpoint.set(str(round(self.SETPOINT_START, 1)))
        vcmd = (self.register(self._validateFloat), '%P')
        setpointEntry = tk.Spinbox(controlFrame, textvariable=self.strSetpoint,
            from_=0.0, to=99.9, increment=0.1, validate='all', validatecommand=vcmd)
        setpointEntry.configure(font=numberFont, width=4, justify='center', borderwidth=1, relief='solid')
        setpointEntry.grid(row=3, column=0, padx=self.PADX, pady=self.PADY)

        self.setpointHistory = []

        valueLabel = tk.Label(controlFrame, text='VALUE:')
        valueLabel.configure(font=labelFont)
        valueLabel.grid(row=4, column=0, padx=self.PADX, pady=self.PADY)
        
        self.strValue = StringVar()
        self.strValue.set(self.strSetpoint.get())
        valueReadout = tk.Spinbox(controlFrame, textvariable=self.strValue, state='disabled')
        valueReadout.configure(font=numberFont, width=4, justify='center', borderwidth=1, relief='solid', disabledforeground='black')
        valueReadout.grid(row=5, column=0, padx=self.PADX, pady=self.PADY)

        self.valueHistory = []

        self.timeStamps = []

        self.fig = Figure(figsize = (5, 5), dpi = 100)
        self.plt = self.fig.add_subplot(111)

        self.plt.plot(self.timeStamps, self.setpointHistory)
        self.plt.plot(self.timeStamps, self.valueHistory)

        # self.plt.set_ylabel('Temperature')
        # self.plt.set_xlabel('Elapsed Time (s)')

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.flush_events()

        self.canvas.get_tk_widget().grid(row=0, rowspan=5, column=1, columnspan=3,
            padx=self.CANVASPAD, pady=self.CANVASPAD, sticky='NSEW')

    def _validateFloat(self, newValue):
        try:
            float(newValue)
            return True
        except ValueError:
            return False

    def _autoChanged(self):
        pass

    def _stateChanged(self):
        self.auto = False

    def _setpointChanged(self):
        pass

    def sample(self):
        setpoint = float(self.strSetpoint.get())
        value = setpoint + random.normalvariate(0, 1) # would sample temp here
        self.strValue.set(str(round(value, 1)))

        self.setpointHistory.append(setpoint)
        self.valueHistory.append(value)

        self.timeStamps.append(len(self.setpointHistory))

        self.plt.clear()
        self.plt.plot(self.timeStamps[-self.PLOTVALS:], self.setpointHistory[-self.PLOTVALS:])
        self.plt.plot(self.timeStamps[-self.PLOTVALS:], self.valueHistory[-self.PLOTVALS:])

        self.canvas.draw()
        self.canvas.flush_events()

    def start(self):
        self.samplingActive = True
        self.sampleRepeatedly()

    def sampleRepeatedly(self):
        if self.samplingActive:
            self.sample()
            self.after(self.MSINTERVAL, self.sampleRepeatedly)

    def stop(self):
        self.samplingActive = False



t = Thermostat()

if __name__ == "__main__":
    t.start()
    t.mainloop()