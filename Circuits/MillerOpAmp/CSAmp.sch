v {xschem version=3.4.1 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 280 -320 280 -160 {
lab=Vo}
N 280 -420 280 -380 {
lab=Vdd}
N 140 -350 240 -350 {
lab=Vi}
N 280 -350 360 -350 {
lab=Vdd}
N 360 -400 360 -350 {
lab=Vdd}
N 280 -400 360 -400 {
lab=Vdd}
N 280 -100 280 -40 {
lab=Vss}
N 280 -130 360 -130 {
lab=Vss}
N 360 -130 360 -70 {
lab=Vss}
N 280 -70 360 -70 {
lab=Vss}
N 140 -130 240 -130 {
lab=Vbias1}
N 280 -240 400 -240 {
lab=Vo}
C {sky130_fd_pr/pfet_01v8.sym} 260 -350 0 0 {name=M1
L=1
W=4
nf=2
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
C {sky130_fd_pr/nfet_01v8.sym} 260 -130 0 0 {name=M2
L=2
W=8
nf=4 
mult=1
ad="'int((nf+1)/2) * W/nf * 0.29'" 
pd="'2*int((nf+1)/2) * (W/nf + 0.29)'"
as="'int((nf+2)/2) * W/nf * 0.29'" 
ps="'2*int((nf+2)/2) * (W/nf + 0.29)'"
nrd="'0.29 / W'" nrs="'0.29 / W'"
sa=0 sb=0 sd=0
model=nfet_01v8
spiceprefix=X
}
C {devices/ipin.sym} 140 -130 0 0 {name=p5 lab=Vbias1}
C {devices/ipin.sym} 140 -350 0 0 {name=p3 lab=Vi}
C {devices/iopin.sym} 280 -420 3 0 {name=p1 lab=Vdd}
C {devices/iopin.sym} 280 -40 3 1 {name=p2 lab=Vss}
C {devices/opin.sym} 400 -240 0 0 {name=p7 lab=Vo}
