v {xschem version=3.4.1 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 260 -450 260 -320 {
lab=outn}
N 400 -450 400 -320 {
lab=outp}
N 250 -480 260 -480 {
lab=VPWR}
N 400 -480 410 -480 {
lab=VPWR}
N 400 -520 400 -510 {
lab=VPWR}
N 260 -520 260 -510 {
lab=VPWR}
N 310 -480 360 -480 {
lab=clk}
N 260 -290 400 -290 {
lab=VGND}
N 320 -130 330 -130 {
lab=VGND}
N 330 -290 330 -130 {
lab=VGND}
N 320 -100 320 -90 {
lab=VGND}
N 320 -90 320 0 {
lab=VGND}
N 260 -260 260 -220 {
lab=in_stage_net1}
N 400 -260 400 -220 {
lab=in_stage_net1}
N 0 0 320 0 {
lab=VGND}
N 0 -560 260 -560 {
lab=VPWR}
N 260 -560 260 -520 {
lab=VPWR}
N 260 -560 400 -560 {
lab=VPWR}
N 400 -560 400 -520 {
lab=VPWR}
N 0 -380 440 -380 {
lab=inn}
N 440 -380 440 -290 {
lab=inn}
N 300 -480 310 -480 {
lab=clk}
N 200 -290 220 -290 {
lab=inp}
N 200 -350 200 -290 {
lab=inp}
N 0 -350 200 -350 {
lab=inp}
N 190 -290 200 -290 {
lab=inp}
N 260 -220 400 -220 {
lab=in_stage_net1}
N 320 -220 320 -160 {
lab=in_stage_net1}
N 260 -130 280 -130 {
lab=clk}
N 220 -130 260 -130 {
lab=clk}
N 410 -560 410 -480 {
lab=VPWR}
N 250 -560 250 -480 {
lab=VPWR}
N 330 -130 330 0 {
lab=VGND}
N 260 -410 600 -410 {
lab=outn}
N 400 -390 600 -390 {
lab=outp}
N 320 0 330 0 {
lab=VGND}
N 400 -560 410 -560 {
lab=VPWR}
C {devices/iopin.sym} 0 -560 0 1 {name=p1 lab=VPWR}
C {devices/iopin.sym} 0 0 0 1 {name=p2 lab=VGND}
C {devices/ipin.sym} 0 -620 0 0 {name=p5 lab=clk}
C {devices/ipin.sym} 0 -350 0 0 {name=p3 lab=inp}
C {devices/ipin.sym} 0 -380 0 0 {name=p4 lab=inn}
C {sky130_fd_pr/nfet_01v8.sym} 240 -290 0 0 {name=M3
L=0.3
W=8
nf=4 
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
C {sky130_fd_pr/nfet_01v8.sym} 420 -290 0 1 {name=M4
L=0.3
W=8
nf=4 
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
C {sky130_fd_pr/nfet_01v8.sym} 300 -130 0 0 {name=M5
L=0.3
W=4
nf=8
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
C {sky130_fd_pr/pfet_01v8.sym} 380 -480 0 0 {name=M2
L=0.3
W=2
nf=4
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
C {sky130_fd_pr/pfet_01v8.sym} 280 -480 0 1 {name=M1
L=0.3
W=2
nf=4
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
C {devices/lab_wire.sym} 400 -240 2 0 {name=l6 sig_type=std_logic lab=in_stage_net1}
C {devices/lab_wire.sym} 330 -480 0 0 {name=l9 sig_type=std_logic lab=clk}
C {devices/lab_wire.sym} 270 -130 0 0 {name=l10 sig_type=std_logic lab=clk}
C {devices/opin.sym} 600 -410 0 0 {name=p7 lab=outn}
C {devices/opin.sym} 600 -390 0 0 {name=p8 lab=outp}
