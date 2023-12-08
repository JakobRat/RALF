v {xschem version=3.4.1 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 440 -460 540 -460 {
lab=vp}
N 600 -460 640 -460 {
lab=v1}
N 700 -460 860 -460 {
lab=Von}
N 860 -460 860 -340 {
lab=Von}
N 600 -180 640 -180 {
lab=v2}
N 360 -260 440 -260 {
lab=vn}
N 440 -260 440 -180 {
lab=vn}
N 440 -180 540 -180 {
lab=vn}
N 440 -300 500 -300 {
lab=vn}
N 440 -300 440 -260 {
lab=vn}
N 360 -360 440 -360 {
lab=vp}
N 440 -360 440 -320 {
lab=vp}
N 440 -320 500 -320 {
lab=vp}
N 440 -460 440 -360 {
lab=vp}
N 800 -300 860 -300 {
lab=Von}
N 800 -320 840 -320 {
lab=Vop}
N 840 -320 840 -180 {
lab=Vop}
N 700 -180 840 -180 {
lab=Vop}
N 800 -280 820 -280 {
lab=VGND}
N 820 -280 820 -100 {
lab=VGND}
N 570 -200 670 -200 {
lab=VGND}
N 670 -200 820 -200 {
lab=VGND}
N 330 -340 330 -280 {
lab=VGND}
N 330 -310 370 -310 {
lab=VGND}
N 480 -340 500 -340 {
lab=Vcmref}
N 480 -520 480 -340 {
lab=Vcmref}
N 300 -520 480 -520 {
lab=Vcmref}
N 570 -440 670 -440 {
lab=VGND}
N 670 -440 820 -440 {
lab=VGND}
N 820 -440 820 -280 {
lab=VGND}
N 800 -580 800 -340 {
lab=VPWR}
N 300 -580 800 -580 {
lab=VPWR}
N 280 -360 300 -360 {
lab=Vin}
N 280 -260 300 -260 {
lab=Vip}
N 820 -100 820 -60 {
lab=VGND}
N 280 -60 820 -60 {
lab=VGND}
N 280 -520 300 -520 {
lab=Vcmref}
N 280 -580 300 -580 {
lab=VPWR}
N 840 -320 900 -320 {
lab=Vop}
N 860 -340 860 -300 {
lab=Von}
N 860 -300 900 -300 {
lab=Von}
C {/home/jakob/Documents/RALF/Circuits/Examples/OpAmp/OpAmp.sym} 650 -310 0 0 {name=x1}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 330 -360 3 0 {name=R1
L=1.75
model=res_xhigh_po_0p35
spiceprefix=X
mult=1}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 570 -460 3 0 {name=R2
L=1.75
model=res_xhigh_po_0p35
spiceprefix=X
mult=1}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 670 -460 3 0 {name=R3
L=1.75
model=res_xhigh_po_0p35
spiceprefix=X
mult=1}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 330 -260 1 0 {name=R4
L=1.75
model=res_xhigh_po_0p35
spiceprefix=X
mult=1}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 670 -180 3 1 {name=R6
L=1.75
model=res_xhigh_po_0p35
spiceprefix=X
mult=1}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 570 -180 3 1 {name=R5
L=1.75
model=res_xhigh_po_0p35
spiceprefix=X
mult=1}
C {devices/iopin.sym} 280 -580 0 1 {name=p1 lab=VPWR}
C {devices/iopin.sym} 280 -60 0 1 {name=p2 lab=VGND}
C {devices/ipin.sym} 280 -520 0 0 {name=p3 lab=Vocm}
C {devices/ipin.sym} 280 -360 0 0 {name=p4 lab=Vin}
C {devices/ipin.sym} 280 -260 0 0 {name=p5 lab=Vip}
C {devices/opin.sym} 900 -320 0 0 {name=p6 lab=Vop}
C {devices/opin.sym} 900 -300 0 0 {name=p7 lab=Von}
C {devices/title.sym} 160 0 0 0 {name=l1 author="Jakob Ratschenberger"}
C {devices/lab_wire.sym} 370 -310 0 1 {name=p8 sig_type=std_logic lab=VGND}
C {devices/lab_wire.sym} 440 -460 0 0 {name=p9 sig_type=std_logic lab=vp}
C {devices/lab_wire.sym} 440 -180 0 0 {name=p10 sig_type=std_logic lab=vn}
C {devices/lab_wire.sym} 630 -460 0 0 {name=p11 sig_type=std_logic lab=v1}
C {devices/lab_wire.sym} 610 -180 2 0 {name=p12 sig_type=std_logic lab=v2}
