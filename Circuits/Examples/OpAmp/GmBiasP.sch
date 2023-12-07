v {xschem version=3.4.1 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 410 -120 410 40 {
lab=Vss}
N 410 -150 480 -150 {
lab=Vss}
N 480 -150 480 -90 {
lab=Vss}
N 410 -90 480 -90 {
lab=Vss}
N 410 -230 410 -180 {
lab=#net1}
N 340 -150 370 -150 {
lab=#net1}
N 340 -210 340 -150 {
lab=#net1}
N 340 -210 410 -210 {
lab=#net1}
N 230 -690 230 -530 {
lab=Vdd}
N 230 -470 230 -440 {
lab=Vbias}
N 270 -500 290 -500 {
lab=Vbias}
N 290 -500 290 -450 {
lab=Vbias}
N 230 -450 290 -450 {
lab=Vbias}
N 190 -500 230 -500 {
lab=Vdd}
N 190 -660 190 -500 {
lab=Vdd}
N 190 -660 230 -660 {
lab=Vdd}
N 230 -380 230 -340 {
lab=Vbias}
N 410 -280 410 -230 {
lab=#net1}
N 230 -440 230 -380 {
lab=Vbias}
N 230 -660 410 -660 {
lab=Vdd}
N 410 -500 480 -500 {
lab=Vdd}
N 480 -660 480 -500 {
lab=Vdd}
N 410 -660 480 -660 {
lab=Vdd}
N 290 -500 370 -500 {
lab=Vbias}
N 270 -150 340 -150 {
lab=#net1}
N 230 -120 230 -90 {
lab=Vss}
N 230 -340 230 -180 {
lab=Vbias}
N 410 -470 410 -280 {
lab=#net1}
N 230 -30 230 0 {
lab=Vss}
N 230 0 410 0 {
lab=Vss}
N 150 -150 230 -150 {
lab=Vss}
N 310 -300 310 -150 {
lab=#net1}
N 260 -330 270 -330 {
lab=Vbias}
N 260 -390 260 -330 {
lab=Vbias}
N 260 -390 310 -390 {
lab=Vbias}
N 310 -390 310 -360 {
lab=Vbias}
N 310 -500 310 -390 {
lab=Vbias}
N 310 -330 370 -330 {
lab=Vss}
N 190 -330 230 -330 {
lab=Vbias}
N 410 -660 410 -630 {
lab=Vdd}
N 410 -570 410 -530 {
lab=#net2}
N 230 -90 230 -30 {
lab=Vss}
N 430 -600 450 -600 {
lab=Vss}
C {sky130_fd_pr/nfet_01v8.sym} 390 -150 0 0 {name=M6
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
C {sky130_fd_pr/pfet_01v8.sym} 250 -500 0 1 {name=M2
L=1
W=16
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
C {devices/iopin.sym} 410 40 1 0 {name=p2 lab=Vss}
C {devices/iopin.sym} 230 -690 3 0 {name=p3 lab=Vdd}
C {sky130_fd_pr/pfet_01v8.sym} 390 -500 0 0 {name=M1
L=1
W=16
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
C {sky130_fd_pr/nfet_01v8.sym} 250 -150 0 1 {name=M3
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
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 410 -600 0 1 {name=R6
L=1
model=res_xhigh_po_0p35
spiceprefix=X
mult=1}
C {devices/lab_wire.sym} 150 -150 0 0 {name=p6 sig_type=std_logic lab=Vss}
C {sky130_fd_pr/nfet_01v8.sym} 290 -330 0 0 {name=M4
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
C {devices/lab_wire.sym} 370 -330 0 1 {name=p4 sig_type=std_logic lab=Vss}
C {devices/opin.sym} 190 -330 0 1 {name=p8 sig_type=std_logic lab=Vbias}
C {devices/lab_wire.sym} 450 -600 0 1 {name=p7 sig_type=std_logic lab=Vss}
