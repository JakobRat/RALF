v {xschem version=3.4.1 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 620 -270 620 -230 {
lab=Vmid}
N 620 -230 860 -230 {
lab=Vmid}
N 860 -270 860 -230 {
lab=Vmid}
N 620 -300 860 -300 {
lab=Vss}
N 620 -400 620 -330 {
lab=Vop}
N 860 -400 860 -330 {
lab=Von}
N 540 -300 580 -300 {
lab=Vp}
N 900 -300 940 -300 {
lab=Vn}
N 740 -230 740 -200 {
lab=Vmid}
N 620 -530 620 -460 {
lab=Vdd}
N 620 -530 860 -530 {
lab=Vdd}
N 860 -530 860 -460 {
lab=Vdd}
N 740 -460 740 -430 {
lab=Vbp}
N 540 -430 620 -430 {
lab=Vdd}
N 540 -530 540 -430 {
lab=Vdd}
N 540 -530 620 -530 {
lab=Vdd}
N 860 -430 940 -430 {
lab=Vdd}
N 940 -530 940 -430 {
lab=Vdd}
N 860 -530 940 -530 {
lab=Vdd}
N 740 -570 740 -530 {
lab=Vdd}
N 620 -170 700 -170 {
lab=Vbn}
N 740 -140 740 -100 {
lab=Vss}
N 620 -370 680 -370 {
lab=Vop}
N 800 -370 860 -370 {
lab=Von}
N 740 -170 830 -170 {
lab=Vss}
N 830 -170 830 -120 {
lab=Vss}
N 740 -120 830 -120 {
lab=Vss}
N 660 -430 680 -430 {
lab=Vbp}
N 800 -430 820 -430 {
lab=Vbp}
N 680 -430 740 -430 {
lab=Vbp}
N 740 -430 800 -430 {
lab=Vbp}
C {sky130_fd_pr/nfet_01v8.sym} 600 -300 0 0 {name=M1
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
C {sky130_fd_pr/nfet_01v8.sym} 880 -300 0 1 {name=M2
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
C {sky130_fd_pr/pfet_01v8.sym} 640 -430 0 1 {name=M3
L=1
W=2
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
C {sky130_fd_pr/pfet_01v8.sym} 840 -430 0 0 {name=M4
L=1
W=2
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
C {sky130_fd_pr/nfet_01v8.sym} 720 -170 0 0 {name=M5
L=2
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
C {devices/iopin.sym} 740 -570 3 0 {name=p1 lab=Vdd}
C {devices/iopin.sym} 740 -100 3 1 {name=p2 lab=Vss}
C {devices/ipin.sym} 540 -300 0 0 {name=p3 lab=Vp}
C {devices/ipin.sym} 940 -300 0 1 {name=p4 lab=Vn}
C {devices/ipin.sym} 620 -170 0 0 {name=p5 lab=Vbn}
C {devices/ipin.sym} 740 -460 1 0 {name=p6 lab=Vbp}
C {devices/opin.sym} 680 -370 0 0 {name=p7 lab=Vop}
C {devices/opin.sym} 800 -370 0 1 {name=p8 lab=Von}
C {devices/lab_wire.sym} 740 -230 0 0 {name=p9 sig_type=std_logic lab=vmid}
C {devices/lab_wire.sym} 740 -300 0 0 {name=p10 sig_type=std_logic lab=Vss}
C {devices/title.sym} 160 0 0 0 {name=l1 author="Jakob Ratschenberger"}
