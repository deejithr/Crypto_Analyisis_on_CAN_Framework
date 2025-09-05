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
from tkinter import font
from tkinter import ttk
from ttkbootstrap.scrolled import ScrolledText
import ttkbootstrap as tb
from CAN_Simulation.simulate import *
from ttkbootstrap.tableview import Tableview
from ttkbootstrap.constants import *



################################################################################
# Macros
################################################################################
#Enum for simulation start/stop
STARTED = 0
STOPPED = 1

# Description information for each cipher
cipherdescription = {
    "None" : [
        ["None\n", "heading"],
        ["No Cipher selected\n", "default"],
        ["Raw data Transmitted\n", "default"]
    ],

    "RC4" : [
        ["RC4\n", "heading"],
        ["RC4 stream cipher\n\n", "default"],
        ["Data is encrypted using RC4 Stream cipher", "default"]
    ],

    "Speck" : [
        ["Speck\n", "heading"],
        ["To be implemented\n\n", "default"],
        ["Raw data Transmitted", "default"]
    ],

    "TEA" : [
        ["TEA\n", "heading"],
        ["Tiny Encryption Algorithm\n", "default"],
        ["To be implemented\n\n", "default"],
        ["Raw data Transmitted", "default"]
    ],

    "CMAC" : [
        ["CMAC\n", "heading"],
        ["To be implemented\n\n", "default"],
        ["Raw data Transmitted", "default"]
    ],

    "HMAC" : [
        ["HMAC\n", "heading"],
        ["To be implemented\n\n", "default"],
        ["Raw data Transmitted", "default"]
    ],
}



################################################################################
# Classes
################################################################################
class CANSimGUI(tb.Window):
    '''Represents the UI'''
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
        self.algodescptext = self.cipherdescpareainit(self.algodescptext)
        self.insertdescription("None")
        self.algodescptext.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        # Tab for Performance Measurements
        perf_tab = tb.Frame(notebook)
        notebook.add(perf_tab, text="Performance")

        perf_label = tb.Label(perf_tab, text="Performance Metrics", bootstyle="info", anchor = "w")
        perf_label.pack(fill=tk.X, padx=10, pady=20)

        coldata = [
        {"text": "Algorithm", "stretch": False},
        "enc_Mean (us)",
        "enc_p95 (us)",
        "dec_Mean (us)",
        "dec_p95 (us)",
        "cpu_cycles/byte",
        ]

        self.dt = Tableview(
        master=perf_tab,
        coldata=coldata,
        paginated=True,
        bootstyle="info",
        stripecolor=(super().style.colors.light, None)
        )
        self.dt.pack(fill=BOTH, expand=YES, padx=10, pady=10)
        self.inserttotableview("No data available")

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

    def do_start_stop_simulation(self):
        '''Function called on pressing the Start/Stop button'''
        #If simulation is already started
        if (self.simulation == STARTED):
            #Set the state to STOPPED
            self.simulation = STOPPED
            self.start_stop_btn.config(text="▶ Start Simulation", bootstyle="success")
            #Call the stop simulation callback 
            self.stopsimcallback()
            self.inserttotableview(None)
        #If simulation is Stopped
        elif(self.simulation == STOPPED):
            #Set the state to STARTED
            self.simulation = STARTED
            self.start_stop_btn.config(text="■ Stop Simulation", bootstyle="danger")
            self.inserttotableview("Simulation in Progress")
            #Call the start simulation callback
            self.startsimcallback()

    def printtosenderconsole(self, msg):
        '''Function to print into the Sender Console text box'''
        self.sender_console_text.insert(tk.END, msg + "\n")
        self.sender_console_text.see(tk.END)

    def printtoreceiverconsole(self, msg):
        '''Function to print into the Receiver Console text box'''
        self.recv_console_text.insert(tk.END, msg + "\n")
        self.recv_console_text.see(tk.END)

    def clearconsole(self):
        '''Function clears the console for both Sender and Receiver'''
        self.sender_console_text.delete("1.0", "end")
        self.recv_console_text.delete("1.0", "end")

    def cipherdescpareainit(self, text_area):
        '''To initialize the font properties for the ScrolledText Area'''
        # Define the fonts
        default_font = font.nametofont("TkDefaultFont")
        heading_font = font.Font(font=default_font)
        heading_font.configure(weight="bold",size=20)
        bold_font = font.Font(font=default_font)
        bold_font.configure(weight="bold")

        text_area.tag_configure("bold", font=bold_font)
        text_area.tag_configure("heading", font=heading_font)

        return text_area
    
    def insertdescription(self,selected):
        '''Insert description for each Cipher'''
        self.algodescptext.text.configure(state="normal")
        # Clear the area first
        self.algodescptext.delete("1.0", "end")
        #Print the description
        for eachline in cipherdescription[selected]:
            if(eachline[1] != "default"):
                self.algodescptext.insert(tb.END, eachline[0], eachline[1])
            else:
                self.algodescptext.insert(tb.END, eachline[0])
        self.algodescptext.text.configure(state="disabled")

    def inserttotableview(self, text):
        '''Add contents to the Perfomance Metrics Table view'''
        # Clear the contents first
        self.dt.delete_rows()

        # If metrics is null, then print only the text
        # This is done when no data is available or the simulation is running
        if (None != text):
            self.dt.insert_row(values=(text, " ", " ", " ", " ", " "))
        # If metrics data available,
        else:
            #Get the performance metrics for both encryption and decryption
            en_perfmetrics = getperfmetrics("encryption_samples")
            de_perfmetrics = getperfmetrics("decryption_samples")
            
            for eachAlgo in ["None", "RC4", "Speck", "TEA", "CMAC", "HMAC" ]:
                # Only if the sample data is present
                if(eachAlgo in en_perfmetrics.keys()):
                    row = []
                    row.append(eachAlgo)
                    row.append(en_perfmetrics[eachAlgo]["mean_ns"])
                    row.append(en_perfmetrics[eachAlgo]["p95"])
                    row.append(de_perfmetrics[eachAlgo]["mean_ns"])
                    row.append(de_perfmetrics[eachAlgo]["p95"])
                    row.append(de_perfmetrics[eachAlgo]["cycles/byte"])
                    # Append row to the table view
                    self.dt.insert_row(values=row) 

        




################################################################################
# Functions
################################################################################