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
from tkinter import constants
from ttkbootstrap.scrolled import ScrolledText
import ttkbootstrap as tb
from CAN_Simulation.simulate import *
from ttkbootstrap.tableview import Tableview
from ttkbootstrap.constants import *
from tkinter import Toplevel, Label, Button
import matplotlib.pyplot as plt
import json
import threading



################################################################################
# Macros
################################################################################
#Enum for simulation start/stop
STARTED = 1
STOPPED = 0

#Enums for Benchmark States
BENCHMARK_INIT = 0
BENCHMARK_START_SIM = 1
BENCHMARK_WAIT_FOR_COMPLETION = 2
BENCHMARK_STOP_SIM = 3
BENCHMARK_DEINIT = 4


#Enums for Replay Attack Simulation
REPLAYSIM_INIT = 0
REPLAYSIM_RECORD_FRAMES = 1
REPLAYSIM_WAIT_FOR_RECORD_COMPLETION = 2
REPLAYSIM_REPLAY_FRAMES = 3
REPLAYSIM_WAIT_FOR_REPLAY_COMPLETION = 4
REPLAYSIM_DEINIT = 5

# Periodicity to print messages in the console
CONSOLE_LOGGING_PERIOD = 335

# Counter Update Period for Encryption Mechanism
COUNTER_UPDATE_PERIOD = 100


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
        ["XTEA\n", "heading"],
        ["\nThe XTEA (eXtended Tiny encryption Algorithm) algorithm is a Feistel cipher that uses a 64-bit block size and a 128-bit key. It is an upgradation over the original TEA (Tiny Encryption Algorithm) to correct the key scheduling weakness related to the TEA Algorithm. The algorithm typically uses 32 rounds.\n", "default"],
        ["\nIt uses a Feistel structure, meaning in each round, half of the data block is used to modify the other half, and then the halves are swapped. But in the XTEA variation, the halves are modified sequentially rather than swapped. The following are the operations associated with xTEA algorithms \n", "default"],
        ["\nBlock Split: \n", "bold"],
        ["\nThe 64 bit input block is first divided into two 32-bit unsigned integers denoted as v0 and v1 \n", "default"],
        ["\nKey Scheduling: \n", "bold"],
        ["\nXTEA uses a more complex key schedule that uses an integer constant called delta (0x9E3779B9, derived from the golden ratio) to generate subkeys dynamically within the round function. The 128-bit master key is split into four 32-bit words denoted as K[0] to K[3] \n", "default"],
        ["\nRound Function: \n", "bold"],
        ["\nEach round involves a mixing function that applies a combination of bitwise shifts, XOR, and modulo 232 additions/subtractions to the data halves. The key scheduling uses a running sum variable, incremented by delta in each cycle, to select different subkeys from the main key array for different rounds. \n", "default"],
        ["\nIteration: \n", "bold"],
        ["\nThese operations are repeated for a set number of rounds to ensure the ciphertext is sufficiently mixed and secure. \n", "default"],
        ["\nThe decryption process performs the reverse operation of the encryption by executing these steps in the reverse order, and using subtraction in place of addition. \n", "default"],
        ["\nThe TEA algorithm was found to be vulnerable to key related attacks, where the attacker could exploit the key biases to compromise the ciphertext. The key schedule was redesigned to use all of the 4 words of the 32 bit key along with the delta coefficient. XTEA has thus enhanced the security of TEA while ensuring the lightweight characteristics of TEA was maintained \n", "default"]
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
        ["AES128\n\n", "heading"],
        ["Advanced Encryption Standard or AES falls under symmetric block cipher category with a block size of 128 bits and can support Key sizes in the range 128, 192 or 256 bits. It is one of the traditional algorithms used in automotive industry. \n", "default"],
        ["\nThe encryption process involves an initial key addition followed by multiple rounds, each containing four transformations - \n", "default"],
        ["\n• Substitution of bytes (S-Box substitution) \n", "bold"],
        ["• Shift Rows \n", "bold"],
        ["• Mixing Columns (Matrix Multiplication) \n", "bold"],
        ["• Round key addition\n", "bold"],
        ["\nThe number of rounds needed depends on the keysize. In this dissertation, the keysize is taken as 128 bits and hence the rounds required is 10. Here, the plaintext length required for AES is 128bit. As CAN data length is of 64bits, in this dissertation, for the comparison of cryptographic algorithms, AES is treated like a stream cipher, by using AES-128 in CTR mode. Different modes are supported by AES like Electronic Codebook(ECB), Cipher Block Chaining (CBC), Galois/Counter mode (GCM), Counter (CTR) and then Cipher Feedback (CFB)/Output Feedback mode (OFB). The Counter mode (CTR) creates a stream cipher by encrypting a counter value, which is then XOR-ed with the plain text. \n", "default"],
        ["\nSteps involved in AES Encryption are: \n", "default"],
        ["\n• Initial Round Key addition: \n", "bold"],
        ["The 128 bit plaintext is combined with the first round-key derived using the add round key transformation \n", "default"],
        ["\n• Subsequent rounds: \n", "bold"],
        ["The data block then goes through a series of repetitive rounds, where each round includes the 4 transformations mentioned above. \n", "default"],
        ["\n• Final round: \n", "bold"],
        ["The final round includes all transformations, except mix columns. \n", "default"],
        ["\nIn this dissertation, for the performance analysis of cryptographic algorithms. the AES-128 encryption algorithm is run in counter mode (CTR) and is used to generate the key stream with the above mentioned steps. The key stream thus generated is then XOR-ed with the plain text to produce the ciphertext. In later phase of this dissertation, when implementing the Encryption Scheme, AES will be used to generate the MAC, which shall be appended along with the encrypted data in the CAN frame. \n", "default"],
        ["\nAES is an open and globally accepted standard. It is highly secure and resistant to brute force attacks, especially if longer key sizes are used. It is regarded to be computationally efficient with high speed performance in hardware. In AUTOSAR SecOc, AES is one of the recommended algorithms for calculating the MAC of the payload in the Protocol Data Unit (PDU). The algorithm supports different block and key sizes, which makes it possible to be used or adapted to various security needs. Implementing AES in software can be complex and requires significant processing. For a single block, the time complexity of AES encryption algorithm is regarded as O(1), whereas when it is used in multiple blocks or in a particular mode of operation, it is time complexity is regarded as O(n), as it scales linearly with n, the number of blocks. \n", "default"]
    ],
}

