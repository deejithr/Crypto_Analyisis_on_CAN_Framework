# Framework for Cryptographic Algorithm analysis on CAN protocol

This python framework aims at simulation and comparative study of different cryptographic mechanisms that can be used to improve the security of CAN Communication protocol. It aims at implementing selected cryptographic algorithms on CAN payload and then compare different attributes, such as computation time for encryption/decryption, payload overhead for accommodating the encrypted information, real time  feasibility to achieve communication timing requirements, to arrive at the best possible encryption algorithm that can be deployed to improve CAN security


# Description

The framework is a CAN simulation environment developed using **python-can**. It simulates two nodes - one as a Sender and other as a Receiver. The CAN interface used is **SocketCAN** provided by the LINUX framework. The sender sends a CAN message periodically to the bus and the receiver listens for messages. On selecting a particular encryption algorithm, the data shall be encrypted using the algorithm and sent on the bus. For Message Authentication Code (MAC) based encryption mechanisms, authentication tag shall sent along with data. The performance attributes of the algorithms shall me measured like - encryption times (mean, 95percentile), decryption times (mean, 95percentile), cpu-cycles per byte, deadline-miss counts, payload overhead (for adding encrypted information), cpu load etc

The following encryption algorithms are currently selected. (TBD)

 - RC4 (Stream Cipher)
	 - 256 byte state array
	 - fast and lightweight, suitable for CAN and low end ECUs
 - SPECK 32/64
	 - designed for IOT devices, hence suitable for CAN usecase
	 - faster and smaller than AES or SHA
 - Tiny Encryption Algorithm (TEA)
	 - fast on smaller MCUs
	 - included for benchmarking purposes
	 - maybe replaced with PRESENT algorithm
 - PRESENT
	 - Lightweight block cipher (substitution–permutation network)
	 - smaller code size and lower cpu consumption


Design of the framework is done in such a way that, new algorithms can be plugged in with little to no change in the framework


## Installation

The framework uses SocketCAN interface which is available only in the LINUX environment. Hence either debian based LINUX machines or Virtual machines running debian based distribution should be available. *Recommended:* Ubuntu 22.10 LTS

### Initial Setup (*tested in Ubuntu 22.10 LTS*)

    # Update system  
    sudo apt update && sudo apt upgrade -y
    # Install essential packages  
    sudo apt install -y build-essential git python3 python3-pip cmake pkg-config wget curl unzip
    #Install CAN utilities  
    sudo apt install -y can-utils
After setting up CAN, it can be tested using the below commands

    # CAN test  
    echo "Testing CAN setup..."  
    cansend vcan0 123#1122334455667788 &  
    sleep 1  
    candump -n 1 vcan0

### Installing python libraries
After the repo has been cloned, run the following command in the repo to install relevant python libraries

    pip install -r requirements.txt

## Usage
Before running the simulation, it must be ensured that the SocketCAN has been initialized. `Setup.sh` initializes the vcan0 interface. It is mandatory to run `Setup.sh` once before running the simulation for the first time.
Run the script `Run.sh` to initate the UI

## UI
Snapshots of the UI
<img width="1201" height="805" alt="UI_1" src="https://github.com/user-attachments/assets/5ae17a40-db4a-467a-94d2-4ce431d99ffb" />

<img width="1200" height="802" alt="UI_2" src="https://github.com/user-attachments/assets/95b2ac8b-f98d-48b9-9723-571a95163f00" />


<img width="1203" height="806" alt="UI_3" src="https://github.com/user-attachments/assets/8f8755a6-9d0a-4106-8557-8d3a47d009e8" />

## RoadMap
- Currently only RC4 encryption is implemented, which directly encrypts the data, and the data is decoded at the reciever side. This shall be expanded with Freshness value and MAC added
- Other algorithms shall be implemented going forward
- For MAC based algorithms, addition of Freshness value/counter, to provide resistance to replay attacks
- In performance metrics. encryption and decryption times have been implemented. Other metrics like deadline miss counts, cpu and ram usage need to be implemented
  



