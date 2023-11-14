v {xschem version=3.4.1 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N -790 -80 -790 -10 {
lab=GND}
N -790 -200 -790 -140 {
lab=VDD}
N -550 -220 -450 -220 {
lab=vd}
N -550 -180 -450 -180 {
lab=GND}
N -500 -180 -500 -160 {
lab=GND}
N -590 -170 -590 -130 {
lab=Vcmm}
N -590 -130 -410 -130 {
lab=Vcmm}
N -410 -170 -410 -130 {
lab=Vcmm}
N -500 -130 -500 -90 {
lab=Vcmm}
N -500 -30 -500 -10 {
lab=GND}
N -590 -280 -590 -230 {
lab=Vp}
N -410 -280 -410 -230 {
lab=Vn}
N -690 -80 -690 -10 {
lab=GND}
N -690 -190 -690 -140 {
lab=vd}
N -40 -170 -0 -170 {
lab=Vp}
N -40 -150 0 -150 {
lab=Vn}
N -40 -190 -0 -190 {
lab=Vcmm}
N 300 -190 320 -190 {
lab=VDD}
N 320 -220 320 -190 {
lab=VDD}
N 300 -170 340 -170 {
lab=Voutp}
N 300 -150 340 -150 {
lab=Voutn}
N 300 -130 320 -130 {
lab=GND}
N 320 -130 320 -100 {
lab=GND}
N 410 -150 440 -150 {
lab=Voutn}
N 440 -150 440 -120 {
lab=Voutn}
N 440 -60 440 -40 {
lab=GND}
N 410 -170 440 -170 {
lab=Voutp}
N 440 -210 440 -170 {
lab=Voutp}
N 440 -290 440 -270 {
lab=GND}
N 340 -170 410 -170 {
lab=Voutp}
N 340 -150 410 -150 {
lab=Voutn}
C {devices/vsource.sym} -790 -110 0 0 {name=V3 value=1.8}
C {devices/gnd.sym} -790 -10 0 0 {name=l3 lab=GND}
C {devices/vdd.sym} -790 -200 0 0 {name=l4 lab=VDD}
C {devices/vcvs.sym} -590 -200 0 1 {name=E1 value=0.5}
C {devices/vcvs.sym} -410 -200 0 0 {name=E2 value=-0.5}
C {devices/vsource.sym} -500 -60 0 0 {name=Vcmm value=0.9}
C {devices/gnd.sym} -500 -10 0 0 {name=l8 lab=GND}
C {devices/lab_wire.sym} -590 -280 0 1 {name=p6 sig_type=std_logic lab=Vp}
C {devices/lab_wire.sym} -410 -280 0 1 {name=p7 sig_type=std_logic lab=Vn}
C {devices/gnd.sym} -500 -160 0 0 {name=l9 lab=GND}
C {devices/lab_wire.sym} -510 -220 0 1 {name=p8 sig_type=std_logic lab=vd}
C {devices/vsource.sym} -690 -110 0 0 {name=Vd value="dc 0 ac 1"}
C {devices/gnd.sym} -690 -10 0 0 {name=l10 lab=GND}
C {devices/lab_wire.sym} -690 -190 0 1 {name=p9 sig_type=std_logic lab=vd}
C {devices/simulator_commands.sym} -730 -700 0 0 {name=COMMANDS
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
C {devices/code_shown.sym} -540 -720 0 0 {name=ngspice 
only_toplevel=false 
format="tcleval( @value )"
value=
".lib $::SKYWATER_MODELS/sky130.lib.spice tt
"}
C {devices/lab_wire.sym} -500 -130 0 1 {name=p21 sig_type=std_logic lab=Vcmm}
C {/foss/designs/xschem/MillerOpAmp/OpAmp.sym} 150 -160 0 0 {name=x1}
C {devices/lab_wire.sym} -40 -170 0 0 {name=p1 sig_type=std_logic lab=Vp}
C {devices/lab_wire.sym} -40 -150 0 0 {name=p2 sig_type=std_logic lab=Vn}
C {devices/lab_wire.sym} -40 -190 0 0 {name=p3 sig_type=std_logic lab=Vcmm}
C {devices/gnd.sym} 320 -100 0 0 {name=l1 lab=GND}
C {devices/vdd.sym} 320 -220 0 0 {name=l2 lab=VDD}
C {devices/lab_wire.sym} 340 -170 0 1 {name=p11 sig_type=std_logic lab=Voutp}
C {devices/lab_wire.sym} 340 -150 0 1 {name=p4 sig_type=std_logic lab=Voutn}
C {devices/capa.sym} 440 -90 0 0 {name=C2
m=1
value=50f
footprint=1206
device="ceramic capacitor"}
C {devices/capa.sym} 440 -240 2 0 {name=C1
m=1
value=50f
footprint=1206
device="ceramic capacitor"}
C {devices/gnd.sym} 440 -40 0 0 {name=l7 lab=GND}
C {devices/gnd.sym} 440 -290 2 0 {name=l11 lab=GND}
