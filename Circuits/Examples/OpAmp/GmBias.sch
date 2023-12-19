v {xschem version=3.4.1 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 700 -280 770 -280 {
lab=Vss}
N 770 -280 770 -220 {
lab=Vss}
N 700 -220 770 -220 {
lab=Vss}
N 700 -360 700 -310 {
lab=Vbias}
N 630 -280 660 -280 {
lab=Vbias}
N 630 -340 630 -280 {
lab=Vbias}
N 630 -340 700 -340 {
lab=Vbias}
N 500 -500 500 -470 {
lab=#net1}
N 540 -530 560 -530 {
lab=#net1}
N 560 -530 560 -480 {
lab=#net1}
N 500 -480 560 -480 {
lab=#net1}
N 460 -530 500 -530 {
lab=Vdd}
N 460 -590 460 -530 {
lab=Vdd}
N 460 -590 500 -590 {
lab=Vdd}
N 500 -440 500 -400 {
lab=#net1}
N 700 -360 700 -340 {
lab=Vbias}
N 500 -470 500 -440 {
lab=#net1}
N 700 -370 780 -370 {
lab=Vbias}
N 500 -590 700 -590 {
lab=Vdd}
N 700 -590 700 -560 {
lab=Vdd}
N 700 -530 770 -530 {
lab=Vdd}
N 770 -590 770 -530 {
lab=Vdd}
N 700 -590 770 -590 {
lab=Vdd}
N 560 -530 660 -530 {
lab=#net1}
N 540 -280 630 -280 {
lab=Vbias}
N 500 -250 500 -220 {
lab=#net2}
N 500 -400 500 -310 {
lab=#net1}
N 700 -500 700 -340 {
lab=Vbias}
N 500 -160 500 -130 {
lab=Vss}
N 500 -130 700 -130 {
lab=Vss}
N 420 -280 500 -280 {
lab=Vss}
N 580 -360 580 -280 {
lab=Vbias}
N 530 -390 540 -390 {
lab=#net1}
N 530 -450 530 -390 {
lab=#net1}
N 530 -450 580 -450 {
lab=#net1}
N 580 -450 580 -420 {
lab=#net1}
N 580 -530 580 -450 {
lab=#net1}
N 580 -390 650 -390 {
lab=Vss}
N 440 -190 480 -190 {
lab=Vss}
N 500 -590 500 -560 {
lab=Vdd}
N 600 -630 600 -590 {
lab=Vdd}
N 700 -250 700 -220 {
lab=Vss}
N 700 -220 700 -130 {
lab=Vss}
N 600 -130 600 -90 {
lab=Vss}
C {sky130_fd_pr/nfet_01v8.sym} 680 -280 0 0 {name=M6
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
C {sky130_fd_pr/pfet_01v8.sym} 520 -530 0 1 {name=M2
L=1
W=4
nf=2
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
C {devices/opin.sym} 780 -370 0 0 {name=p1 sig_type=std_logic lab=Vbias}
C {devices/iopin.sym} 600 -90 1 0 {name=p2 lab=Vss}
C {devices/iopin.sym} 600 -630 3 0 {name=p3 lab=Vdd}
C {sky130_fd_pr/pfet_01v8.sym} 680 -530 0 0 {name=M1
L=1
W=4
nf=2
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
C {sky130_fd_pr/nfet_01v8.sym} 520 -280 0 1 {name=M3
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
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 500 -190 0 0 {name=R6
L=1
model=res_xhigh_po_0p35
spiceprefix=X
mult=1}
C {devices/lab_wire.sym} 420 -280 0 0 {name=p6 sig_type=std_logic lab=Vss}
C {sky130_fd_pr/nfet_01v8.sym} 560 -390 0 0 {name=M4
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
C {devices/lab_wire.sym} 650 -390 0 1 {name=p4 sig_type=std_logic lab=Vss}
C {devices/lab_wire.sym} 440 -190 0 0 {name=p7 sig_type=std_logic lab=Vss}
C {devices/title.sym} 160 0 0 0 {name=l1 author="Jakob Ratschenberger"}
C {devices/lab_wire.sym} 500 -340 0 0 {name=p5 sig_type=std_logic lab=v1}
