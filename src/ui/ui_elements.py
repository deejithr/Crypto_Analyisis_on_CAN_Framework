"""
This module define the UI and its elements.

It includes :
    * Classes for UI
    * Functions to be triggered based in the interaction in the bus

"""
################################################################################
# Imports
################################################################################
import os, sys
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
import ttkbootstrap as tb
from CAN_Simulation.simulate import *

################################################################################
# Macros
################################################################################
#Enum for simulation start/stop
STARTED = 0
STOPPED = 1

################################################################################
# Classes
################################################################################
class CANSimGUI(tb.Window):
    def __init__(self):
        self.startsimcallback = None
        self.stopsimcallback = None
        super().__init__(title="CryptoAnalysis for CAN", themename="cosmo")
        self.geometry("1024x768")

        # Start and Stop simulation
        button_frame = tb.Frame(self)
        button_frame.pack(fill="x", pady=10)
        self.start_stop_btn = tb.Button(button_frame, text="▶ Start Simulation",
                                   bootstyle="success", command=self.do_start_stop_simulation)
        self.start_stop_btn.pack(side="left", padx=10)
        
        # Create a tabbed view
        notebook = ttk.Notebook(self, width=500, height=200, bootstyle="secondary")
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Tab for selecting Crypto Algorithm
        cryalgo_tab = tb.Frame(notebook)
        notebook.add(cryalgo_tab, text="Crypto Algorithms")

        cryalgo_label = tb.Label(cryalgo_tab, text="Select Cryptographic Algorithm:", 
                                 bootstyle="info", justify="left")
        cryalgo_label.pack(pady=10)

        # Radio button for selecting the algorithm
        self.selected_algo = tk.StringVar(value="RC4")
        for algo in ["RC4", "Speck", "TEA", "CMAC", "HMAC" ]:
            rb_cryalgo_tab = tb.Radiobutton(cryalgo_tab, text=algo, variable=self.selected_algo, 
                                            value=algo, bootstyle="info")
            rb_cryalgo_tab.pack(anchor="w", padx=20)

        # Tab for Performance Measurements
        perf_tab = tb.Frame(notebook)
        notebook.add(perf_tab, text="Performance")

        perf_label = tb.Label(perf_tab, text="Performance Metrics", bootstyle="info", justify="left")
        perf_label.pack(pady=10)

        # Tab 3: Algorithm Comparison
        compare_tab = tb.Frame(notebook)
        notebook.add(compare_tab, text="Comparison")

        #Console for Printing the logs
        console_frame = tb.Frame(self)
        console_frame.pack(fill="x", pady=10)
        self.perf_text = scrolledtext.ScrolledText(console_frame, height=15)
        self.perf_text.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        # Set simulation state to STOPPED, initially
        self.simulation = STOPPED

    # Function called on pressing the Start/Stop button
    def do_start_stop_simulation(self):
        #If simulation is already started
        if (self.simulation == STARTED):
            #Set the state to STOPPED
            self.simulation = STOPPED
            self.start_stop_btn.config(text="▶ Start Simulation", bootstyle="success")
            #Call the start simulation callback 
            self.stopsimcallback()
        #If simulation is Stopped
        elif(self.simulation == STOPPED):
            #Set the state to STARTED
            self.simulation = STARTED
            self.start_stop_btn.config(text="■ Stop Simulation", bootstyle="danger")
            #Call the stop simulation callback
            self.startsimcallback()

    # Function for printing into the text box
    def printtotextbox(self, msg):
        self.perf_text.insert(tk.END, msg + "\n")
        self.perf_text.see(tk.END)


################################################################################
# Functions
################################################################################