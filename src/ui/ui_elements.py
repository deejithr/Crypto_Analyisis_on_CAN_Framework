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
import matplotlib.pyplot as plt
import json



################################################################################
# Macros
################################################################################
#Enum for simulation start/stop
STARTED = 1
STOPPED = 0

# Periodicity to print messages in the console
CONSOLE_LOGGING_PERIOD = 200

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

    "SPECK" : [
        ["SPECK", "heading"],
        ["\nSPECK 64/128 is a lightweight block cipher ", "default"],
        ["\n  -  designed by the U.S. National Security Agency (NSA) for software implementations on resource-constrained devices, specifically IOT devices.", "default"],
        ["\n  -  \"64/128\" in its name indicates that it uses a 64-bit block size and a 128-bit key size.", "default"],
        ["\n\nSPECK 64/128 is an ARX cipher, which means its round function uses only three operations:", "default"],
        ["\n  - Addition: Modular addition", "default"],
        ["\n  - Rotation: Circular shifts (or rotations) of a fixed number of bits", "default"],
        ["\n  - XOR: Bitwise exclusive OR", "default"],
        ["\n\nInitial state:", "bold"],
        ["\nThe 64-bit plaintext block is split into two 32-bit words, typically x and y.The 128-bit master key is used to generate a sequence of round keys. For SPECK 64/128, this process uses 27 rounds", "default"],
        ["\n\nRound function:", "bold"],
        ["\nIn each round, the two data words are updated using the following steps:", "default"],
        ["\n  - Rotation and addition: ", "bold"],
        ["\n    The x word is rotated right by 8 bits, then added to the y word modulo 2^32.", "default"],
        ["\n  - XOR with round key: ", "bold"],
        ["\n    The result is XORed with the current round key.", "default"],
        ["\n  - Rotation and XOR: ", "bold"],
        ["\n    The y word is rotated left by 3 bits, then XORed with the new x word.", "default"],
        ["\n  - Update words: ", "bold"],
        ["\n    The newly computed values become the inputs for the next round", "default"],
        ["\n\nDecryption:", "bold"],
        ["\nThe decryption process is a simple reversal of the encryption steps. ", "default"],
        ["\nBy performing the inverse of each operation the plaintext can be recovered.", "default"]
    ],

    "xTEA" : [
        ["xTEA\n", "heading"],
        ["Tiny Encryption Algorithm\n", "default"],
        ["To be implemented\n\n", "default"],
        ["Raw data Transmitted", "default"]
    ],

    "PRESENT" : [
        ["PRESENT\n", "heading"],
        ["The PRESENT algorithm is an ultra-lightweight block cipher designed for resource-constrained devices, such as radio-frequency identification (RFID) tags and sensor networks. The algorithm uses a Substitution-Permutation Network (SPN) structure, and its low-complexity design makes it highly efficient for hardware implementation.\n", "default"],
        ["\nBlock size: ", "bold"],
        ["64 bits.\n", "default"],
        ["Key size: ", "bold"],
        ["80 bits (PRESENT-80)\n", "default"],
        ["Rounds: ", "bold"],
        ["31 rounds, plus a final key addition.\n", "default"],
        ["Structure: ", "bold"],
        ["SPN, with each round comprising three layers.\n", "default"],
        ["\nEncryption process\n", "bold"],
        ["The encryption of a 64-bit plaintext block involves 31 identical rounds, each with three main operations, plus a final key addition.\n", "default"],
        ["\nRound 1 through 31\n", "bold"],
        ["Each of these rounds consists of the following steps:\n", "default"],
        ["AddRoundKey: The current 64-bit state is bitwise XORed with a unique 64-bit round key K_i derived from the master key.\n", "default"],
        ["SBoxLayer (Substitution): The 64-bit state is split into 16 separate 4-bit \"nibbles.\" Each nibble is passed through the same 4x4 S-box (substitution box), which provides the non-linear \"confusion\" aspect of the cipher.pLayer (Permutation): All 64 bits of the state are rearranged according to a specific permutation table. This operation provides \"diffusion\" by mixing the bits across the state.\n", "default"],
        ["\nRound 32\n", "bold"],
        ["After the 31st round, a final AddRoundKey operation is performed. The resulting state is XORed with the 32nd round key K_32 to produce the final 64-bit ciphertext.\n", "default"],
        ["\nKey schedule\n", "bold"],
        ["PRESENT uses an algorithm to generate 32 round keys from the initial master key. The key schedule is as follows\n", "default"],
        ["\nFor PRESENT-80\n", "bold"],
        ["Initial state: The 80-bit master key is loaded into a key register.Round key generation: For each round, the leftmost 64 bits of the key register become the round key K_i.Key register update: The key register is updated for the next round by performing the following operations:Rotate the register 61 bits to the left.Apply the 4x4 S-box to the four leftmost bits of the register.XOR five specific bits of the register with the round counter.\n", "default"],
        ["\nDecryption is the inverse of encryption, applying the operations in reverse order. Inverse operations include XOR for AddRoundKey, the inverse permutation P^-1 for pLayer, and the inverse S-box S^-1 for SBoxLayer.\n", "default"],
    ],

    "AES128" : [
        ["AES128\n", "heading"],
        ["To be implemented\n\n", "default"],
        ["Raw data Transmitted", "default"]
    ],
}

