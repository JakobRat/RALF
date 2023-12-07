v {xschem version=3.4.1 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 50 -170 50 -100 {
lab=GND}
N 50 -290 50 -230 {
lab=VDD}
N 290 -310 390 -310 {
lab=vd}
N 290 -270 390 -270 {
lab=GND}
N 340 -270 340 -250 {
lab=GND}
N 250 -260 250 -220 {
lab=Vcmm}
N 250 -220 430 -220 {
lab=Vcmm}
N 430 -260 430 -220 {
lab=Vcmm}
N 340 -220 340 -180 {
lab=Vcmm}
N 340 -120 340 -100 {
lab=GND}
N 250 -370 250 -320 {
lab=Vp}
N 430 -370 430 -320 {
lab=Vn}
N 150 -170 150 -100 {
lab=GND}
N 150 -280 150 -230 {
lab=vd}
N 630 -240 670 -240 {
lab=Vn}
N 630 -220 670 -220 {
lab=Vp}
N 630 -260 670 -260 {
lab=Vcmm}
N 970 -260 990 -260 {
lab=VDD}
N 990 -290 990 -260 {
lab=VDD}
N 970 -240 1010 -240 {
lab=Voutp}
N 970 -220 1010 -220 {
lab=Voutn}
N 970 -200 990 -200 {
lab=GND}
N 990 -200 990 -170 {
lab=GND}
N 1080 -220 1110 -220 {
lab=Voutn}
N 1110 -220 1110 -190 {
lab=Voutn}
N 1110 -130 1110 -110 {
lab=GND}
N 1080 -240 1110 -240 {
lab=Voutp}
N 1110 -280 1110 -240 {
lab=Voutp}
N 1110 -360 1110 -340 {
lab=GND}
N 1010 -240 1080 -240 {
lab=Voutp}
N 1010 -220 1080 -220 {
lab=Voutn}
C {devices/vsource.sym} 50 -200 0 0 {name=V3 value=1.8}
C {devices/gnd.sym} 50 -100 0 0 {name=l3 lab=GND}
C {devices/vdd.sym} 50 -290 0 0 {name=l4 lab=VDD}
C {devices/vcvs.sym} 250 -290 0 1 {name=E1 value=0.5}
C {devices/vcvs.sym} 430 -290 0 0 {name=E2 value=-0.5}
C {devices/vsource.sym} 340 -150 0 0 {name=Vcmm value=0.9}
C {devices/gnd.sym} 340 -100 0 0 {name=l8 lab=GND}
C {devices/lab_wire.sym} 250 -370 0 1 {name=p6 sig_type=std_logic lab=Vp}
C {devices/lab_wire.sym} 430 -370 0 1 {name=p7 sig_type=std_logic lab=Vn}
C {devices/gnd.sym} 340 -250 0 0 {name=l9 lab=GND}
C {devices/lab_wire.sym} 330 -310 0 1 {name=p8 sig_type=std_logic lab=vd}
C {devices/vsource.sym} 150 -200 0 0 {name=Vd value="dc 0 ac 1 SIN(0 0.01 10k)"}
C {devices/gnd.sym} 150 -100 0 0 {name=l10 lab=GND}
C {devices/lab_wire.sym} 150 -280 0 1 {name=p9 sig_type=std_logic lab=vd}
C {devices/simulator_commands.sym} 20 -490 0 0 {name=COMMANDS
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
tran 1u 1m
let vod = v(voutp)-v(voutn)
plot vod
op
.endc
"}
C {devices/code_shown.sym} 210 -510 0 0 {name=ngspice 
only_toplevel=false 
format="tcleval( @value )"
value=
".lib $::SKYWATER_MODELS/sky130.lib.spice tt
"}
C {devices/lab_wire.sym} 340 -220 0 1 {name=p21 sig_type=std_logic lab=Vcmm}
C {devices/lab_wire.sym} 630 -220 0 0 {name=p1 sig_type=std_logic lab=Vp}
C {devices/lab_wire.sym} 630 -240 0 0 {name=p2 sig_type=std_logic lab=Vn}
C {devices/lab_wire.sym} 630 -260 0 0 {name=p3 sig_type=std_logic lab=Vcmm}
C {devices/gnd.sym} 990 -170 0 0 {name=l1 lab=GND}
C {devices/vdd.sym} 990 -290 0 0 {name=l2 lab=VDD}
C {devices/lab_wire.sym} 1010 -240 0 1 {name=p11 sig_type=std_logic lab=Voutp}
C {devices/lab_wire.sym} 1010 -220 0 1 {name=p4 sig_type=std_logic lab=Voutn}
C {devices/capa.sym} 1110 -160 0 0 {name=C2
m=1
value=50f
footprint=1206
device="ceramic capacitor"}
C {devices/capa.sym} 1110 -310 2 0 {name=C1
m=1
value=50f
footprint=1206
device="ceramic capacitor"}
C {devices/gnd.sym} 1110 -110 0 0 {name=l7 lab=GND}
C {devices/gnd.sym} 1110 -360 2 0 {name=l11 lab=GND}
C {devices/title.sym} 160 0 0 0 {name=l5 author="Jakob Ratschenberger"}
C {/home/jakob/Documents/RALF/Circuits/Examples/InvAmp/InvAmp.sym} 820 -230 0 0 {name=x1}
