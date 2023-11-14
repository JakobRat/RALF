# RALF - Reinforcement Learning assisted Automated analog Layout design Flow

As part of a master's thesis, at the Institute for Integrated Circuits (IIC), Johannes Kepler University, Linz, Austria,
a automated analog layout design flow were developed.


## Getting started
### Step 0: Prerequisites
- [SKY130 PDK](https://github.com/google/skywater-pdk)
    - For easy installation check out [volare](https://github.com/efabless/volare)
- [MAGIC](https://github.com/RTimothyEdwards/magic)
- Python >= 3.10
- Path to the sky130A pdk set under `$PDKPATH`, this can look like as follows
```
    export PDKPATH=/home/pdks/sky130A
```
### Step 1: Clone the repository
```
    $ git clone https://github.com/JakobRat/RALF
```

### Step 2: Add your circuits netlist
To design your circuit, add the circuits-netlist (only `.spice` formats are supported) to the `Circuits` folder. 

#### Netlist prerequisites
- The top-circuit isn't a subcircuit.
- The netlist only contains the devices
    - sky130_fd_pr__nfet_01v8
    - sky130_fd_pr__pfet_01v8
    - sky130_fd_pr__cap_mim_m3_1
    - sky130_fd_pr__cap_mim_m3_2
    - sky130_fd_pr__res_xhigh_po_0p35
- E.g. a valid netlist looks like
```
    x1 Vin Vout1 Vdd Vss inv
    x2 Vin2 Vout Vdd Vss inv
    XR1 Vout1 Vin2 Vss sky130_fd_pr__res_xhigh_po_0p35 L=2 mult=1 m=1
    XC1 Vin2 Vss sky130_fd_pr__cap_mim_m3_1 W=4 L=4 MF=1 m=1

    .subckt inv A Y Vdd Vss
    XM1 Y A Vss Vss sky130_fd_pr__nfet_01v8 L=1 W=1 nf=1
    XM2 Y A Vdd Vdd sky130_fd_pr__pfet_01v8 L=1 W=3 nf=3
    .ends
    .end
```

## Step 2: Do a placement
There are two supported placement mechanisms:
- Reinforcement learning based (`main_RL_placement.py`)
- Simulated annealing based (`main_RPS_placement.py`)

To do a placement, adapt the global variables according to your circuit, and run the script in a shell.\
For the reinforcement learning based placement run:
```
$ python3 main_RL_placement.py
```
For the simulated annealing based placement run:
```
$ python3 main_RPS_placement.py
```
The placed circuit will be stored under `PlacementCircuits/<circuit_name>_placement.pkl`.

## Step 3: View the placement in Magic
To view the placement in Magic run the script `main_place_circuit.py`.
```
$ python3 main_place_circuit.py
```
Don't forget to adapt the variable `CIRCUIT_NAME` to your circuits name!\
The generated Magic file of the placement will be located under `Magic/Placement/<CIRCUIT_NAME>.mag`.

## Step 4: Do a routing
The routing of an already placed circuit can be performed by running the script `main_routing.py`.
```
$ python3 main_routing.py
```
Don't forget to adapt the variable `CIRCUIT_NAME` to your circuits name!\
Per default, the script generates a `.tcl`-file located under `Magic/Routing/<CIRCUIT_NAME>_routing.tcl`.\
To view the routing, open the placement in Magic per (make sure you are in the same directory as `main_routing.py`)
```
$ magic Magic/Placement/<CIRCUIT_NAME>.mag
```
then run in the Magic command shell
```
source Magic/Routing/<CIRCUIT_NAME>_routing.tcl
```

### Net-rules file
A net-rules file contains information for the routing stage.
 - To specify the needed minimum width of a nets wires put the lines
 ```
 ["MinNetWireWidth",
    {
        "net" : <SubCircuit_Instance>.<Net_name>,
        "min_width" : <min_width>
    }
 ]
 ```
 If the net is located in the top-circuit the prefix `<SubCircuit_Instance>.` hasn't to be specified. The variable `<min_width>` defines the minimum width of the wire, whereby the unit of the width is in $\lambda = 10\,\mathrm{nm}$. 

 E.g. for the netlist
 ```
    x1 Vin1 Vout Vdd Vss buf
    XR1 Vin Vin1 Vss sky130_fd_pr__res_xhigh_po_0p35 L=2 mult=1 m=1
    XC1 Vin1 Vss sky130_fd_pr__cap_mim_m3_1 W=4 L=4 MF=1 m=1

    .subckt buf A Y Vdd Vss
    x1 A Y1 Vdd Vss inv
    x2 Y1 Y Vdd Vss inv
    .ends

    .subckt inv A Y Vdd Vss
    XM1 Y A Vss Vss sky130_fd_pr__nfet_01v8 L=1 W=1 nf=1
    XM2 Y A Vdd Vdd sky130_fd_pr__pfet_01v8 L=1 W=3 nf=3
    .ends
    .end
```
  the net `Vout1` gets accessed by 
 ```
 ["MinNetWireWidth",
    {
        "net" : Vout1,
        "min_width" : 20
    }
 ]
 ``` 

 The net `Y1` in the sub-circuit `buf` of device `x1` gets accessed by
 ```
 ["MinNetWireWidth",
    {
        "net" : x1.Y1,
        "min_width" : 20
    }
 ]
 ``` 

# Example - Differential amplifier 

In the following, the layout generation flow for the circuit `Circuits/Examples/DiffAmp.spice`, will be presented.

## Schematic

<p align="left">
    <img src="Images/Example/DiffAmp_circuit.png" width="300" />
<p/>

## Placement
Run for example
```
$ python3 main_RPS_placement.py
```
and place the circuit in Magic, per
```
$ python3 main_place_circuit.py
```

Resulting placement:
<p align="left">
    <img src="Images/Example/DiffAmp_placement1.png" width="300" />
    <img src="Images/Example/DiffAmp_placement2.png" width="300" />
<p/>    


## Routing
Run 
```
$ python3 main_routing.py
```
and show the routing in Magic per
```
source Magic/Routing/DiffAmp_routing.tcl
```
Resulting routing:
<p align="left">
    <img src="Images/Example/DiffAmp_routing1.png" width="300" />
    <img src="Images/Example/DiffAmp_routing2.png" width="300" />
<p/> 