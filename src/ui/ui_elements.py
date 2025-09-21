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
        ["RC4 stream cipher is a symmetric cipher that generates a pseudorandom keystream \n", "default"],
        ["to encrypt data by XORing it with the plaintext\n\n", "default"],
        ["It involves a ", "default"], 
		["Key Scheduling Algorithm (KSA)", "bold"],
		[" to permute an internal state array based \n", "default"],
        ["on the secret key and a ", "default"],
		["Pseudo-Random Generation Algorithm (PRGA)\n", "bold"],
		["to produce the actual keystream.\n\n", "default"],
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

        # For CAN Message Configuration
        canconf_frame = tb.Frame(cryalgo_tab, borderwidth=1, relief="raised")
        canconf_frame.pack(side="left", padx=10, fill=tk.X)
        canconf_label1 = tb.Label(canconf_frame, text="CAN Message Configuration:", 
                                 bootstyle="info")
        canconf_label1.pack(padx=10, pady=10)
        
        canconf_subframe1 = tb.Frame(canconf_frame)
        canconf_subframe1.pack(padx=10, fill=tk.X)
        canconf_label2 = tb.Label(canconf_subframe1, text="CAN ID            ", 
                                 bootstyle="info")
        canconf_label2.pack(side="left", padx=10, pady=10)
        self.canconf_entry1 = tb.Entry(canconf_subframe1, width=40)
        self.canconf_entry1.pack(side="left", padx=10, pady=10)
        self.canconf_entry1.insert(0, "0xC0FFEE")

        canconf_subframe2 = tb.Frame(canconf_frame)
        canconf_subframe2.pack(side="top", padx=10, fill=tk.X)
        canconf_label3 = tb.Label(canconf_subframe2, text="Payload           ", 
                                 bootstyle="info")
        canconf_label3.pack(side="left", padx=10, pady=10)
        self.canconf_entry2 = tb.Entry(canconf_subframe2, width=40)
        self.canconf_entry2.pack(side="left", padx=10, pady=10)
        self.canconf_entry2.insert(0, "0xAA,0xBB,0xCC,0xDD,0XEE,0xFF,0x00,0x11")

        canconf_subframe3 = tb.Frame(canconf_frame)
        canconf_subframe3.pack(side="top", padx=10, fill=tk.X)
        canconf_label4 = tb.Label(canconf_subframe3, text="Periodicity(ms)", 
                                 bootstyle="info")
        canconf_label4.pack(side="left", padx=10, pady=10)
        self.canconf_entry3 = tb.Entry(canconf_subframe3,width=40)
        self.canconf_entry3.pack(side="left", padx=10, pady=10)
        self.canconf_entry3.insert(0, "20")

        self.canconfupdate_btn = tb.Button(canconf_frame, text="Update",
                                   bootstyle="info", command=self.do_canmsgupdate)
        self.canconfupdate_btn.pack(anchor=tk.SE, padx=10, pady=10)

        #Run updatecanmessagecallback once
        self.do_canmsgupdate()

        cryalgo_mainframe = tb.Frame(cryalgo_tab, borderwidth=1, relief="raised")
        cryalgo_mainframe.pack(side="left", padx=10, pady=10, anchor=tk.NW)
        cryalgo_frame = tb.Frame(cryalgo_mainframe)
        cryalgo_frame.pack(side="left", padx=10, pady=10, anchor=tk.NW)
        cryalgo_label = tb.Label(cryalgo_frame, text="Select Cryptographic Algorithm:", 
                                 bootstyle="info")
        cryalgo_label.pack(side="top", padx=10, pady=10)

        # Radio button for selecting the algorithm
        self.selected_algo = tk.StringVar(value="None")
        self.rb_cryalgo_tab = []
        index = 0
        for algo in ["None", "RC4", "Speck", "TEA", "CMAC", "HMAC" ]:
            self.rb_cryalgo_tab.append(tb.Radiobutton(cryalgo_frame, text=algo, variable=self.selected_algo, 
                                            value=algo, bootstyle="info"))
            self.rb_cryalgo_tab[index].pack(side="top", anchor="w", padx=20, pady=5)
            index = index + 1
        

        cryalgo_descp_frame = tb.Frame(cryalgo_mainframe)
        cryalgo_descp_frame.pack(fill="both",padx=10, pady=20)
        self.algodescptext = ScrolledText(cryalgo_descp_frame, height=15, bootstyle="secondary", wrap=tk.WORD)
        self.algodescptext = self.cipherdescpareainit(self.algodescptext)
        self.insertdescription("None")
        self.algodescptext.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        # Tab for Performance Measurements
        perf_tab = tb.Frame(notebook)
        notebook.add(perf_tab, text="Performance")

        perf_tab_subframe1 = tb.Frame(perf_tab)
        perf_tab_subframe1.pack(side="top", padx=10, fill=tk.X)

        perf_label = tb.Label(perf_tab_subframe1, text="Performance Metrics", bootstyle="info", anchor = "w")
        perf_label.pack(side="left",anchor=tk.NW, padx=10, pady=20)

        self.perf_comparebtn = tb.Button(perf_tab_subframe1, text="Compare",
                                   bootstyle="danger", command=self.do_comparison)
        self.perf_comparebtn.pack(anchor=tk.SE, padx=10, pady=10)

        coldata = [
        {"text": "Algorithm", "stretch": True},
        "enc_Mean (us)",
        "enc_p95 (us)",
        "dec_Mean (us)",
        "dec_p95 (us)",
        "enc cpu_cycles/byte",
        "dec cpu_cycles/byte",
        ]

        self.dt = Tableview(
        master=perf_tab,
        coldata=coldata,
        paginated=True,
        bootstyle="info",
        autofit=True,
        stripecolor=(super().style.colors.light, None)
        )
        self.dt.pack(fill=BOTH, expand=YES, padx=10, pady=10)
        self.inserttotableview("No data available")

        # Tab 3: Encryption Scheme
        compare_tab = tb.Frame(notebook)
        notebook.add(compare_tab, text="Encryption Scheme")

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
                    row.append(en_perfmetrics[eachAlgo]["cycles/byte"])
                    row.append(de_perfmetrics[eachAlgo]["cycles/byte"])
                    # Append row to the table view
                    self.dt.insert_row(values=row) 
    
    def do_comparison(self):
        ''' Prepares chart for data comparison '''
        pass

    def do_canmsgupdate(self):
        ''' Updates the CAN message based on new configuration '''
        canid = int(self.canconf_entry1.get(),16)
        data = [int(h,16) for h in self.canconf_entry2.get().split(",")]
        periodicity = int(self.canconf_entry3.get())

        # Input validation logic to be added

        # Set the CAn message and periodicity
        setcanmessage(canid, data, True)
        setmsgperiodicity(periodicity)


        




################################################################################
# Functions
################################################################################