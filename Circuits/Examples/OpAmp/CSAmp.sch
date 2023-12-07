v {xschem version=3.4.1 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 540 -370 540 -210 {
lab=Vo}
N 540 -470 540 -430 {
lab=Vdd}
N 400 -400 500 -400 {
lab=Vi}
N 540 -400 620 -400 {
lab=Vdd}
N 620 -450 620 -400 {
lab=Vdd}
N 540 -450 620 -450 {
lab=Vdd}
N 540 -150 540 -90 {
lab=Vss}
N 540 -180 620 -180 {
lab=Vss}
N 620 -180 620 -120 {
lab=Vss}
N 540 -120 620 -120 {
lab=Vss}
N 400 -180 500 -180 {
lab=Vbn}
N 540 -290 720 -290 {
lab=Vo}
N 700 -360 780 -360 {
lab=Vdd}
N 780 -410 780 -360 {
lab=Vdd}
N 700 -410 780 -410 {
lab=Vdd}
N 700 -410 700 -390 {
lab=Vdd}
N 700 -450 700 -410 {
lab=Vdd}
N 620 -450 700 -450 {
lab=Vdd}
N 480 -360 660 -360 {
lab=Vi}
N 480 -400 480 -360 {
lab=Vi}
N 700 -330 700 -290 {
lab=Vo}
N 700 -220 780 -220 {
lab=Vss}
N 780 -220 780 -160 {
lab=Vss}
N 700 -160 780 -160 {
lab=Vss}
N 700 -190 700 -160 {
lab=Vss}
N 700 -160 700 -120 {
lab=Vss}
N 620 -120 700 -120 {
lab=Vss}
N 480 -220 660 -220 {
lab=Vbn}
N 480 -220 480 -180 {
lab=Vbn}
N 700 -290 700 -250 {
lab=Vo}
C {sky130_fd_pr/pfet_01v8.sym} 520 -400 0 0 {name=M1
L=1
W=8
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
C {sky130_fd_pr/nfet_01v8.sym} 520 -180 0 0 {name=M2
L=2
W=10
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
C {devices/ipin.sym} 400 -180 0 0 {name=p5 lab=Vbn}
C {devices/ipin.sym} 400 -400 0 0 {name=p3 lab=Vi}
C {devices/iopin.sym} 540 -470 3 0 {name=p1 lab=Vdd}
C {devices/iopin.sym} 540 -90 3 1 {name=p2 lab=Vss}
C {devices/opin.sym} 720 -290 0 0 {name=p7 lab=Vo}
C {devices/title.sym} 160 0 0 0 {name=l1 author="Jakob Ratschenberger"}
C {sky130_fd_pr/pfet_01v8.sym} 680 -360 0 0 {name=M3
L=1
W=8
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
C {sky130_fd_pr/nfet_01v8.sym} 680 -220 0 0 {name=M4
L=2
W=10
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
