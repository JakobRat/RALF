v {xschem version=3.4.1 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 90 -240 90 -100 {
lab=Vbias}
N 90 -130 160 -130 {
lab=Vbias}
N 160 -130 160 -70 {
lab=Vbias}
N 90 -40 90 0 {
lab=Vss}
N 90 -260 90 -240 {
lab=Vbias}
N 90 -340 90 -320 {
lab=Vdd}
N 20 -70 90 -70 {
lab=Vss}
N 20 -70 20 0 {
lab=Vss}
N 20 0 90 0 {
lab=Vss}
N 130 -70 160 -70 {
lab=Vbias}
N 160 -70 210 -70 {
lab=Vbias}
N 90 -0 120 -0 {
lab=Vss}
N 110 -290 160 -290 {
lab=#net1}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 90 -290 0 1 {name=R3
L=0.35
model=res_xhigh_po_0p35
spiceprefix=X
mult=1}
C {sky130_fd_pr/nfet_01v8.sym} 110 -70 0 1 {name=M4
L=1
W=1
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
C {devices/iopin.sym} 210 -70 0 0 {name=p7 sig_type=std_logic lab=Vbias}
C {devices/iopin.sym} 90 -340 3 0 {name=p1 sig_type=std_logic lab=Vdd}
C {devices/iopin.sym} 120 0 0 0 {name=p2 sig_type=std_logic lab=Vss}
C {devices/lab_wire.sym} 160 -290 0 1 {name=p3 sig_type=std_logic lab=Vss}
