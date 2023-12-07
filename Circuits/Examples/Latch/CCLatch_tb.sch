v {xschem version=3.4.1 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N -560 -20 -560 0 {
lab=GND}
N -560 -100 -560 -80 {
lab=VDD}
N -450 -20 -450 0 {
lab=GND}
N -450 -100 -450 -80 {
lab=clk}
N 250 -110 320 -110 {
lab=clk}
N 180 -130 320 -130 {
lab=in}
N 180 -90 320 -90 {
lab=inn}
N 620 -120 660 -120 {
lab=out}
N 620 -100 660 -100 {
lab=outn}
N -190 -20 -190 0 {
lab=GND}
N -190 -100 -190 -80 {
lab=in}
N -10 -20 -10 0 {
lab=GND}
N -60 -30 -50 -30 {
lab=GND}
N -60 -30 -60 -10 {
lab=GND}
N -60 -10 -10 -10 {
lab=GND}
N -60 -70 -50 -70 {
lab=in}
N -60 -90 -60 -70 {
lab=in}
N -190 -90 -60 -90 {
lab=in}
N -10 -100 -10 -80 {
lab=#net1}
N -10 -180 -10 -160 {
lab=inn}
C {/home/jakob/Documents/RALF/Circuits/Examples/Latch/CCLatch.sym} 470 -110 0 0 {name=x1}
C {devices/vsource.sym} -560 -50 0 0 {name=V1 value=1.8}
C {devices/vdd.sym} -560 -100 0 0 {name=l1 lab=VDD}
C {devices/vdd.sym} 470 -170 0 0 {name=l2 lab=VDD}
C {devices/gnd.sym} -560 0 0 0 {name=l3 lab=GND}
C {devices/gnd.sym} 470 -50 0 0 {name=l4 lab=GND}
C {devices/vsource.sym} -450 -50 0 0 {name=V2 value="PULSE(0 1.8 5n 0.1n 0.1n 5ns 10ns 10)"}
C {devices/gnd.sym} -450 0 0 0 {name=l6 lab=GND}
C {devices/lab_wire.sym} -450 -100 0 0 {name=p1 sig_type=std_logic lab=clk}
C {devices/lab_wire.sym} 250 -110 0 0 {name=p2 sig_type=std_logic lab=clk}
C {devices/vsource.sym} -190 -50 0 0 {name=V3 value="PULSE(0 1.8 2.5ns 0.1n 0.1n 5ns 20ns 5)"}
C {devices/gnd.sym} -190 0 0 0 {name=l5 lab=GND}
C {devices/lab_wire.sym} -190 -100 0 0 {name=p3 sig_type=std_logic lab=in}
C {devices/vcvs.sym} -10 -50 0 0 {name=E1 value=-1}
C {devices/gnd.sym} -10 0 0 0 {name=l7 lab=GND}
C {devices/lab_wire.sym} -10 -180 0 0 {name=p4 sig_type=std_logic lab=inn}
C {devices/lab_wire.sym} 180 -130 0 0 {name=p5 sig_type=std_logic lab=in}
C {devices/lab_wire.sym} 180 -90 0 0 {name=p6 sig_type=std_logic lab=inn}
C {devices/lab_wire.sym} 660 -120 0 1 {name=p7 sig_type=std_logic lab=out}
C {devices/lab_wire.sym} 660 -100 0 1 {name=p8 sig_type=std_logic lab=outn}
C {devices/vsource.sym} -10 -130 0 0 {name=V4 value=1.8}
C {devices/simulator_commands.sym} -190 -520 0 0 {name=COMMANDS
simulator=ngspice
only_toplevel=false 
value="
* ngspice commands
.option savecurrents
.save all
.control
tran 1ns 100ns
.endc
"}
C {devices/code_shown.sym} 0 -540 0 0 {name=ngspice 
only_toplevel=false 
format="tcleval( @value )"
value=
".lib $::SKYWATER_MODELS/sky130.lib.spice tt
"}
