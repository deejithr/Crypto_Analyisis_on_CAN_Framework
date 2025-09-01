"""
This module defines the UI and its elements.

It includes :
    * Classes for UI
    * Functions to be triggered based on the interaction in the UI

"""
################################################################################
# Imports
################################################################################
import os, sys
import tkinter as tk
from tkinter import ttk
from ttkbootstrap.scrolled import ScrolledText
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
# Represents the UI 
class CANSimGUI(tb.Window):
    def __init__(self):
        self.startsimcallback = None
        self.stopsimcallback = None
        super().__init__(title="CryptoAnalysis for CAN", themename="simplex")
        self.geometry("1200x768")

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

        cryalgo_frame = tb.Frame(cryalgo_tab)
        cryalgo_frame.pack(side="left", padx=10, pady=20, anchor=tk.NW)
        cryalgo_label = tb.Label(cryalgo_frame, text="Select Cryptographic Algorithm:", 
                                 bootstyle="info")
        cryalgo_label.pack(side="top", padx=10, pady=20)

        # Radio button for selecting the algorithm
        self.selected_algo = tk.StringVar(value="None")
        self.rb_cryalgo_tab = []
        index = 0
        for algo in ["None", "RC4", "Speck", "TEA", "CMAC", "HMAC" ]:
            self.rb_cryalgo_tab.append(tb.Radiobutton(cryalgo_frame, text=algo, variable=self.selected_algo, 
                                            value=algo, bootstyle="info"))
            self.rb_cryalgo_tab[index].pack(side="top", anchor="w", padx=20, pady=5)
            index = index + 1
        

        cryalgo_descp_frame = tb.Frame(cryalgo_tab)
        cryalgo_descp_frame.pack(fill="both",padx=10, pady=20)
        self.algodescptext = ScrolledText(cryalgo_descp_frame, height=15, bootstyle="secondary")
        self.algodescptext.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        # Tab for Performance Measurements
        perf_tab = tb.Frame(notebook)
        notebook.add(perf_tab, text="Performance")

        perf_label = tb.Label(perf_tab, text="Performance Metrics", bootstyle="info", anchor = "w")
        perf_label.pack(fill=tk.X, padx=10, pady=20)

        # Tab 3: Algorithm Comparison
        compare_tab = tb.Frame(notebook)
        notebook.add(compare_tab, text="Comparison")

        #Console for Printing the logs
        console_frame = tb.Frame(self)
        console_frame.pack(fill=tk.X, side="top", pady=10)
        console_label = tb.Label(console_frame, text="Console", bootstyle="info", anchor = "w")
        console_label.pack(side="left", padx=10, pady=20, anchor=tk.NW)
        self.clearlog = tb.Button(console_frame, text="Clear Log",
                                   bootstyle="dark", command=self.clearconsole)
        self.clearlog.pack(side="left", padx=10)
        
        # Create a tabbed view inside the Console
        notebook_console = ttk.Notebook(self, width=500, height=200, bootstyle="secondary")
        notebook_console.pack(fill="both", expand=True, padx=10, pady=10)
        
        #For Sender
        sender_tab = tb.Frame(notebook_console)
        notebook_console.add(sender_tab, text="Sender")
        self.sender_console_text = ScrolledText(sender_tab, height=15, bootstyle="secondary")
        self.sender_console_text.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        #For Receiver
        receiver_tab = tb.Frame(notebook_console)
        notebook_console.add(receiver_tab, text="Receiver")
        self.recv_console_text = ScrolledText(receiver_tab, height=15, bootstyle="secondary")
        self.recv_console_text.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        # Set simulation state to STOPPED, initially
        self.simulation = STOPPED

    # Function called on pressing the Start/Stop button
    def do_start_stop_simulation(self):
        #If simulation is already started
        if (self.simulation == STARTED):
            #Set the state to STOPPED
            self.simulation = STOPPED
            self.start_stop_btn.config(text="▶ Start Simulation", bootstyle="success")
            #Call the stop simulation callback 
            self.stopsimcallback()
        #If simulation is Stopped
        elif(self.simulation == STOPPED):
            #Set the state to STARTED
            self.simulation = STARTED
            self.start_stop_btn.config(text="■ Stop Simulation", bootstyle="danger")
            #Call the start simulation callback
            self.startsimcallback()

    # Function to print into the Sender Console text box
    def printtosenderconsole(self, msg):
        self.sender_console_text.insert(tk.END, msg + "\n")
        self.sender_console_text.see(tk.END)

    # Function to print into the Receiver Console text box
    def printtoreceiverconsole(self, msg):
        self.recv_console_text.insert(tk.END, msg + "\n")
        self.recv_console_text.see(tk.END)

    def clearconsole(self):
        self.sender_console_text.delete("1.0", "end")
        self.recv_console_text.delete("1.0", "end")




################################################################################
# Functions
################################################################################