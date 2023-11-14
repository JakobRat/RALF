v {xschem version=3.4.1 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 300 -440 360 -440 {
lab=Vl}
N 260 -500 260 -470 {
lab=Vdd}
N 400 -500 400 -470 {
lab=Vdd}
N 260 -410 260 -360 {
lab=Vl}
N 400 -410 400 -360 {
lab=Vr}
N 260 -500 400 -500 {
lab=Vdd}
N 330 -440 330 -390 {
lab=Vl}
N 260 -390 330 -390 {
lab=Vl}
N 330 -520 330 -500 {
lab=Vdd}
N 180 -440 260 -440 {
lab=Vdd}
N 180 -500 180 -440 {
lab=Vdd}
N 180 -500 260 -500 {
lab=Vdd}
N 400 -440 470 -440 {
lab=Vdd}
N 470 -500 470 -440 {
lab=Vdd}
N 400 -500 470 -500 {
lab=Vdd}
C {sky130_fd_pr/pfet_01v8.sym} 280 -440 0 1 {name=M1
L=1
W=5
nf=1
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
C {sky130_fd_pr/pfet_01v8.sym} 380 -440 0 0 {name=M2
L=1
W=5
nf=1
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
C {devices/iopin.sym} 330 -520 3 0 {name=p1 lab=Vdd}
C {devices/iopin.sym} 260 -360 1 0 {name=p2 lab=Vl}
C {devices/iopin.sym} 400 -360 1 0 {name=p3 lab=Vr}
