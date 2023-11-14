v {xschem version=3.4.1 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 40 -180 80 -180 {
lab=in}
N 40 -180 40 -70 {
lab=in}
N 40 -70 40 -60 {
lab=in}
N 40 -60 80 -60 {
lab=in}
N -0 -120 40 -120 {
lab=in}
N 120 -240 120 -210 {
lab=Vdd}
N 120 -150 120 -90 {
lab=out}
N 120 -120 220 -120 {
lab=out}
N 120 -30 120 -0 {
lab=Vss}
N 120 -180 180 -180 {
lab=Vdd}
N 180 -240 180 -180 {
lab=Vdd}
N 120 -240 180 -240 {
lab=Vdd}
N 120 -60 200 -60 {
lab=Vss}
N 200 -60 200 -0 {
lab=Vss}
N 120 -0 200 -0 {
lab=Vss}
C {sky130_fd_pr/pfet_01v8_nf.sym} 100 -180 0 0 {name=M1
L=0.3
W=1
nf=8
mult=1
ad="'int((nf+1)/2) * W / nf * 0.29'"
pd="'2*int((nf+1)/2) * (W / nf + 0.29)'"
as="'int((nf+2)/2) * W / nf * 0.29'"
ps="'2*int((nf+2)/2) * (W / nf + 0.29)'"
nrd="'0.29 / W '" nrs="'0.29 / W '"
sa=0 sb=0 sd=0
model=pfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8_nf.sym} 100 -60 0 0 {name=M2
L=0.3
W=1
nf=8
mult=1
ad="'int((nf+1)/2) * W / nf * 0.29'"
pd="'2*int((nf+1)/2) * (W / nf + 0.29)'"
as="'int((nf+2)/2) * W / nf * 0.29'"
ps="'2*int((nf+2)/2) * (W / nf + 0.29)'"
nrd="'0.29 / W '" nrs="'0.29 / W '"
sa=0 sb=0 sd=0
model=nfet_01v8
spiceprefix=X
}
C {devices/iopin.sym} 120 -240 3 0 {name=p1 lab=Vdd}
C {devices/iopin.sym} 120 0 3 1 {name=p2 lab=Vss}
C {devices/ipin.sym} 0 -120 0 0 {name=p3 lab=in}
C {devices/opin.sym} 220 -120 0 0 {name=p4 lab=out}
