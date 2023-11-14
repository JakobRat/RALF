v {xschem version=3.4.1 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 140 -340 140 -320 {
lab=Vdd}
N 140 -320 140 -270 {
lab=Vdd}
N 140 -210 140 -140 {
lab=Vout}
N 140 -140 140 -100 {
lab=Vout}
N 140 -40 140 0 {
lab=Vss}
N 60 -70 120 -70 {
lab=Vss}
N 60 -70 60 0 {
lab=Vss}
N 140 -160 180 -160 {
lab=Vout}
N 140 -240 220 -240 {
lab=Vdd}
N 220 -340 220 -240 {
lab=Vdd}
N 140 -340 220 -340 {
lab=Vdd}
N -60 -240 100 -240 {
lab=Vi}
N 60 -0 140 0 {
lab=Vss}
N 140 -370 140 -340 {
lab=Vdd}
N 30 0 60 -0 {
lab=Vss}
C {sky130_fd_pr/pfet_01v8.sym} 120 -240 0 0 {name=M5
L=2
W=20
nf=10
mult=1
ad="'int((nf+1)/2) * W/nf * 0.29'" 
pd="'2*int((nf+1)/2) * (W/nf + 0.29)'"
as="'int((nf+2)/2) * W/nf * 0.29'" 
ps="'2*int((nf+2)/2) * (W/nf + 0.29)'"
nrd="'0.29 / W'" nrs="'0.29 / W'"
sa=0 sb=0 sd=0
model=pfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 140 -70 0 0 {name=R4
L=20
model=res_xhigh_po_0p35
spiceprefix=X
mult=1}
C {devices/opin.sym} 180 -160 2 1 {name=p3 sig_type=std_logic lab=Vout}
C {devices/ipin.sym} -60 -240 2 1 {name=p1 sig_type=std_logic lab=Vi}
C {devices/iopin.sym} 140 -370 1 1 {name=p2 sig_type=std_logic lab=Vdd}
C {devices/iopin.sym} 30 0 0 1 {name=p4 sig_type=std_logic lab=Vss}
