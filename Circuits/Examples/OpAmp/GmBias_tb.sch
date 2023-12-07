v {xschem version=3.4.1 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N -450 -70 -450 0 {
lab=GND}
N -450 -190 -450 -130 {
lab=VDD}
N 0 -100 40 -100 {
lab=VDD}
N 0 -150 0 -100 {
lab=VDD}
N 0 -60 40 -60 {
lab=GND}
N 0 -60 -0 -20 {
lab=GND}
N -30 -80 40 -80 {
lab=Vbias}
C {/home/jakob/Documents/RALF/Circuits/Examples/MillerOpAmpCMMFB/GmBias.sym} 190 -80 0 1 {name=x1}
C {devices/vsource.sym} -450 -100 0 0 {name=V3 value=1.8}
C {devices/gnd.sym} -450 0 0 0 {name=l3 lab=GND}
C {devices/vdd.sym} -450 -190 0 0 {name=l4 lab=VDD}
C {devices/vdd.sym} 0 -150 0 0 {name=l1 lab=VDD}
C {devices/gnd.sym} 0 -20 0 0 {name=l2 lab=GND}
C {devices/lab_wire.sym} -30 -80 0 0 {name=p1 sig_type=std_logic lab=Vbias}
C {devices/simulator_commands.sym} -460 -400 0 0 {name=COMMANDS
simulator=ngspice
only_toplevel=false 
value="
* ngspice commands
.option savecurrents
.save all
.control
op
.endc
"}
C {devices/code_shown.sym} -270 -420 0 0 {name=ngspice 
only_toplevel=false 
format="tcleval( @value )"
value=
".lib $::SKYWATER_MODELS/sky130.lib.spice tt
"}
