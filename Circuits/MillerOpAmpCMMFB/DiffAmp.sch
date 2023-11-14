v {xschem version=3.4.1 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 380 -380 380 -300 {
lab=Vmid}
N 380 -300 620 -300 {
lab=Vmid}
N 620 -380 620 -300 {
lab=Vmid}
N 380 -410 620 -410 {
lab=Vss}
N 380 -600 380 -440 {
lab=Vop}
N 620 -600 620 -440 {
lab=Von}
N 260 -410 340 -410 {
lab=Vp}
N 660 -410 740 -410 {
lab=Vn}
N 500 -300 500 -240 {
lab=Vmid}
N 380 -770 380 -660 {
lab=Vdd}
N 380 -770 620 -770 {
lab=Vdd}
N 620 -770 620 -660 {
lab=Vdd}
N 420 -630 580 -630 {
lab=Vbias2}
N 500 -660 500 -630 {
lab=Vbias2}
N 300 -630 380 -630 {
lab=Vdd}
N 300 -770 300 -630 {
lab=Vdd}
N 300 -770 380 -770 {
lab=Vdd}
N 620 -630 700 -630 {
lab=Vdd}
N 700 -770 700 -630 {
lab=Vdd}
N 620 -770 700 -770 {
lab=Vdd}
N 500 -810 500 -770 {
lab=Vdd}
N 380 -210 460 -210 {
lab=Vbias1}
N 500 -180 500 -140 {
lab=Vss}
N 380 -520 440 -520 {
lab=Vop}
N 560 -520 620 -520 {
lab=Von}
N 500 -210 590 -210 {
lab=Vss}
N 590 -210 590 -160 {
lab=Vss}
N 500 -160 590 -160 {
lab=Vss}
C {sky130_fd_pr/nfet_01v8.sym} 360 -410 0 0 {name=M1
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
C {sky130_fd_pr/nfet_01v8.sym} 640 -410 0 1 {name=M2
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
C {sky130_fd_pr/pfet_01v8.sym} 400 -630 0 1 {name=M3
L=1
W=2
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
C {sky130_fd_pr/pfet_01v8.sym} 600 -630 0 0 {name=M4
L=1
W=2
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
C {sky130_fd_pr/nfet_01v8.sym} 480 -210 0 0 {name=M5
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
C {devices/iopin.sym} 500 -810 3 0 {name=p1 lab=Vdd}
C {devices/iopin.sym} 500 -140 3 1 {name=p2 lab=Vss}
C {devices/ipin.sym} 260 -410 0 0 {name=p3 lab=Vp}
C {devices/ipin.sym} 740 -410 0 1 {name=p4 lab=Vn}
C {devices/ipin.sym} 380 -210 0 0 {name=p5 lab=Vbias1}
C {devices/ipin.sym} 500 -660 1 0 {name=p6 lab=Vbias2}
C {devices/opin.sym} 440 -520 0 0 {name=p7 lab=Vop}
C {devices/opin.sym} 560 -520 0 1 {name=p8 lab=Von}
C {devices/lab_wire.sym} 500 -300 0 0 {name=p9 sig_type=std_logic lab=Vmid}
C {devices/lab_wire.sym} 500 -410 0 0 {name=p10 sig_type=std_logic lab=Vss}