# Description for Encryption Scheme
encryptionschemedescription = [
["Encryption Scheme\n", "heading"],
["\nThe Encryption Scheme aims at authentication and replay protection for CAN communication.Along with the encrypted payload, a truncated MAC shall be sent to ensure authenticity of the sender. An incrementing counter shall be maintained at both sender and receiver side for each individual CAN ID. The counter shall be a 16-bit or 24-bit counter and is not transmitted in payload and is used as an input for data encryption and MAC generation. \n", "default"],
["\nThe sender increments this counter on successful transmission of CAN frame and the receiver increments the counter on successful reception. On reception of a CAN frame, the receiver increments its counter and then performs decryption and MAC verification using that value. An attempt at decryption and MAC verification with an increment of 2 to the counter shall be performed if the counter increment of 1 doesn’t satisfy verification. If verification still fails, then the frame will be dropped. On successful verification, the counter shall be made as the value for which the verification passed. \n", "default"],
["\n\nNonce Creation: N = encrypt (K1, (CAN_ID || counter))", "default"],
["\n\nKeystream: S = encrypt (K2, N)", "default"],
["\n\nPayload Data encryption: C = P xor S", "default"],
["\n\nMAC generation: MAC[0:2] = CMAC(K3, (CAN_ID || counter || C))", "default"]
]