# Description for Encryption Scheme
encryptionschemedescription = {

}

# Algorithms that can be selected for Nonce Creation
nonce_creation_gen_algo =[
    "SPECK",
    "PRESENT",
    "RC4",
    "xTEA",
    "AES",
]

# Algorithms that can be selected for KeyStream Gen
keystream_gen_algo =[
    "PRESENT",
    "SPECK",
    "xTEA",
    "RC4",
    "AES",
]

# Algorithms that can be selected for MAC Creation
mac_gen_algo =[
    "AES128",
    "HMAC"
]


################################################################################
# Globals
################################################################################
# For saving the Performance Metrics to plot
en_perfmetrics = {}
de_perfmetrics = {}
# For saving the deadline miss ratio
deadlinemiss = {}

#Multiprocessing Queues
ui_senderqueue = None
ui_receiverqueue = None

# Shared Variables
deadlinemisscounts = None
sentmessagescount = None
simulationstate = None

#Shared variables for collecting the encrypt and decrypt time samples
manager = None
encrypt_samples = None
decrypt_samples = None
encrypt_cpuper = None
decrypt_cpuper = None

# For benchmarking
benchmark_deadlinemiss = {}
benchmarkthread = None

################################################################################
# Classes
################################################################################
class CANSimGUI(tb.Window):
    '''Represents the UI'''
    def __init__(self):
        global encrypt_samples, decrypt_samples, encrypt_cpuper , decrypt_cpuper
        global manager 

        self.startsimcallback = None
        self.stopsimcallback = None
        super().__init__(title="CryptoAnalysis for CAN", themename="simplex")
        self.geometry("1200x768")

        #----------------------------------- UI Initialization --------------------------------#
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
                                 bootstyle="info", font=("Arial", 12, "bold"))
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
                                 bootstyle="info", font=("Arial", 12, "bold"))
        cryalgo_label.pack(side="top", padx=10, pady=10)

        # Radio button for selecting the algorithm
        self.selected_algo = tk.StringVar(value="None")
        self.rb_cryalgo_tab = []
        index = 0
        for algo in ENCRYPTION_ALGORITHMS:
            # Omit radio button for Encryption Scheme
            if("ENCRYPTION_SCHEME" != algo):
                self.rb_cryalgo_tab.append(tb.Radiobutton(cryalgo_frame, text=algo, variable=self.selected_algo, 
                                                value=algo, bootstyle="info"))
                self.rb_cryalgo_tab[index].pack(side="top", anchor="w", padx=20, pady=5)
                index = index + 1

        cryalgo_descp_frame = tb.Frame(cryalgo_mainframe)
        cryalgo_descp_frame.pack(fill="both",padx=10, pady=20)
        self.algodescptext = ScrolledText(cryalgo_descp_frame, height=15, bootstyle="secondary", wrap=tk.WORD)
        self.algodescptext = self.descrpareainit(self.algodescptext)
        self.insertdescription("None")
        self.algodescptext.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        # Tab for Performance Measurements
        perf_tab = tb.Frame(notebook)
        notebook.add(perf_tab, text="Performance")

        perf_tab_subframe1 = tb.Frame(perf_tab)
        perf_tab_subframe1.pack(side="top", padx=10, fill=tk.X)

        perf_label = tb.Label(perf_tab_subframe1, text="Performance Metrics", bootstyle="info", anchor = "w", font=("Arial", 14, "bold"))
        perf_label.pack(side="left",anchor=tk.NW, padx=10, pady=10)

        perf_tab_subframe2 = tb.Frame(perf_tab_subframe1)
        perf_tab_subframe2.pack(anchor=tk.SE, side="left", expand=True)

        self.perf_benchmarkbtn = tb.Button(perf_tab_subframe2, text="Run Benchmark",
                                   bootstyle="danger", command=self.do_benchmark)
        self.perf_benchmarkbtn.pack(side="left", padx=10, pady=10)
        self.perf_comparebtn = tb.Button(perf_tab_subframe2, text="Compare",
                                   bootstyle="danger", command=self.do_comparison)
        self.perf_comparebtn.pack(side="left", padx=10, pady=10)

        coldata = [
        {"text": "Algorithm", "stretch": True},
        {"text":"enc_Mean (us)", "stretch": True},
        {"text":"enc_p95 (us)", "stretch": True},
        {"text":"dec_Mean (us)", "stretch": True},
        {"text":"dec_p95 (us)", "stretch": True},
        {"text": "enc cycles/byte", "stretch": True},
        {"text": "dec cycles/byte", "stretch": True},
        {"text": "enc cpu %", "stretch": True},
        {"text": "dec cpu %", "stretch": True},
        {"text": "deadline miss ratio %", "stretch": True}
        ]

        self.dt = Tableview(
        master=perf_tab,
        coldata=coldata,
        paginated=True,
        bootstyle="info",
        autofit=True,
        autoalign=True,
        stripecolor=(super().style.colors.light, None)
        )
        self.dt.pack(fill=BOTH, expand=YES, padx=10, pady=10)
        self.inserttotableview("No data available")

        # Tab 3: Encryption Scheme
        # Combobox variables
        self.nonce_creation_option = tk.StringVar()
        self.keystream_gen_option = tk.StringVar()
        self.mac_gen_option = tk.StringVar()
        # For encryption enabled/disabled state, initial state is false
        self.encscheme_state = tk.BooleanVar(value=False)

        encryption_scheme_tab = tb.Frame(notebook)
        notebook.add(encryption_scheme_tab, text="Encryption Scheme")

        # For encryption scheme enable/disable
        es_onoff_frame = tb.Frame(encryption_scheme_tab)
        es_onoff_frame.pack(side="top", padx=10, fill=tk.X)
        es_onoff_labell1 = tb.Label(es_onoff_frame, text="Encryption Scheme", 
                                 bootstyle="info", font=("Arial", 14, "bold"))
        es_onoff_labell1.pack(side="left", padx=10, pady=5)
        es_onoff_button1 = tb.Checkbutton(es_onoff_frame, bootstyle="success-round-toggle", 
                                          variable=self.encscheme_state, 
                                          command=self.toggleencschemestate)
        es_onoff_button1.pack(side="left", padx=10, pady=5)

        encryption_scheme_masterframe1 = tb.Frame(encryption_scheme_tab)
        encryption_scheme_masterframe1.pack(side="left", fill=tk.X)
        
        # For Encryption Scheme Configuration 
        encryption_scheme_subframe1 = tb.Frame(encryption_scheme_masterframe1, borderwidth=1, relief="raised")
        encryption_scheme_subframe1.pack(side="left", padx=10, fill=tk.X)

        encryption_scheme_label1 = tb.Label(encryption_scheme_subframe1, text="Select Algorithms:", 
                                 bootstyle="info", font=("Arial", 12, "bold"))
        encryption_scheme_label1.pack(padx=10, pady=5)
        
        encschemeconf_childframe2 = tb.Frame(encryption_scheme_subframe1)
        encschemeconf_childframe2.pack(fill=tk.X)
        encschemeconf_label2 = tb.Label(encschemeconf_childframe2, text=("Nonce Derivation").ljust(16), 
                                 bootstyle="info")
        encschemeconf_label2.pack(side="left", padx=10, pady=5)
        self.encschemeconf_combobox1 = tb.Combobox(encschemeconf_childframe2, 
                                                   textvariable=self.nonce_creation_option, 
                                                   bootstyle="danger", 
                                                   values=nonce_creation_gen_algo)
        self.encschemeconf_combobox1.pack(side="left", padx=10, pady=5)
        self.nonce_creation_option.set(nonce_creation_gen_algo[0])
        

        encschemeconf_childframe3 = tb.Frame(encryption_scheme_subframe1)
        encschemeconf_childframe3.pack(side="top", fill=tk.X)
        encschemeconf_label3 = tb.Label(encschemeconf_childframe3, text=("Keystream Gen").ljust(16), 
                                 bootstyle="info")
        encschemeconf_label3.pack(side="left", padx=10, pady=5)
        self.encschemeconf_combobox2 = tb.Combobox(encschemeconf_childframe3, 
                                                   textvariable=self.keystream_gen_option, 
                                                   bootstyle="danger", 
                                                   values=keystream_gen_algo)
        self.encschemeconf_combobox2.pack(side="left", padx=10, pady=5)
        self.keystream_gen_option.set(keystream_gen_algo[0])
        

        encschemeconf_childframe4 = tb.Frame(encryption_scheme_subframe1)
        encschemeconf_childframe4.pack(side="top", fill=tk.X)
        encschemeconf_label4 = tb.Label(encschemeconf_childframe4, text=("MAC Generation").ljust(16), 
                                 bootstyle="info")
        encschemeconf_label4.pack(side="left", padx=10, pady=5)
        self.encschemeconf_combobox3 = tb.Combobox(encschemeconf_childframe4, 
                                                   textvariable=self.mac_gen_option, 
                                                   bootstyle="danger", values=mac_gen_algo)
        self.encschemeconf_combobox3.pack(side="left", padx=10, pady=5)
        self.mac_gen_option.set(mac_gen_algo[0])

        self.encschemeupdatebtn = tb.Button(encryption_scheme_subframe1, text="Update",
                                   bootstyle="info", command=self.do_encschemeupdate)
        self.encschemeupdatebtn.pack(anchor=tk.SE, padx=10, pady=5)

        # For Encryption Scheme Counters 
        encryption_scheme_subframe2 = tb.Frame(encryption_scheme_masterframe1)
        encryption_scheme_subframe2.pack(side="left", padx=10, fill=tk.X)

        encschemeconf_childframe5 = tb.Frame(encryption_scheme_subframe2)
        encschemeconf_childframe5.pack(side="left", padx=10, fill=tk.X)
        self.sendercounter_entry = tb.Entry(encschemeconf_childframe5,width=10)
        self.sendercounter_entry.pack(side="top", padx=10, pady=10)
        sendercounter_label = tb.Label(encschemeconf_childframe5, text="Sender Counter", 
                                 bootstyle="info")
        sendercounter_label.pack(side="top", padx=10, pady=10)

        encschemeconf_childframe6 = tb.Frame(encryption_scheme_subframe2)
        encschemeconf_childframe6.pack(side="left", padx=10, fill=tk.X)
        self.receivercounter_entry = tb.Entry(encschemeconf_childframe6,width=10)
        self.receivercounter_entry.pack(side="top", padx=10, pady=10)
        receivercounter_label = tb.Label(encschemeconf_childframe6, text="Receiver Counter", 
                                 bootstyle="info")
        receivercounter_label.pack(side="top", padx=10, pady=10)

        # For Encription Scheme Description
        encryption_scheme_subframe3 = tb.Frame(encryption_scheme_masterframe1)
        encryption_scheme_subframe3.pack(fill="both", padx=10)
        self.encryptionschemedescp_entry = ScrolledText(encryption_scheme_subframe3, height=15, bootstyle="secondary", wrap=tk.WORD)
        # Initialize font properties for the encryption scheme description area
        self.encryptionschemedescp_entry = self.descrpareainit(self.encryptionschemedescp_entry)
        self.encryptionschemedescp_entry.pack(side="top", padx=10, pady=10, fill=BOTH)

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
        self.recv_console_text.tag_config("green_bold", foreground="green", font=("Arial", 10, "bold"))
        self.recv_console_text.tag_config("red_bold", foreground="red", font=("Arial", 10, "bold"))

        # Call to initialize or de-init Encryption Scheme
        self.toggleencschemestate()

        # Tab 4: Replay Attack Simulation
        replayattacksim_tab = tb.Frame(notebook)
        notebook.add(replayattacksim_tab, text="Replay Attack Simulation")
        
        #------------------------------------------------------------------------------------------#

        # Set simulation state to STOPPED, initially
        self.simulation = STOPPED

        #Initialize the Shared variables to capture the performance metrics
        manager = Manager()
        encrypt_samples = manager.dict()
        decrypt_samples = manager.dict()
        encrypt_cpuper = manager.dict()
        decrypt_cpuper = manager.dict()
        
        #Initialize the samples array in the performance Metrics array for each algorithm
        for algo in ENCRYPTION_ALGORITHMS:
            encrypt_samples[algo] = []
            decrypt_samples[algo] = []
            encrypt_cpuper[algo] = []
            decrypt_cpuper[algo] = []

    def do_start_stop_simulation(self):
        '''Function called on pressing the Start/Stop button'''
        global ui_receiverqueue, ui_senderqueue
        global deadlinemisscounts, sentmessagescount
        global simulationstate
        global encrypt_samples, encrypt_cpuper
        global decrypt_samples, decrypt_cpuper

        #If simulation is already started
        if (self.simulation == STARTED):
            #Set the state to STOPPED
            self.simulation = STOPPED
            self.start_stop_btn.config(text="▶ Start Simulation", bootstyle="success")
            #Call the stop simulation callback 
            self.stopsimcallback(simulationstate)
            self.inserttotableview(None)
        
        #If simulation is Stopped
        elif(self.simulation == STOPPED):
            #Create a multiprocessing queue for sender and receiver
            ui_senderqueue = multiprocessing.Queue()
            ui_receiverqueue = multiprocessing.Queue()

            # Shared variables
            # Simulation State. Simulation will stop, once the state becomes False
            simulationstate = Value('i', False)
            # DeadlineMissCounts. Number of times the deadline was missed
            deadlinemisscounts = Value('i', False)
            # Total Number of Sent Messages
            sentmessagescount = Value('i', False)

            #Set the state to STARTED
            self.simulation = STARTED
            self.start_stop_btn.config(text="■ Stop Simulation", bootstyle="danger")
            self.inserttotableview("Simulation in Progress")
            #Call the start simulation callback
            self.startsimcallback(ui_senderqueue, ui_receiverqueue, simulationstate, 
                                  deadlinemisscounts, sentmessagescount,
                                  encrypt_samples, encrypt_cpuper,
                                  decrypt_samples, decrypt_cpuper,
                                  self.encscheme_state
                                  )

    def printtosenderconsole(self):
        '''Function to print into the Sender Console text box'''
        global ui_senderqueue

        if(None != ui_senderqueue):
            #Print until the queue is empty
            while not ui_senderqueue.empty():
                msg = ui_senderqueue.get()
                self.sender_console_text.insert(tk.END, "\n" + msg )
                self.sender_console_text.see(tk.END)
        # schedule next check
        self.after(CONSOLE_LOGGING_PERIOD, self.printtosenderconsole)  

    def printtoreceiverconsole(self):
        '''Function to print into the Receiver Console text box'''
        global ui_receiverqueue

        if (None != ui_receiverqueue):
            #Print until the queue is empty
            while not ui_receiverqueue.empty():
                msg = ui_receiverqueue.get()
                # self.recv_console_text.insert(tk.END, )
                if (msg.__contains__("  ✅")):
                    self.recv_console_text.insert(tk.END, "\n" + msg, "green_bold")
                else:
                    self.recv_console_text.insert(tk.END, "\n" + msg, "red_bold")
                self.recv_console_text.see(tk.END)
        # schedule next check
        self.after(CONSOLE_LOGGING_PERIOD, self.printtoreceiverconsole)  

    def clearconsole(self):
        '''Function clears the console for both Sender and Receiver'''
        self.sender_console_text.delete("1.0", "end")
        self.recv_console_text.delete("1.0", "end")

    def descrpareainit(self, text_area):
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
        global en_perfmetrics, de_perfmetrics, deadlinemiss
        # Clear the contents first
        self.dt.delete_rows()

        # If metrics is null, then print only the text
        # This is done when no data is available or the simulation is running
        if (None != text):
            self.dt.insert_row(values=(text, " ", " ", " ", " ", " "))
        # If metrics data available,
        else:
            #Get the performance metrics for both encryption and decryption
            en_perfmetrics = self.getperfmetrics("encryption_samples")
            de_perfmetrics = self.getperfmetrics("decryption_samples")
            deadlinemiss[self.selected_algo.get()] = '%.3f'%self.getdeadlinemissratio()
           
            for eachAlgo in ENCRYPTION_ALGORITHMS:
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
                    row.append(en_perfmetrics[eachAlgo]["cpu_percent"])
                    row.append(de_perfmetrics[eachAlgo]["cpu_percent"])
                    row.append(deadlinemiss[eachAlgo])
                    # Append row to the table view
                    self.dt.insert_row(values=row) 
    
    def getdeadlinemissratio(self):
        '''Function to get the deadline miss ratio'''
        global deadlinemisscounts, sentmessagescount
        return (100 * (deadlinemisscounts.value)/sentmessagescount.value)

    def do_comparison(self):
        ''' Prepares chart for data comparison '''
        # Plot Encryption Performance Metrics
        self.plot_bar()
    
    def do_benchmark(self):
        global sentmessagescount
        # This is to indicate the results are from benchmarking
        self.benchmarkresults = True

        for eachalgo in ENCRYPTION_ALGORITHMS:
            # All algorithms except ENCRYPTION_SCHEME
            if ("ENCRYPTION_SCHEME" != eachalgo):
                # Set the encryption algorithm to the selected one
                setencryptionalgo(eachalgo)
                self.selected_algo.set(eachalgo)
                for eachperiod in BENCHMARKPERIOD:
                    #Set the periodicity
                    self.canconf_entry3.set(eachperiod)
                    setmsgperiodicity(eachperiod)

                    # Start the simulation
                    self.do_start_stop_simulation()
                    # Run the process for 200 frames
                    while(200 > sentmessagescount.value):
                        pass
                    # Stop the simulation
                    self.do_start_stop_simulation()
        # Compare the results
        self.do_comparison()

    def plot_bar(self):
        global en_perfmetrics, de_perfmetrics, deadlinemiss
        # X-axis positions
        x = np.arange(len(en_perfmetrics.keys()))
        width = 0.20  # bar width
        fig1, (ax1, ax2) = plt.subplots(1,2, figsize=(12, 6))
  

        # For Performance Measurements Bar Plot
        title1 = "Performance Measurements - Time"
        enc_mean_ns = list(float(en_perfmetrics[eachalgo]["mean_ns"]) for eachalgo in en_perfmetrics.keys())
        enc_p95 = list(float(en_perfmetrics[eachalgo]["p95"]) for eachalgo in en_perfmetrics.keys())
        dec_mean_ns = list(float(de_perfmetrics[eachalgo]["mean_ns"]) for eachalgo in en_perfmetrics.keys())
        dec_p95 = list(float(de_perfmetrics[eachalgo]["p95"]) for eachalgo in en_perfmetrics.keys())

        ax1_bars1 = ax1.bar(x - width, enc_mean_ns, width, label="enc Mean")
        ax1_bars2 = ax1.bar(x, enc_p95, width, label="enc p95")
        ax1_bars3 = ax1.bar(x + width, dec_mean_ns, width, label="dec Mean")
        ax1_bars4 = ax1.bar(x + 2*width, dec_p95, width, label="dec p95")
        
        ax1.set_ylabel("Time in us")
        ax1.set_title(title1)
        ax1.set_xticks(x)
        ax1.set_xticklabels(en_perfmetrics.keys())
        ax1.legend(loc='upper left') 
        ax1.grid(axis="y", linestyle="--", alpha=0.7)

        ax1.bar_label(ax1_bars1, rotation=90, padding=5)
        ax1.bar_label(ax1_bars2, rotation=90, padding=5)
        ax1.bar_label(ax1_bars3, rotation=90, padding=5)
        ax1.bar_label(ax1_bars4, rotation=90, padding=5)

        # For Cycles per Bytes Bar Plot
        title2 = "Cycles per byte"
        enc_cyclesperb = list(float(en_perfmetrics[eachalgo]["cycles/byte"]) for eachalgo in en_perfmetrics.keys())
        dec_cyclesperb = list(float(de_perfmetrics[eachalgo]["cycles/byte"]) for eachalgo in en_perfmetrics.keys())

        ax2_bars1 = ax2.bar(x - width, enc_cyclesperb, width, label="enc cycles/bytes")
        ax2_bars2 = ax2.bar(x, dec_cyclesperb, width, label="dec cycles/bytes")

        ax2.set_ylabel("cycles/byte")
        ax2.set_title(title2)
        ax2.set_xticks(x)
        ax2.set_xticklabels(en_perfmetrics.keys())
        ax2.legend(loc='upper left', ncols=2) 
        ax2.grid(axis="y", linestyle="--", alpha=0.7)

        ax2.bar_label(ax2_bars1, rotation=90, padding=5)
        ax2.bar_label(ax2_bars2, rotation=90, padding=5)
     
        fig2, (ax3, ax4) = plt.subplots(1,2, figsize=(12, 6))
        # For CPU Percent
        title3 = f"CPU Percentage "
        enc_cpupercent = list(float(en_perfmetrics[eachalgo]["cpu_percent"]) for eachalgo in en_perfmetrics.keys())
        dec_cpupercent = list(float(de_perfmetrics[eachalgo]["cpu_percent"]) for eachalgo in en_perfmetrics.keys())

        ax3_bars1 = ax3.bar(x - width, enc_cpupercent, width, label="enc cpu percentage")
        ax3_bars2 = ax3.bar(x, dec_cpupercent, width, label="dec cpu percentage")

        ax3.set_ylabel("CPU Percent")
        ax3.set_title(title3)
        ax3.set_xticks(x)
        ax3.set_xticklabels(en_perfmetrics.keys())
        ax3.legend(loc='upper left', ncols=2) 
        ax3.grid(axis="y", linestyle="--", alpha=0.7)

        ax3.bar_label(ax3_bars1, rotation=90, padding=5)
        ax3.bar_label(ax3_bars2, rotation=90, padding=5)
        
        # For Deadline miss counts
        title4 = f"Deadline Miss counts at {self.canconf_entry3.get()}ms periodicity"
        deadlinemisses = list(float(deadlinemiss[eachalgo]) for eachalgo in deadlinemiss.keys())

        ax4_bars1 = ax4.bar(x, deadlinemisses, width, label="Deadline Miss counts")

        ax4.set_ylabel("counts")
        ax4.set_title(title4)
        ax4.set_xticks(x)
        ax4.set_xticklabels(deadlinemiss.keys())
        ax4.legend(loc='upper left') 
        ax4.grid(axis="y", linestyle="--", alpha=0.7)

        ax4.bar_label(ax4_bars1, rotation=90, padding=5)

        plt.tight_layout()
        plt.show()

    def do_canmsgupdate(self):
        ''' Updates the CAN message based on new configuration '''
        canid = int(self.canconf_entry1.get(),16)
        data = [int(h,16) for h in self.canconf_entry2.get().split(",")]
        periodicity = int(self.canconf_entry3.get())

        # Input validation logic to be added

        # Set the CAN message and periodicity
        setcanmessage(canid, data, True)
        setmsgperiodicity(periodicity)

    def do_encschemeupdate(self):
        ''' Updates the encryption scheme based on new configuration '''
        # Check if the encyrption scheme is enabled
        initializeencryptionscheme(self.nonce_creation_option.get(),
                                   self.keystream_gen_option.get(),
                                   self.mac_gen_option.get(),
                                   int(self.canconf_entry1.get(),16))
        
    def toggleencschemestate(self):
        '''Callback triggered on changing encryption scheme state'''
        # Check if the encyrption scheme is enabled
        if(True == self.encscheme_state.get()):
            # Initialize the objects for encryption scheme
            initializeencryptionscheme(self.nonce_creation_option.get(),
                                   self.keystream_gen_option.get(),
                                   self.mac_gen_option.get(),
                                   int(self.canconf_entry1.get(),16))
        else: # Encryption scheme disabled
            #Deinitialize the objects
            deinitencryptionscheme()

    def resetsamples(self, algorithm):
        '''Function to reset the samples for encryption and decryption'''
        global decrypt_samples, encrypt_cpuper
        global encrypt_samples, decrypt_cpuper

        # Reset the encryption and decryption samples
        encrypt_samples[algorithm] = []
        decrypt_samples[algorithm] = []
        # Reset the cpu percentage samples
        encrypt_cpuper[algorithm] = []
        decrypt_cpuper[algorithm] = []

    def getperfmetrics(self, sampletype):
        '''Called after simulation stopped to get the Performance metrics for each algorithm'''
        global encrypt_samples, decrypt_samples
        global encrypt_cpuper, decrypt_cpuper

        perfmetrics = {}
        # Select the array depending on the metrics needed
        if ("encryption_samples" == sampletype):
            samplearray = encrypt_samples
            cpuperarray = encrypt_cpuper
        elif ("decryption_samples" == sampletype):
            samplearray = decrypt_samples
            cpuperarray = decrypt_cpuper

        # Reset the mean cpu percentage variable
        mean_cpuper = {}
        # For cpu percentage samples
        for eachalgo, cpuper in cpuperarray.items():
            mean_cpuper[eachalgo] = 0
            #Only if valid samples are available
            if(len(cpuper) > 0):
                cpuper = np.array(cpuper)
                # Calculate the median
                mean_cpuper[eachalgo] = np.mean(cpuper)

        # For encryption and decryption times
        for eachalgo, samples in samplearray.items():
            #Only if valid samples are available
            if(len(samples) > 0):
                samples = np.array(samples)
                mean_ns = statistics.fmean(samples)
                p95 = np.percentile(samples, 95)
                p99 = np.percentile(samples, 99)
                jitter_ns = statistics.pstdev(samples)
                cyclesperbyte = (mean_ns * CPU_FREQ_MHZ / 1000)/8

                # Add data to the Metrics dictionary
                perfmetrics[eachalgo] = {
                    "mean_ns" : '%.3f'%(mean_ns),
                    "p95" : '%.3f'%(p95),
                    "p99" : '%.3f'%(p99),
                    "jitter_ns" : '%.3f'%(jitter_ns),
                    "cycles/byte" : '%.3f'%(cyclesperbyte),
                    "cpu_percent" : '%.3f'%(mean_cpuper[eachalgo])
                }
        return perfmetrics

################################################################################
# Functions
################################################################################