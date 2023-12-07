v {xschem version=3.4.1 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 40 -50 40 0 {
lab=Vss}
N 40 -80 110 -80 {
lab=Vss}
N 110 -80 110 -20 {
lab=Vss}
N 40 -20 110 -20 {
lab=Vss}
N 40 -160 40 -110 {
lab=Vbias}
N -70 -80 0 -80 {
lab=Vbias}
N -70 -140 -70 -80 {
lab=Vbias}
N -70 -140 40 -140 {
lab=Vbias}
N 40 -520 40 -460 {
lab=Vdd}
N 40 -400 40 -370 {
lab=VbiasP}
N -20 -430 0 -430 {
lab=VbiasP}
N -20 -430 -20 -380 {
lab=VbiasP}
N -20 -380 40 -380 {
lab=VbiasP}
N 40 -430 80 -430 {
lab=Vdd}
N 80 -490 80 -430 {
lab=Vdd}
N 40 -490 80 -490 {
lab=Vdd}
N 40 -310 40 -270 {
lab=VbiasP}
N 40 -210 40 -160 {
lab=Vbias}
N 40 -370 40 -310 {
lab=VbiasP}
N 210 -330 230 -330 {
lab=#net1}
N 290 -330 320 -330 {
lab=#net2}
N 380 -330 400 -330 {
lab=#net3}
N 460 -330 480 -330 {
lab=#net4}
N 540 -330 580 -330 {
lab=Vbias}
N 120 -330 150 -330 {
lab=VbiasP}
N 180 -380 180 -350 {
lab=Vss}
N 180 -380 510 -380 {
lab=Vss}
N 510 -380 510 -350 {
lab=Vss}
N 430 -380 430 -350 {
lab=Vss}
N 350 -380 350 -350 {
lab=Vss}
N 260 -380 260 -350 {
lab=Vss}
N 350 -400 350 -380 {
lab=Vss}
N 40 -170 240 -170 {
lab=Vbias}
C {sky130_fd_pr/nfet_01v8.sym} 20 -80 0 0 {name=M6
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
C {devices/lab_wire.sym} 40 -210 0 0 {name=p5 sig_type=std_logic lab=Vbias}
C {sky130_fd_pr/pfet_01v8.sym} 20 -430 0 0 {name=M2
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
model=pfet_01v8
spiceprefix=X
}
C {devices/lab_wire.sym} 40 -270 0 0 {name=p18 sig_type=std_logic lab=VbiasP}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 180 -330 1 0 {name=R1
L=2
model=res_xhigh_po_0p35
spiceprefix=X
mult=1}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 260 -330 1 0 {name=R2
L=2
model=res_xhigh_po_0p35
spiceprefix=X
mult=1}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 350 -330 1 0 {name=R3
L=2
model=res_xhigh_po_0p35
spiceprefix=X
mult=1}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 430 -330 1 0 {name=R4
L=2
model=res_xhigh_po_0p35
spiceprefix=X
mult=1}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 510 -330 1 0 {name=R5
L=2
model=res_xhigh_po_0p35
spiceprefix=X
mult=1}
C {devices/lab_wire.sym} 120 -330 0 0 {name=p10 sig_type=std_logic lab=VbiasP}
C {devices/lab_wire.sym} 580 -330 0 1 {name=p19 sig_type=std_logic lab=Vbias}
C {devices/opin.sym} 240 -170 0 0 {name=p1 sig_type=std_logic lab=Vbias}
C {devices/iopin.sym} 40 0 1 0 {name=p2 lab=Vss}
C {devices/iopin.sym} 40 -520 3 0 {name=p3 lab=Vdd}
C {devices/lab_wire.sym} 350 -400 0 1 {name=p4 sig_type=std_logic lab=Vss}
