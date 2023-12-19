v {xschem version=3.4.1 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 440 -260 440 -220 {
lab=Vmid}
N 440 -220 680 -220 {
lab=Vmid}
N 680 -260 680 -220 {
lab=Vmid}
N 440 -290 680 -290 {
lab=Vss}
N 440 -440 440 -320 {
lab=outn}
N 680 -440 680 -320 {
lab=out}
N 360 -290 400 -290 {
lab=in}
N 720 -290 760 -290 {
lab=inn}
N 560 -220 560 -180 {
lab=Vmid}
N 440 -540 440 -500 {
lab=Vdd}
N 440 -540 680 -540 {
lab=Vdd}
N 680 -540 680 -500 {
lab=Vdd}
N 360 -470 440 -470 {
lab=Vdd}
N 360 -540 360 -470 {
lab=Vdd}
N 360 -540 440 -540 {
lab=Vdd}
N 680 -470 760 -470 {
lab=Vdd}
N 760 -540 760 -470 {
lab=Vdd}
N 680 -540 760 -540 {
lab=Vdd}
N 560 -560 560 -540 {
lab=Vdd}
N 440 -150 520 -150 {
lab=clk}
N 560 -120 560 -80 {
lab=Vss}
N 440 -360 500 -360 {
lab=outn}
N 620 -360 680 -360 {
lab=out}
N 560 -150 650 -150 {
lab=Vss}
N 650 -150 650 -100 {
lab=Vss}
N 560 -100 650 -100 {
lab=Vss}
N 480 -470 510 -470 {
lab=out}
N 510 -470 610 -400 {
lab=out}
N 610 -400 680 -400 {
lab=out}
N 610 -470 640 -470 {
lab=outn}
N 510 -400 610 -470 {
lab=outn}
N 440 -400 510 -400 {
lab=outn}
C {sky130_fd_pr/nfet_01v8.sym} 420 -290 0 0 {name=M1
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
C {sky130_fd_pr/nfet_01v8.sym} 700 -290 0 1 {name=M2
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
C {sky130_fd_pr/pfet_01v8.sym} 460 -470 0 1 {name=M3
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
model=pfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/pfet_01v8.sym} 660 -470 0 0 {name=M4
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
model=pfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8.sym} 540 -150 0 0 {name=M5
L=1
W=6
nf=2 
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
C {devices/iopin.sym} 560 -560 3 0 {name=p1 lab=Vdd}
C {devices/iopin.sym} 560 -80 3 1 {name=p2 lab=Vss}
C {devices/ipin.sym} 360 -290 0 0 {name=p3 lab=in}
C {devices/ipin.sym} 760 -290 0 1 {name=p4 lab=inn}
C {devices/ipin.sym} 440 -150 0 0 {name=p5 lab=clk}
C {devices/opin.sym} 500 -360 0 0 {name=p7 lab=outn}
C {devices/opin.sym} 620 -360 0 1 {name=p8 lab=out}
C {devices/lab_wire.sym} 560 -220 0 0 {name=p9 sig_type=std_logic lab=vmid}
C {devices/lab_wire.sym} 560 -290 0 0 {name=p10 sig_type=std_logic lab=Vss}
C {devices/title.sym} 160 0 0 0 {name=l1 author="Jakob Ratschenberger"}
