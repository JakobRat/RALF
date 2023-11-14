v {xschem version=3.4.1 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 260 -480 270 -480 {
lab=VPWR}
N 430 -480 440 -480 {
lab=VPWR}
N 430 -520 430 -510 {
lab=VPWR}
N 270 -520 270 -510 {
lab=VPWR}
N 270 -560 270 -520 {
lab=VPWR}
N 270 -560 430 -560 {
lab=VPWR}
N 430 -560 430 -520 {
lab=VPWR}
N 270 -290 430 -290 {
lab=VPWR}
N 350 -560 350 -290 {
lab=VPWR}
N 430 -450 430 -320 {
lab=in_stage_net3}
N 270 -450 270 -320 {
lab=in_stage_net2}
N 270 -260 270 -250 {
lab=outn}
N 270 -250 270 -230 {
lab=outn}
N 270 -230 320 -230 {
lab=outn}
N 320 -230 380 -270 {
lab=outn}
N 380 -480 380 -270 {
lab=outn}
N 380 -480 390 -480 {
lab=outn}
N 430 -260 430 -230 {
lab=outp}
N 380 -230 430 -230 {
lab=outp}
N 320 -270 380 -230 {
lab=outp}
N 320 -480 320 -270 {
lab=outp}
N 310 -480 320 -480 {
lab=outp}
N 490 -420 490 -290 {
lab=inp}
N 470 -290 490 -290 {
lab=inp}
N 220 -290 230 -290 {
lab=inn}
N 220 -400 220 -290 {
lab=inn}
N 110 -100 120 -100 {
lab=VGND}
N 120 -100 270 -100 {
lab=VGND}
N 430 -100 590 -100 {
lab=VGND}
N 270 -230 270 -140 {
lab=outn}
N 430 -230 430 -140 {
lab=outp}
N 430 -230 590 -230 {
lab=outp}
N 590 -230 590 -140 {
lab=outp}
N 110 -230 270 -230 {
lab=outn}
N 110 -230 110 -140 {
lab=outn}
N 310 -100 340 -100 {
lab=outp}
N 340 -130 340 -100 {
lab=outp}
N 370 -100 390 -100 {
lab=outn}
N 370 -130 370 -100 {
lab=outn}
N 340 -130 370 -150 {
lab=outp}
N 370 -150 430 -150 {
lab=outp}
N 340 -150 370 -130 {
lab=outn}
N 270 -150 340 -150 {
lab=outn}
N 100 0 110 0 {
lab=VGND}
N 110 0 270 0 {
lab=VGND}
N 270 0 430 0 {
lab=VGND}
N 430 -80 430 0 {
lab=VGND}
N 430 0 590 0 {
lab=VGND}
N 590 -80 590 0 {
lab=VGND}
N 590 -140 590 -130 {
lab=outp}
N 430 -140 430 -130 {
lab=outp}
N 270 -140 270 -130 {
lab=outn}
N 270 -170 750 -170 {
lab=outn}
N 590 -300 590 -230 {
lab=outp}
N 590 -440 750 -440 {
lab=outp}
N 190 -100 190 0 {
lab=VGND}
N 520 -100 520 0 {
lab=VGND}
N 110 -70 110 0 {
lab=VGND}
N 270 -70 270 0 {
lab=VGND}
N 110 -140 110 -130 {
lab=outn}
N 750 -440 770 -440 {
lab=outp}
N 590 -440 590 -300 {
lab=outp}
N 750 -170 770 -170 {
lab=outn}
N 260 -560 260 -480 {
lab=VPWR}
N 440 -560 440 -480 {
lab=VPWR}
N 60 -100 70 -100 {
lab=nclk}
N 630 -100 640 -100 {
lab=nclk}
N 430 -560 440 -560 {
lab=VPWR}
N 220 -420 490 -420 {
lab=inp}
N 210 -400 220 -400 {
lab=inn}
N 0 -560 270 -560 {
lab=VPWR}
N -0 -0 100 0 {
lab=VGND}
N 110 -420 220 -420 {
lab=inp}
N 110 -400 210 -400 {
lab=inn}
C {devices/opin.sym} 770 -440 0 0 {name=p7 lab=outp}
C {devices/opin.sym} 770 -170 0 0 {name=p8 lab=outn}
C {sky130_fd_pr/pfet_01v8.sym} 290 -480 0 1 {name=M6
L=0.3
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
C {sky130_fd_pr/pfet_01v8.sym} 410 -480 0 0 {name=M7
L=0.3
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
C {sky130_fd_pr/pfet_01v8.sym} 250 -290 0 0 {name=M8
L=0.3
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
C {sky130_fd_pr/pfet_01v8.sym} 450 -290 0 1 {name=M9
L=0.3
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
C {sky130_fd_pr/nfet_01v8.sym} 290 -100 0 1 {name=M10
L=0.3
W=2
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
C {sky130_fd_pr/nfet_01v8.sym} 90 -100 0 0 {name=M11
L=0.3
W=2
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
C {sky130_fd_pr/nfet_01v8.sym} 610 -100 0 1 {name=M12
L=0.3
W=2
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
C {sky130_fd_pr/nfet_01v8.sym} 410 -100 0 0 {name=M13
L=0.3
W=2
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
C {devices/lab_wire.sym} 270 -440 1 1 {name=l7 sig_type=std_logic lab=in_stage_net2}
C {devices/lab_wire.sym} 430 -440 3 0 {name=l8 sig_type=std_logic lab=in_stage_net3}
C {devices/lab_wire.sym} 60 -100 0 0 {name=l14 sig_type=std_logic lab=nclk}
C {devices/lab_wire.sym} 640 -100 0 1 {name=l15 sig_type=std_logic lab=nclk}
C {devices/iopin.sym} 0 -560 0 1 {name=p1 lab=VPWR}
C {devices/ipin.sym} 0 -600 0 0 {name=p6 lab=nclk}
C {devices/iopin.sym} 0 0 0 1 {name=p2 lab=VGND}
C {devices/ipin.sym} 110 -420 0 0 {name=p3 lab=inp}
C {devices/ipin.sym} 110 -400 0 0 {name=p4 lab=inn}
