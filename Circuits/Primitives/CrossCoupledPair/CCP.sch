v {xschem version=3.4.1 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 110 -30 140 -30 {
lab=Vd2}
N 140 -60 140 -30 {
lab=Vd2}
N 170 -30 190 -30 {
lab=Vd1}
N 170 -60 170 -30 {
lab=Vd1}
N 140 -60 170 -80 {
lab=Vd2}
N 170 -80 230 -80 {
lab=Vd2}
N 140 -80 170 -60 {
lab=Vd1}
N 70 -80 140 -80 {
lab=Vd1}
N 230 -70 230 -60 {
lab=Vd2}
N 70 -70 70 -60 {
lab=Vd1}
N 70 -80 70 -70 {
lab=Vd1}
N 70 -110 70 -80 {
lab=Vd1}
N 230 -80 230 -70 {
lab=Vd2}
N 230 -110 230 -80 {
lab=Vd2}
N 70 0 70 20 {
lab=Vs1}
N 70 20 70 30 {
lab=Vs1}
N 230 0 230 30 {
lab=Vs2}
N 0 -30 70 -30 {
lab=Vb}
N 230 -30 300 -30 {
lab=xxx}
C {sky130_fd_pr/nfet_01v8.sym} 90 -30 0 1 {name=M1
L=0.15
W=2
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
C {sky130_fd_pr/nfet_01v8.sym} 210 -30 0 0 {name=M2
L=0.15
W=2
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
C {devices/iopin.sym} 70 -110 3 0 {name=p1 lab=Vd1}
C {devices/iopin.sym} 230 -110 3 0 {name=p2 lab=Vd2}
C {devices/iopin.sym} 230 30 1 0 {name=p3 lab=Vs2}
C {devices/iopin.sym} 70 30 1 0 {name=p4 lab=Vs1}
C {devices/iopin.sym} 0 -30 2 0 {name=p5 lab=Vb}
C {devices/lab_wire.sym} 300 -30 0 1 {name=p6 sig_type=std_logic lab=Vb}
