v {xschem version=3.4.1 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 40 -170 40 -100 {
lab=GND}
N 40 -290 40 -230 {
lab=VDD}
N 280 -310 380 -310 {
lab=vd}
N 280 -270 380 -270 {
lab=GND}
N 330 -270 330 -250 {
lab=GND}
N 240 -260 240 -220 {
lab=Vcmm}
N 240 -220 420 -220 {
lab=Vcmm}
N 420 -260 420 -220 {
lab=Vcmm}
N 330 -220 330 -180 {
lab=Vcmm}
N 330 -120 330 -100 {
lab=GND}
N 240 -370 240 -320 {
lab=Vp}
N 420 -370 420 -320 {
lab=Vn}
N 140 -170 140 -100 {
lab=GND}
N 140 -280 140 -230 {
lab=vd}
N 620 -240 660 -240 {
lab=Vp}
N 620 -220 660 -220 {
lab=Vn}
N 620 -260 660 -260 {
lab=Vcmm}
N 960 -260 980 -260 {
lab=VDD}
N 980 -290 980 -260 {
lab=VDD}
N 960 -240 1000 -240 {
lab=Voutp}
N 960 -220 1000 -220 {
lab=Voutn}
N 960 -200 980 -200 {
lab=GND}
N 980 -200 980 -170 {
lab=GND}
N 1070 -220 1100 -220 {
lab=Voutn}
N 1100 -220 1100 -190 {
lab=Voutn}
N 1100 -130 1100 -110 {
lab=GND}
N 1070 -240 1100 -240 {
lab=Voutp}
N 1100 -280 1100 -240 {
lab=Voutp}
N 1100 -360 1100 -340 {
lab=GND}
N 1000 -240 1070 -240 {
lab=Voutp}
N 1000 -220 1070 -220 {
lab=Voutn}
C {devices/vsource.sym} 40 -200 0 0 {name=V3 value=1.8}
C {devices/gnd.sym} 40 -100 0 0 {name=l3 lab=GND}
C {devices/vdd.sym} 40 -290 0 0 {name=l4 lab=VDD}
C {devices/vcvs.sym} 240 -290 0 1 {name=E1 value=0.5}
C {devices/vcvs.sym} 420 -290 0 0 {name=E2 value=-0.5}
C {devices/vsource.sym} 330 -150 0 0 {name=Vcmm value=0.9}
C {devices/gnd.sym} 330 -100 0 0 {name=l8 lab=GND}
C {devices/lab_wire.sym} 240 -370 0 1 {name=p6 sig_type=std_logic lab=Vp}
C {devices/lab_wire.sym} 420 -370 0 1 {name=p7 sig_type=std_logic lab=Vn}
C {devices/gnd.sym} 330 -250 0 0 {name=l9 lab=GND}
C {devices/lab_wire.sym} 320 -310 0 1 {name=p8 sig_type=std_logic lab=vd}
C {devices/vsource.sym} 140 -200 0 0 {name=Vd value="dc 0 ac 1"}
C {devices/gnd.sym} 140 -100 0 0 {name=l10 lab=GND}
C {devices/lab_wire.sym} 140 -280 0 1 {name=p9 sig_type=std_logic lab=vd}
C {devices/simulator_commands.sym} 10 -490 0 0 {name=COMMANDS
simulator=ngspice
only_toplevel=false 
value="
* ngspice commands
.option savecurrents
.save all
.control
ac dec 1001 1 100Meg
let vod = V(Voutp)-V(Voutn)
meas ac gain max vod
let gain3dB = gain/sqrt(2)
meas ac BW TRIG at=1 TARG vod val=gain3dB fall=LAST
let GBW = BW*gain*1e-6
print GBW
print vodmax
plot vdb(vod) xlimit 1k 100Meg ylabel 'small signal gain'
let outd = 180/PI*cph(vod)
meas ac ftHz when vdb(vod)=1 fall=LAST
meas ac ph find outd when vdb(vod)=0 fall=LAST
let phm = ph+180
print phm
settype phase outd
plot outd xlimit 1k 100Meg ylabel 'phase'
dc Vd -0.02 0.02 1m
let vod = V(Voutp)-V(Voutn)
plot vod
op
write MillerOpAmp_tb.raw
.endc
"}
C {devices/code_shown.sym} 200 -510 0 0 {name=ngspice 
only_toplevel=false 
format="tcleval( @value )"
value=
".lib $::SKYWATER_MODELS/sky130.lib.spice tt
"}
C {devices/lab_wire.sym} 330 -220 0 1 {name=p21 sig_type=std_logic lab=Vcmm}
C {devices/lab_wire.sym} 620 -240 0 0 {name=p1 sig_type=std_logic lab=Vp}
C {devices/lab_wire.sym} 620 -220 0 0 {name=p2 sig_type=std_logic lab=Vn}
C {devices/lab_wire.sym} 620 -260 0 0 {name=p3 sig_type=std_logic lab=Vcmm}
C {devices/gnd.sym} 980 -170 0 0 {name=l1 lab=GND}
C {devices/vdd.sym} 980 -290 0 0 {name=l2 lab=VDD}
C {devices/lab_wire.sym} 1000 -240 0 1 {name=p11 sig_type=std_logic lab=Voutp}
C {devices/lab_wire.sym} 1000 -220 0 1 {name=p4 sig_type=std_logic lab=Voutn}
C {devices/capa.sym} 1100 -160 0 0 {name=C2
m=1
value=50f
footprint=1206
device="ceramic capacitor"}
C {devices/capa.sym} 1100 -310 2 0 {name=C1
m=1
value=50f
footprint=1206
device="ceramic capacitor"}
C {devices/gnd.sym} 1100 -110 0 0 {name=l7 lab=GND}
C {devices/gnd.sym} 1100 -360 2 0 {name=l11 lab=GND}
C {devices/title.sym} 150 0 0 0 {name=l5 author="Jakob Ratschenberger"}
C {/home/jakob/Documents/RALF/Circuits/Examples/OpAmp/OpAmp.sym} 810 -230 0 0 {name=x1}