replayattackdescription =[
["Replay Attack Simulation\n", "heading"],
["\nIntention of replay attack simulation is to ensure that, with the encryption mechanism implemented, the receiver is able to detect replayed frames and discard them. If only the encryption of payload data is done, it is not possible for the receiver to identify if the frame that has been received is a replayed frame or not. With the encryption scheme described above, a counter is maintained at both sender side and receiver side. The sender increments the counter whenever there is a successful transmission of message and the receiver increments the counter whenever it accepts a message. Whenever the receiver receives a message, it tries to perform MAC verification, by using the stored counter +1 value. If the MAC calculated at the receiver side with this counter value does not match the truncated MAC available in the CAN frame, the receiver will discard the message.\n", "default"],  
["\nReplay attacks will be modelled by intentionally re-sending previously transmitted encrypted frames. On starting the replay simulation, the sender will first normally send the frames with the current counter value and incrementing it each time a message is send. These sent frames shall be captured and saved to a file. \n", "default"],
["\nThe receiver will accept the frames as the MAC verification will be successful as the counter values are in sync with the sender. After certain number of frames are sent, the simulation shall be stopped. The captured frames will then be loaded back from the file and the sender will send these messages as such, without any changes. Now, the receiver on performing MAC verification of these replayed frames, will discard the frames as the verification fails. Since the implicit counter value in the replayed frames are old, they will never pass the MAC verification. In the UI, the discarded frames can be seen in the Receiver console marked in red with a cross mark next to them. With this, demonstration of the resistance to replay attack is successful \n", "default"]
]


# Algorithms that can be selected for Nonce Creation
nonce_creation_gen_algo =[
    "SPECK",
    "xTEA",
]

# Algorithms that can be selected for KeyStream Gen
keystream_gen_algo =[
    "xTEA",
    "SPECK",
]

