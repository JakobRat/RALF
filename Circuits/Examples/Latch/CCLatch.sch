v {xschem version=3.4.1 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 440 -320 440 -240 {
lab=Vmid}
N 440 -240 680 -240 {
lab=Vmid}
N 680 -320 680 -240 {
lab=Vmid}
N 440 -350 680 -350 {
lab=Vss}
N 440 -540 440 -380 {
lab=outn}
N 680 -540 680 -380 {
lab=out}
N 320 -350 400 -350 {
lab=in}
N 720 -350 800 -350 {
lab=inn}
N 560 -240 560 -180 {
lab=Vmid}
N 440 -710 440 -600 {
lab=Vdd}
N 440 -710 680 -710 {
lab=Vdd}
N 680 -710 680 -600 {
lab=Vdd}
N 360 -570 440 -570 {
lab=Vdd}
N 360 -710 360 -570 {
lab=Vdd}
N 360 -710 440 -710 {
lab=Vdd}
N 680 -570 760 -570 {
lab=Vdd}
N 760 -710 760 -570 {
lab=Vdd}
N 680 -710 760 -710 {
lab=Vdd}
N 560 -750 560 -710 {
lab=Vdd}
N 440 -150 520 -150 {
lab=clk}
N 560 -120 560 -80 {
lab=Vss}
N 440 -460 500 -460 {
lab=outn}
N 620 -460 680 -460 {
lab=out}
N 560 -150 650 -150 {
lab=Vss}
N 650 -150 650 -100 {
lab=Vss}
N 560 -100 650 -100 {
lab=Vss}
N 480 -570 510 -570 {
lab=out}
N 510 -570 610 -500 {
lab=out}
N 610 -500 680 -500 {
lab=out}
N 610 -570 640 -570 {
lab=outn}
N 510 -500 610 -570 {
lab=outn}
N 440 -500 510 -500 {
lab=outn}
C {sky130_fd_pr/nfet_01v8.sym} 420 -350 0 0 {name=M1
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
C {sky130_fd_pr/nfet_01v8.sym} 700 -350 0 1 {name=M2
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
C {sky130_fd_pr/pfet_01v8.sym} 460 -570 0 1 {name=M3
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
C {sky130_fd_pr/pfet_01v8.sym} 660 -570 0 0 {name=M4
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
C {devices/iopin.sym} 560 -750 3 0 {name=p1 lab=Vdd}
C {devices/iopin.sym} 560 -80 3 1 {name=p2 lab=Vss}
C {devices/ipin.sym} 320 -350 0 0 {name=p3 lab=in}
C {devices/ipin.sym} 800 -350 0 1 {name=p4 lab=inn}
C {devices/ipin.sym} 440 -150 0 0 {name=p5 lab=clk}
C {devices/opin.sym} 500 -460 0 0 {name=p7 lab=outn}
C {devices/opin.sym} 620 -460 0 1 {name=p8 lab=out}
C {devices/lab_wire.sym} 560 -240 0 0 {name=p9 sig_type=std_logic lab=vmid}
C {devices/lab_wire.sym} 560 -350 0 0 {name=p10 sig_type=std_logic lab=Vss}
C {devices/title.sym} 160 0 0 0 {name=l1 author="Jakob Ratschenberger"}
