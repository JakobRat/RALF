v {xschem version=3.4.1 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 620 -340 620 -260 {
lab=Vmid}
N 620 -260 860 -260 {
lab=Vmid}
N 860 -340 860 -260 {
lab=Vmid}
N 620 -370 860 -370 {
lab=Vss}
N 620 -560 620 -400 {
lab=Vop}
N 860 -560 860 -400 {
lab=Von}
N 500 -370 580 -370 {
lab=Vp}
N 900 -370 980 -370 {
lab=Vn}
N 740 -260 740 -200 {
lab=Vmid}
N 620 -730 620 -620 {
lab=Vdd}
N 620 -730 860 -730 {
lab=Vdd}
N 860 -730 860 -620 {
lab=Vdd}
N 740 -620 740 -590 {
lab=Vbp}
N 540 -590 620 -590 {
lab=Vdd}
N 540 -730 540 -590 {
lab=Vdd}
N 540 -730 620 -730 {
lab=Vdd}
N 860 -590 940 -590 {
lab=Vdd}
N 940 -730 940 -590 {
lab=Vdd}
N 860 -730 940 -730 {
lab=Vdd}
N 740 -770 740 -730 {
lab=Vdd}
N 620 -170 700 -170 {
lab=Vbn}
N 740 -140 740 -100 {
lab=Vss}
N 620 -480 680 -480 {
lab=Vop}
N 800 -480 860 -480 {
lab=Von}
N 740 -170 830 -170 {
lab=Vss}
N 830 -170 830 -120 {
lab=Vss}
N 740 -120 830 -120 {
lab=Vss}
N 660 -590 680 -590 {
lab=Vbp}
N 800 -590 820 -590 {
lab=Vbp}
N 680 -590 740 -590 {
lab=Vbp}
N 740 -590 800 -590 {
lab=Vbp}
C {sky130_fd_pr/nfet_01v8.sym} 600 -370 0 0 {name=M1
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
C {sky130_fd_pr/nfet_01v8.sym} 880 -370 0 1 {name=M2
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
C {sky130_fd_pr/pfet_01v8.sym} 640 -590 0 1 {name=M3
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
C {sky130_fd_pr/pfet_01v8.sym} 840 -590 0 0 {name=M4
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
C {devices/iopin.sym} 740 -770 3 0 {name=p1 lab=Vdd}
C {devices/iopin.sym} 740 -100 3 1 {name=p2 lab=Vss}
C {devices/ipin.sym} 500 -370 0 0 {name=p3 lab=Vp}
C {devices/ipin.sym} 980 -370 0 1 {name=p4 lab=Vn}
C {devices/ipin.sym} 620 -170 0 0 {name=p5 lab=Vbn}
C {devices/ipin.sym} 740 -620 1 0 {name=p6 lab=Vbp}
C {devices/opin.sym} 680 -480 0 0 {name=p7 lab=Vop}
C {devices/opin.sym} 800 -480 0 1 {name=p8 lab=Von}
C {devices/lab_wire.sym} 740 -260 0 0 {name=p9 sig_type=std_logic lab=vmid}
C {devices/lab_wire.sym} 740 -370 0 0 {name=p10 sig_type=std_logic lab=Vss}
C {devices/title.sym} 160 0 0 0 {name=l1 author="Jakob Ratschenberger"}