# Algorithms that can be selected for MAC Creation
mac_gen_algo =[
    "AES128-CMAC",
    "SHA256-HMAC"
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
ready_event = None

# For benchmarking
benchmark_deadlinemiss = {}
benchmarkthread = None
bm_algo = None
bm_period = None

# For encrytpion scheme counter display
counterthread = None

#For replay attack simulation
replayattacksimthread = None

################################################################################
# Classes
################################################################################
class CANSimGUI(tb.Window):
    '''Represents the UI'''
    def __init__(self):
        global encrypt_samples, decrypt_samples, encrypt_cpuper , decrypt_cpuper, ready_event
        global manager 

        #----------------------------------- Callbacks for simulation------------------------------#
        self.startsimcallback = None
        self.stopsimcallback = None

        #--------------------------------------- For Benchmark ------------------------------------#
        self.deadlinemissbenchmark = {}
        # To hold the state of StateMachine
        self.benchmarkstate = BENCHMARK_INIT
        # Index for Algorithms and periodicity, during benchmarking process
        self.benchmarkalgoidx = 0
        self.benchmarkperiodidx = 0
        # Indicates benchmark is in progress
        self.benchmarkinprogress = False
        self.benchmarkresults = False
        # For Progressbar increments during benchmark results
        self.step = 0

        #----------------------------------- For Replay Simulation --------------------------------#
        self.replaysim_state = Value('i', REPLAYSIM_INIT)

        super().__init__(title="CryptoAnalysis for CAN", themename="simplex")
        self.geometry("1200x768")

        #------------------------------------- UI Initialization ----------------------------------#
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
        self.selected_algo = tk.StringVar(value="RC4")
        self.rb_cryalgo_tab = []
        index = 0
        for algo in ENCRYPTION_ALGORITHMS:
            self.rb_cryalgo_tab.append(tb.Radiobutton(cryalgo_frame, text=algo, variable=self.selected_algo, 
                                            value=algo, bootstyle="info"))
            self.rb_cryalgo_tab[index].pack(side="top", anchor="w", padx=20, pady=5)
            index = index + 1
        # To set the encryption algorithm as RC4, initially
        setencryptionalgo("RC4")

        cryalgo_descp_frame = tb.Frame(cryalgo_mainframe)
        cryalgo_descp_frame.pack(fill="both",padx=10, pady=20)
        self.algodescptext = ScrolledText(cryalgo_descp_frame, height=15, bootstyle="secondary", wrap=tk.WORD)
        self.algodescptext = self.descrpareainit(self.algodescptext)
        self.insertdescription(self.algodescptext, cipherdescription["RC4"])
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

        self.perf_benchmarkbtn = tb.Button(perf_tab_subframe2, text="▶ Run Benchmark",
                                   bootstyle="success", command=self.do_benchmark)
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
        self.replaysim_start = tk.BooleanVar(value=False)

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
        self.insertdescription(self.encryptionschemedescp_entry, encryptionschemedescription)
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

        # For replay attack enable/disable
        replay_onoff_frame = tb.Frame(replayattacksim_tab)
        replay_onoff_frame.pack(side="top", padx=10, fill=tk.X)
        self.replaysimbtn = tb.Button(replay_onoff_frame, text="▶ Simulate Replay Attack",
                                   bootstyle="success", command=self.do_replayattacksim)
        self.replaysimbtn.pack(side="left", padx=10, pady=5)


        replaysim_masterframe1 = tb.Frame(replayattacksim_tab)
        replaysim_masterframe1.pack(side="left", fill=tk.X)

        # Displaying replay attack simulation status 
        replaysim_subframe1 = tb.Frame(replaysim_masterframe1, borderwidth=1, relief="raised")
        replaysim_subframe1.pack(side="left", padx=10, fill=tk.Y, expand=True)

        self.replaysim_entry1 = ScrolledText(replaysim_subframe1, height=15, width=60, bootstyle="secondary", wrap=tk.WORD)
        self.replaysim_entry1.pack(padx=10, pady=5, expand=True, fill=tk.Y)

        # For Replay Attack Simulation
        replaysim_subframe3 = tb.Frame(replaysim_masterframe1)
        replaysim_subframe3.pack(fill="both", padx=10)
        self.replaysim_descrpentry = ScrolledText(replaysim_subframe3, height=15, bootstyle="secondary", wrap=tk.WORD)
        # Initialize font properties for the encryption scheme description area
        self.replaysim_descrpentry = self.descrpareainit(self.replaysim_descrpentry)
        self.insertdescription(self.replaysim_descrpentry, replayattackdescription)
        self.replaysim_descrpentry.pack(side="top", padx=10, pady=10, fill=BOTH)
        
        #------------------------------------------------------------------------------------------#

        # Set simulation state to STOPPED, initially
        self.simulation = STOPPED

        #Initialize the Shared variables to capture the performance metrics
        manager = Manager()
        encrypt_samples = manager.dict()
        decrypt_samples = manager.dict()
        encrypt_cpuper = manager.dict()
        decrypt_cpuper = manager.dict()
        ready_event = multiprocessing.Event()
        
        #Initialize the samples array in the performance Metrics array for each algorithm
        for algo in (ENCRYPTION_ALGORITHMS + ["ENCRYPTION_SCHEME"]):
            encrypt_samples[algo] = []
            decrypt_samples[algo] = []
            encrypt_cpuper[algo] = []
            decrypt_cpuper[algo] = []

    def getcipherdescription(self, algo):
        return cipherdescription[algo]
    
    def do_start_stop_simulation(self):
        '''Function called on pressing the Start/Stop button'''
        global ui_receiverqueue, ui_senderqueue
        global deadlinemisscounts, sentmessagescount
        global simulationstate
        global encrypt_samples, encrypt_cpuper
        global decrypt_samples, decrypt_cpuper
        global counterthread

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
            
            # Only if the encrypton scheme is enabled, start tasks for counter update
            if(True == self.encscheme_state.get()):
                # To display the status of benchmark process
                counterthread = threading.Thread(target = self.update_counters, args = ())
                counterthread.start()
            #Call the start simulation callback
            self.startsimcallback(ui_senderqueue, ui_receiverqueue, simulationstate, 
                                  deadlinemisscounts, sentmessagescount,
                                  encrypt_samples, encrypt_cpuper,
                                  decrypt_samples, decrypt_cpuper,
                                  self.encscheme_state,
                                  self.benchmarkinprogress,
                                  ready_event,
                                  self.replaysim_state
                                  )

    def printtosenderconsole(self):
        '''Function to print into the Sender Console text box'''
        global ui_senderqueue

        if(STARTED == self.simulation):
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

        if(STARTED == self.simulation):
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
    
    def insertdescription(self, entry, text):
        '''Insert description for each Cipher'''
        entry.text.configure(state="normal")
        # Clear the area first
        entry.delete("1.0", "end")
        #Print the description
        for eachline in text:
            if(eachline[1] != "default"):
                entry.insert(tb.END, eachline[0], eachline[1])
            else:
                entry.insert(tb.END, eachline[0])
        entry.text.configure(state="disabled")

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

    def update_label(self, label, pbar):
        # Progres value 
        progress_value = (self.step / (len(ENCRYPTION_ALGORITHMS) * len(BENCHMARKPERIOD))) * 100
        pbar.config(value=progress_value)

        #If benchmark completed
        if(100 == progress_value):
            labeltext = "BenchMark completed !!"
        else:
            labeltext=f"Running benchmark for {ENCRYPTION_ALGORITHMS[self.benchmarkalgoidx]} at {BENCHMARKPERIOD[self.benchmarkperiodidx]}ms periodicity"

        # Update the label's text
        label.config(text=labeltext)
    
        # Schedule this function to be called again after 3000 milliseconds (3 seconds)
        label.after(3000, self.update_label, label, pbar)

    def update_counters(self):
        global simulationstate

        # Clear the counter entries first
        self.sendercounter_entry.delete(0, END)
        self.receivercounter_entry.delete(0, END)
        #Update with the current values of sender and receiver counters
        scounter = getsendercounter()
        rcounter = getreceivercounter()
        self.sendercounter_entry.insert(0, str(scounter))
        self.receivercounter_entry.insert(0, str(rcounter))
        
        if(True == simulationstate.value):
            # Schedule this function to be called again after COUNTER_UPDATE_PERIOD milliseconds
            self.after(COUNTER_UPDATE_PERIOD, self.update_counters)
    
    def display_popup(self):
        pid = os.getpid()
        p = psutil.Process(pid)
        p.cpu_affinity([3])

        top = Toplevel()
        top.title("Benchmark Progress")
        top.geometry("500x200") # Set desired size

        label = ttk.Label(top, text=f"Running benchmark for {ENCRYPTION_ALGORITHMS[self.benchmarkalgoidx]} at {BENCHMARKPERIOD[self.benchmarkperiodidx]}ms periodicity", bootstyle="info")
        label.pack(pady=20)

        pbar = ttk.Progressbar(
            top,
            bootstyle="info",
            maximum=100,
            value=0,
            length=300
        )
        pbar.pack(padx=10, pady=10)

        # Start the periodic update function
        self.update_label(label, pbar)

    def do_replayattacksim(self):
        global sentmessagescount
        
        #Run StateMachine
        if(REPLAYSIM_INIT == self.replaysim_state.value):
            pid = os.getpid()
            p = psutil.Process(pid)
            p.cpu_affinity([3])

            # Display the replay simulation information
            self.replaysimbtn.config(text="■ Replay Sim Running", bootstyle="danger")
            self.replaysim_entry1.delete("1.0", "end")
            self.replaysim_entry1.insert(tb.END, "Replay attack simulation started...\n")

            # Set the encryption state first
            self.encscheme_state.set(True)
            # Initialize the objects for encryption scheme
            initializeencryptionscheme(self.nonce_creation_option.get(),
                                   self.keystream_gen_option.get(),
                                   self.mac_gen_option.get(),
                                   int(self.canconf_entry1.get(),16))
            # switch to the next state
            self.replaysim_state.value = REPLAYSIM_RECORD_FRAMES

        elif (REPLAYSIM_RECORD_FRAMES == self.replaysim_state.value):
            # Start the simulation
            self.do_start_stop_simulation()
            self.replaysim_entry1.insert(tb.END, "Recording CAN frames...\n")
            #Change to next State
            self.replaysim_state.value = REPLAYSIM_WAIT_FOR_RECORD_COMPLETION
        
        elif (REPLAYSIM_WAIT_FOR_RECORD_COMPLETION == self.replaysim_state.value):
            if(sentmessagescount.value >= REPLAY_MESSAGE_COUNT):
                # Stop the simulation
                self.do_start_stop_simulation()
                self.replaysim_entry1.insert(tb.END, "Recording Stopped...\n")
                time.sleep(1)
                #Change to next State
                self.replaysim_state.value = REPLAYSIM_REPLAY_FRAMES

        elif (REPLAYSIM_REPLAY_FRAMES == self.replaysim_state.value):
            self.replaysim_entry1.insert(tb.END, "Start Replaying Frames...\n")
            #Change to next State
            self.replaysim_state.value = REPLAYSIM_WAIT_FOR_REPLAY_COMPLETION
            # Start the simulation
            self.do_start_stop_simulation()
        
        elif (REPLAYSIM_WAIT_FOR_REPLAY_COMPLETION == self.replaysim_state.value):
            if(sentmessagescount.value >= REPLAY_MESSAGE_COUNT):
                # Stop the simulation
                self.do_start_stop_simulation()
                self.replaysim_entry1.insert(tb.END, "Replay Stopped...\n")
                #Change to next State
                self.replaysim_state.value = REPLAYSIM_DEINIT
        
        elif (REPLAYSIM_DEINIT == self.replaysim_state.value):
            # Reset the state to REPLAYSIM_INIT
            self.replaysim_state.value = REPLAYSIM_INIT
            self.replaysimbtn.config(text="▶ Simulate Replay Attack", bootstyle="success")
        
        # Schedule the task every 1 second, only in states other than INIT
        if(REPLAYSIM_INIT != self.replaysim_state.value):
            self.after(1000, self.do_replayattacksim)


    def do_benchmark(self):
        global sentmessagescount, deadlinemiss, bm_algo, bm_period, benchmarkthread
        
        #Run StateMachine
        if(BENCHMARK_INIT == self.benchmarkstate):
            pid = os.getpid()
            p = psutil.Process(pid)
            p.cpu_affinity([3])
            #Setup the benchmark variables
            # This is to indicate the results are from benchmarking
            self.benchmarkresults = True
            self.step = 0
            self.perf_benchmarkbtn.config(text="■ Benchmark Running", bootstyle="danger")
            print("Benchmark started --- ")
            # To display the status of benchmark process
            benchmarkthread = threading.Thread(target = self.display_popup, args = ())
            benchmarkthread.start()

            # Set benchamrk state to true
            self.benchmarkinprogress = True
            # switch to the next state
            self.benchmarkstate = BENCHMARK_START_SIM

        elif (BENCHMARK_START_SIM == self.benchmarkstate):
            bm_algo = ENCRYPTION_ALGORITHMS[self.benchmarkalgoidx]
            bm_period =  BENCHMARKPERIOD[self.benchmarkperiodidx]
            # Set the encryption algorithm and the periodicity
            setencryptionalgo(bm_algo)
            self.selected_algo.set(bm_algo)
            # Create a dictionary only if key not present
            if(bm_algo not in self.deadlinemissbenchmark):
                self.deadlinemissbenchmark[bm_algo] = []

            #Set the periodicity, after clearing the current value
            self.canconf_entry3.delete(0, END)
            self.canconf_entry3.insert(0, str(bm_period))
            setmsgperiodicity(bm_period)
            # Start the simulation
            self.do_start_stop_simulation()
            # Increment the step 
            self.step += 1
            #Change to next State
            self.benchmarkstate = BENCHMARK_WAIT_FOR_COMPLETION
        
        elif (BENCHMARK_WAIT_FOR_COMPLETION == self.benchmarkstate):
            if(BENCHMARK_MESSAGE_COUNT <= sentmessagescount.value):
                #Change to next State
                self.benchmarkstate = BENCHMARK_STOP_SIM

        elif (BENCHMARK_STOP_SIM == self.benchmarkstate):
            # Stop the simulation
            self.do_start_stop_simulation()
            # Store the deadline misscounts for each periodicity
            self.deadlinemissbenchmark[bm_algo].append(deadlinemiss[bm_algo])
            #Check if all the periodicity tests have been covered for the current algorithm
            if(self.benchmarkperiodidx == len(BENCHMARKPERIOD) - 1):
                self.benchmarkperiodidx = 0
                #Check if benchmark has been done for all the algorithms
                if(self.benchmarkalgoidx == len(ENCRYPTION_ALGORITHMS) - 1):
                    self.benchmarkalgoidx = 0
                    #Set State to DEINIT
                    self.benchmarkstate = BENCHMARK_DEINIT
                else:
                    self.benchmarkalgoidx +=1
            else:
                self.benchmarkperiodidx +=1
            #Set State to BENCHMARK_START_SIM
            if(BENCHMARK_DEINIT != self.benchmarkstate):
                self.benchmarkstate = BENCHMARK_START_SIM
        
        elif (BENCHMARK_DEINIT == self.benchmarkstate):
            # Reset the state to BENCHMARK_INIT
            self.benchmarkstate = BENCHMARK_INIT
            # Set benchamrk state to False
            self.benchmarkinprogress = False
            
            # Compare the results
            self.do_comparison()
            benchmarkthread.join()
            self.perf_benchmarkbtn.config(text="▶ Run Benchmark", bootstyle="success")
            # Set periodicity back to 20ms
            #Set the periodicity, after clearing the current value
            self.canconf_entry3.delete(0, END)
            self.canconf_entry3.insert(0, "20")
            setmsgperiodicity(bm_period)
            print("Benchmark Completed !!! ")
        
        # Schedule the task every 1 second, only in states other than INIT
        if(BENCHMARK_INIT != self.benchmarkstate):
            self.after(1000, self.do_benchmark) 


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
        
        # Check if the resutlts are from benchmark results
        if(False == self.benchmarkresults):
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
        else: # Benchmark Results
            # For Deadline miss counts after benchmark results
            title4 = f"Deadline Miss ratio"
            ax4.set_title(title4)
            ax4.set_xlabel('Periodicity')
            ax4.set_ylabel('Deadline miss ratio')

            # Deadline miss ratio to be plotted
            x_unsorted = BENCHMARKPERIOD
            base_offset_y = 12  # Base vertical offset in points for annotations

            index = 0
            for each in ENCRYPTION_ALGORITHMS:
                #Convert y data to float list
                y_data_unsorted = list(float(val) for val in self.deadlinemissbenchmark[each])

                # Sort x and y data together
                # Sorts the data based on the periodicity
                data_points = sorted(list(zip(x_unsorted, y_data_unsorted)), key=lambda p: p[0])

                # Unpack the sorted data
                x_sorted, y_sorted = zip(*data_points)
                x_sorted = list(x_sorted)
                y_sorted = list(y_sorted)

                #Plot the data
                ax4.plot(
                    x_sorted, 
                    y_sorted, 
                    label=each, 
                    linestyle='-', 
                    marker='o', 
                    markersize=8
                )

                # Add Annotations with Overlap Prevention, depending on the offset direction and magnitude.
                # This prevents labels from different lines from overlapping.

                # Alternating vertical direction (1 or -1)
                stagger_direction = 1 if index % 2 == 0 else -1 

                # Calculate a slight horizontal offset proportional to the index
                final_offset_x = (index - (len(ENCRYPTION_ALGORITHMS) - 1) / 2) * 4

                # Final Vertical Offset: base_offset_y (e.g., 12 points) multiplied by direction
                final_offset_y = base_offset_y * stagger_direction

                for xi, yi in zip(x_sorted, y_sorted):
                    # Format the text to 3 decimal places
                    value_text = f'{yi:.3f}' 

                    ax4.annotate(
                        value_text,
                        (xi, yi),
                        textcoords="offset points",
                        xytext=(final_offset_x, final_offset_y), # Apply the staggered offset
                        ha='center', # Horizontal alignment: centered on the point
                        fontsize=8,
                        color=ax4.lines[-1].get_color() # Use the color of the current line
                    )
                index += 1

            ax4.legend(loc='upper right')
            # Reset the flag
            self.benchmarkresults = False

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
        setencryptionalgo("ENCRYPTION_SCHEME")
        
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