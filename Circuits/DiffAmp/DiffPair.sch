v {xschem version=3.4.1 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 200 -200 420 -200 {
lab=GND}
N 200 -170 200 -130 {
lab=Vs}
N 200 -130 300 -130 {
lab=Vs}
N 300 -130 420 -130 {
lab=Vs}
N 420 -170 420 -130 {
lab=Vs}
N 130 -200 160 -200 {
lab=Vn}
N 460 -200 480 -200 {
lab=Vp}
N 200 -280 200 -230 {
lab=Vdn}
N 420 -280 420 -230 {
lab=Vdp}
N 310 -240 310 -200 {
lab=GND}
N 300 -130 300 -100 {
lab=Vs}
C {sky130_fd_pr/nfet_01v8.sym} 180 -200 0 0 {name=M1
L=1
W=3
nf=1 
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
C {sky130_fd_pr/nfet_01v8.sym} 440 -200 0 1 {name=M2
L=1
W=3
nf=1 
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
C {devices/ipin.sym} 130 -200 0 0 {name=p1 sig_type=std_logic lab=Vn}
C {devices/ipin.sym} 480 -200 0 1 {name=p2 sig_type=std_logic lab=Vp}
C {devices/iopin.sym} 310 -240 3 0 {name=p3 lab=Vb}
C {devices/iopin.sym} 300 -100 1 0 {name=p4 lab=Vs}
C {devices/iopin.sym} 200 -280 3 0 {name=p5 lab=Vdn}
C {devices/iopin.sym} 420 -280 3 0 {name=p6 lab=Vdp}
