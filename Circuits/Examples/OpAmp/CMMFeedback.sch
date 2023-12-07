v {xschem version=3.4.1 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 820 -430 850 -430 {
lab=vdts}
N 820 -480 820 -430 {
lab=vdts}
N 820 -480 1180 -480 {
lab=vdts}
N 1180 -480 1180 -390 {
lab=vdts}
N 1150 -390 1180 -390 {
lab=vdts}
N 790 -370 850 -370 {
lab=Vbdan}
N 1150 -430 1160 -430 {
lab=Vdd}
N 1160 -540 1160 -430 {
lab=Vdd}
N 1150 -370 1180 -370 {
lab=Vss}
N 1180 -370 1180 -330 {
lab=Vss}
N 1150 -410 1250 -410 {
lab=Vout}
N 720 -390 790 -390 {
lab=vcmi}
N 770 -410 800 -410 {
lab=Vcmref}
N 770 -520 770 -410 {
lab=Vcmref}
N 270 -510 290 -510 {
lab=#net1}
N 350 -510 380 -510 {
lab=#net2}
N 440 -510 460 -510 {
lab=#net3}
N 520 -510 540 -510 {
lab=#net4}
N 600 -510 640 -510 {
lab=vcmi}
N 170 -510 210 -510 {
lab=Vp}
N 240 -560 240 -530 {
lab=Vss}
N 240 -560 570 -560 {
lab=Vss}
N 570 -560 570 -530 {
lab=Vss}
N 490 -560 490 -530 {
lab=Vss}
N 410 -560 410 -530 {
lab=Vss}
N 320 -560 320 -530 {
lab=Vss}
N 270 -260 290 -260 {
lab=#net5}
N 350 -260 380 -260 {
lab=#net6}
N 440 -260 460 -260 {
lab=#net7}
N 520 -260 540 -260 {
lab=#net8}
N 600 -260 640 -260 {
lab=vcmi}
N 170 -260 210 -260 {
lab=Vn}
N 240 -240 240 -210 {
lab=Vss}
N 240 -210 570 -210 {
lab=Vss}
N 570 -240 570 -210 {
lab=Vss}
N 490 -240 490 -210 {
lab=Vss}
N 410 -240 410 -210 {
lab=Vss}
N 320 -240 320 -210 {
lab=Vss}
N 640 -510 660 -510 {
lab=vcmi}
N 660 -510 660 -260 {
lab=vcmi}
N 640 -260 660 -260 {
lab=vcmi}
N 660 -390 720 -390 {
lab=vcmi}
N 410 -580 410 -560 {
lab=Vss}
N 410 -210 410 -200 {
lab=Vss}
N 410 -200 410 -190 {
lab=Vss}
N 790 -390 820 -390 {
lab=vcmi}
N 800 -410 820 -410 {
lab=Vcmref}
N 820 -410 850 -410 {
lab=Vcmref}
N 820 -390 850 -390 {
lab=vcmi}
N 170 -630 770 -630 {
lab=Vcmref}
N 770 -630 770 -520 {
lab=Vcmref}
N 150 -100 1180 -100 {
lab=Vss}
N 1180 -330 1180 -100 {
lab=Vss}
N 150 -140 770 -140 {
lab=Vbdan}
N 770 -360 770 -140 {
lab=Vbdan}
N 770 -370 770 -360 {
lab=Vbdan}
N 770 -370 790 -370 {
lab=Vbdan}
N 170 -680 1160 -680 {
lab=Vdd}
N 1160 -680 1160 -540 {
lab=Vdd}
C {devices/ipin.sym} 150 -140 0 0 {name=p12 sig_type=std_logic lab=Vbdan}
C {devices/opin.sym} 1250 -410 0 0 {name=p13 sig_type=std_logic lab=Vout}
C {devices/ipin.sym} 170 -510 0 0 {name=p14 sig_type=std_logic lab=Vp}
C {devices/ipin.sym} 170 -630 0 0 {name=p17 sig_type=std_logic lab=Vcmref}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 240 -510 1 0 {name=R1
L=3.5
model=res_xhigh_po_0p35
spiceprefix=X
mult=1}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 320 -510 1 0 {name=R2
L=3.5
model=res_xhigh_po_0p35
spiceprefix=X
mult=1}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 410 -510 1 0 {name=R3
L=3.5
model=res_xhigh_po_0p35
spiceprefix=X
mult=1}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 490 -510 1 0 {name=R4
L=3.5
model=res_xhigh_po_0p35
spiceprefix=X
mult=1}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 570 -510 1 0 {name=R5
L=3.5
model=res_xhigh_po_0p35
spiceprefix=X
mult=1}
C {devices/ipin.sym} 170 -260 2 1 {name=p20 sig_type=std_logic lab=Vn}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 240 -260 1 1 {name=R6
L=3.5
model=res_xhigh_po_0p35
spiceprefix=X
mult=1}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 320 -260 1 1 {name=R10
L=3.5
model=res_xhigh_po_0p35
spiceprefix=X
mult=1}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 410 -260 1 1 {name=R9
L=3.5
model=res_xhigh_po_0p35
spiceprefix=X
mult=1}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 490 -260 1 1 {name=R8
L=3.5
model=res_xhigh_po_0p35
spiceprefix=X
mult=1}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 570 -260 1 1 {name=R7
L=3.5
model=res_xhigh_po_0p35
spiceprefix=X
mult=1}
C {devices/lab_wire.sym} 720 -390 0 1 {name=p15 sig_type=std_logic lab=vcmi}
C {devices/iopin.sym} 150 -100 2 0 {name=p1 lab=Vss}
C {devices/iopin.sym} 170 -680 0 1 {name=p2 lab=Vdd}
C {devices/lab_wire.sym} 410 -190 3 0 {name=p3 sig_type=std_logic lab=Vss}
C {devices/lab_wire.sym} 410 -580 1 0 {name=p4 sig_type=std_logic lab=Vss}
C {devices/lab_wire.sym} 890 -480 0 1 {name=p5 sig_type=std_logic lab=vdts}
C {devices/title.sym} 150 0 0 0 {name=l1 author="Jakob Ratschenberger"}
C {/home/jakob/Documents/RALF/Circuits/Examples/OpAmp/DiffAmp.sym} 1000 -400 0 0 {name=x1}
