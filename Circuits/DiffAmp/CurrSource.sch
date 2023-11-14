v {xschem version=3.4.1 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 100 -30 170 -30 {
lab=GND}
N 20 -30 60 -30 {}
N 100 0 100 20 {}
N 100 20 170 20 {}
N 170 -30 170 20 {}
N 100 20 100 40 {}
N 100 -100 100 -60 {}
C {sky130_fd_pr/nfet_01v8.sym} 80 -30 0 0 {name=M3
L=1
W=2
nf=5 
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
C {devices/ipin.sym} 20 -30 0 0 {name=p1 sig_type=std_logic lab=Vbias}
C {devices/iopin.sym} 100 40 1 0 {name=p4 lab=Vs}
C {devices/iopin.sym} 100 -100 3 0 {name=p5 lab=Vp}
