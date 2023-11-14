v {xschem version=3.4.1 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 70 -240 70 -100 {
lab=Vbias}
N 70 -130 140 -130 {
lab=Vbias}
N 140 -130 140 -70 {
lab=Vbias}
N 70 -40 70 0 {
lab=Vss}
N 70 -260 70 -240 {
lab=Vbias}
N 70 -340 70 -320 {
lab=Vdd}
N 0 -70 70 -70 {
lab=Vss}
N 0 -70 0 0 {
lab=Vss}
N 0 0 70 0 {
lab=Vss}
N 110 -70 140 -70 {
lab=Vbias}
N 140 -70 190 -70 {
lab=Vbias}
N 90 -290 140 -290 {
lab=Vss}
N 510 -370 570 -370 {
lab=#net1}
N 470 -430 470 -400 {
lab=Vdd}
N 610 -430 610 -400 {
lab=Vdd}
N 470 -340 470 -290 {
lab=#net1}
N 610 -340 610 -290 {
lab=#net2}
N 470 -430 610 -430 {
lab=Vdd}
N 540 -370 540 -320 {
lab=#net1}
N 470 -320 540 -320 {
lab=#net1}
N 540 -450 540 -430 {
lab=Vdd}
N 390 -370 470 -370 {
lab=Vdd}
N 390 -430 390 -370 {
lab=Vdd}
N 390 -430 470 -430 {
lab=Vdd}
N 610 -370 680 -370 {
lab=Vdd}
N 680 -430 680 -370 {
lab=Vdd}
N 610 -430 680 -430 {
lab=Vdd}
N 440 -120 660 -120 {
lab=Vss}
N 440 -90 440 -50 {
lab=#net3}
N 440 -50 540 -50 {
lab=#net3}
N 540 -50 660 -50 {
lab=#net3}
N 660 -90 660 -50 {
lab=#net3}
N 370 -120 400 -120 {
lab=Vn}
N 700 -120 720 -120 {
lab=Vp}
N 440 -200 440 -150 {
lab=#net1}
N 660 -200 660 -150 {
lab=#net2}
N 550 -160 550 -120 {
lab=Vss}
N 540 -50 540 -20 {
lab=#net3}
N 1080 -340 1080 -320 {
lab=Vdd}
N 1080 -320 1080 -270 {
lab=Vdd}
N 1080 -210 1080 -140 {
lab=Vout}
N 1080 -140 1080 -100 {
lab=Vout}
N 1080 -40 1080 0 {
lab=Vss}
N 1000 -70 1060 -70 {
lab=Vss}
N 1000 -70 1000 0 {
lab=Vss}
N 1080 -160 1120 -160 {
lab=Vout}
N 1080 -240 1160 -240 {
lab=Vdd}
N 1160 -340 1160 -240 {
lab=Vdd}
N 1080 -340 1160 -340 {
lab=Vdd}
N 880 -240 1040 -240 {
lab=#net2}
N 1000 0 1080 0 {
lab=Vss}
N 1080 -370 1080 -340 {
lab=Vdd}
N 940 -240 940 -210 {
lab=#net2}
N 940 -150 940 -130 {
lab=Vout}
N 940 -130 1080 -130 {
lab=Vout}
N 190 -70 270 -70 {
lab=Vbias}
N 270 -70 270 80 {
lab=Vbias}
N 270 80 500 80 {
lab=Vbias}
N 540 -20 540 50 {
lab=#net3}
N 540 110 540 140 {
lab=Vss}
N -0 140 540 140 {
lab=Vss}
N 540 140 1080 140 {
lab=Vss}
N 1080 -0 1080 140 {
lab=Vss}
N 440 -290 440 -200 {
lab=#net1}
N 440 -290 470 -290 {
lab=#net1}
N 610 -290 660 -290 {
lab=#net2}
N 660 -240 880 -240 {
lab=#net2}
N 660 -290 660 -200 {
lab=#net2}
N 70 -430 70 -340 {
lab=Vdd}
N 70 -430 390 -430 {
lab=Vdd}
N 680 -430 1080 -430 {
lab=Vdd}
N 1080 -430 1080 -370 {
lab=Vdd}
N 70 0 70 140 {
lab=Vss}
N 540 80 640 80 {
lab=Vss}
N 640 80 640 140 {
lab=Vss}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 70 -290 0 1 {name=R3
L=0.35
model=res_xhigh_po_0p35
spiceprefix=X
mult=1}
C {sky130_fd_pr/nfet_01v8.sym} 90 -70 0 1 {name=M4
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
C {devices/iopin.sym} 0 140 0 1 {name=p2 sig_type=std_logic lab=Vss}
C {devices/lab_wire.sym} 140 -290 0 1 {name=p3 sig_type=std_logic lab=Vss}
C {sky130_fd_pr/pfet_01v8.sym} 490 -370 0 1 {name=M1
L=1
W=5
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
C {sky130_fd_pr/pfet_01v8.sym} 590 -370 0 0 {name=M2
L=1
W=5
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
C {sky130_fd_pr/nfet_01v8.sym} 420 -120 0 0 {name=M3
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
C {sky130_fd_pr/nfet_01v8.sym} 680 -120 0 1 {name=M5
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
C {devices/ipin.sym} 370 -120 0 0 {name=p8 sig_type=std_logic lab=Vn}
C {devices/ipin.sym} 720 -120 0 1 {name=p9 sig_type=std_logic lab=Vp}
C {sky130_fd_pr/nfet_01v8.sym} 520 80 0 0 {name=M6
L=1
W=12
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
C {sky130_fd_pr/pfet_01v8.sym} 1060 -240 0 0 {name=M7
L=2
W=20
nf=10
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
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 1080 -70 0 0 {name=R4
L=20
model=res_xhigh_po_0p35
spiceprefix=X
mult=1}
C {devices/opin.sym} 1120 -160 2 1 {name=p14 sig_type=std_logic lab=Vout}
C {devices/iopin.sym} 540 -450 1 1 {name=p16 sig_type=std_logic lab=Vdd}
C {sky130_fd_pr/cap_mim_m3_1.sym} 940 -180 0 0 {name=C1 model=cap_mim_m3_1 W=10 L=10 MF=1 spiceprefix=X}
C {devices/lab_wire.sym} 550 -160 0 1 {name=p1 sig_type=std_logic lab=Vss}
C {devices/lab_wire.sym} 270 -70 0 1 {name=p4 sig_type=std_logic lab=Vbias}
C {devices/lab_wire.sym} 540 -50 0 1 {name=p5 sig_type=std_logic lab=Vmid}
C {devices/lab_wire.sym} 440 -220 0 1 {name=p6 sig_type=std_logic lab=Vo_p}
C {devices/lab_wire.sym} 660 -260 0 1 {name=p7 sig_type=std_logic lab=Vo_n}
