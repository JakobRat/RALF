v {xschem version=3.4.1 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 940 -260 970 -260 {
lab=#net1}
N 940 -310 940 -260 {
lab=#net1}
N 940 -310 1300 -310 {
lab=#net1}
N 1300 -310 1300 -220 {
lab=#net1}
N 1270 -220 1300 -220 {
lab=#net1}
N 910 -240 970 -240 {
lab=Vcmm}
N 910 -220 970 -220 {
lab=VcmmOut}
N 910 -200 970 -200 {
lab=Vbias}
N 1270 -260 1280 -260 {
lab=Vdd}
N 1280 -370 1280 -260 {
lab=Vdd}
N 1270 -200 1300 -200 {
lab=Vss}
N 1300 -200 1300 -160 {
lab=Vss}
N 1270 -240 1370 -240 {
lab=Vout}
N 840 -220 910 -220 {
lab=VcmmOut}
N 880 -240 910 -240 {
lab=Vcmm}
N 880 -350 880 -240 {
lab=Vcmm}
N 830 -350 880 -350 {
lab=Vcmm}
N 180 -380 200 -380 {
lab=#net2}
N 260 -380 290 -380 {
lab=#net3}
N 350 -380 370 -380 {
lab=#net4}
N 430 -380 450 -380 {
lab=#net5}
N 510 -380 550 -380 {
lab=VcmmOut}
N 90 -380 120 -380 {
lab=Vop}
N 150 -430 150 -400 {
lab=Vss}
N 150 -430 480 -430 {
lab=Vss}
N 480 -430 480 -400 {
lab=Vss}
N 400 -430 400 -400 {
lab=Vss}
N 320 -430 320 -400 {
lab=Vss}
N 230 -430 230 -400 {
lab=Vss}
N 180 -130 200 -130 {
lab=#net6}
N 260 -130 290 -130 {
lab=#net7}
N 350 -130 370 -130 {
lab=#net8}
N 430 -130 450 -130 {
lab=#net9}
N 510 -130 550 -130 {
lab=VcmmOut}
N 90 -130 120 -130 {
lab=Von}
N 150 -110 150 -80 {
lab=Vss}
N 150 -80 480 -80 {
lab=Vss}
N 480 -110 480 -80 {
lab=Vss}
N 400 -110 400 -80 {
lab=Vss}
N 320 -110 320 -80 {
lab=Vss}
N 230 -110 230 -80 {
lab=Vss}
N 550 -380 570 -380 {
lab=VcmmOut}
N 570 -380 570 -130 {
lab=VcmmOut}
N 550 -130 570 -130 {
lab=VcmmOut}
N 570 -260 630 -260 {
lab=VcmmOut}
N 320 -450 320 -430 {
lab=Vss}
N 320 -80 320 -70 {
lab=Vss}
N 320 -70 320 -60 {
lab=Vss}
C {devices/ipin.sym} 910 -200 0 0 {name=p12 sig_type=std_logic lab=Vbias}
C {devices/opin.sym} 1370 -240 0 0 {name=p13 sig_type=std_logic lab=Vout}
C {devices/ipin.sym} 90 -380 0 0 {name=p14 sig_type=std_logic lab=Vop}
C {devices/ipin.sym} 830 -350 2 1 {name=p17 sig_type=std_logic lab=Vcmm}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 150 -380 1 0 {name=R6
L=2
model=res_xhigh_po_0p35
spiceprefix=X
mult=1}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 230 -380 1 0 {name=R7
L=2
model=res_xhigh_po_0p35
spiceprefix=X
mult=1}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 320 -380 1 0 {name=R8
L=2
model=res_xhigh_po_0p35
spiceprefix=X
mult=1}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 400 -380 1 0 {name=R9
L=2
model=res_xhigh_po_0p35
spiceprefix=X
mult=1}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 480 -380 1 0 {name=R10
L=2
model=res_xhigh_po_0p35
spiceprefix=X
mult=1}
C {devices/ipin.sym} 90 -130 2 1 {name=p20 sig_type=std_logic lab=Von}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 150 -130 1 1 {name=R11
L=2
model=res_xhigh_po_0p35
spiceprefix=X
mult=1}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 230 -130 1 1 {name=R12
L=2
model=res_xhigh_po_0p35
spiceprefix=X
mult=1}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 320 -130 1 1 {name=R13
L=2
model=res_xhigh_po_0p35
spiceprefix=X
mult=1}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 400 -130 1 1 {name=R14
L=2
model=res_xhigh_po_0p35
spiceprefix=X
mult=1}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 480 -130 1 1 {name=R15
L=2
model=res_xhigh_po_0p35
spiceprefix=X
mult=1}
C {devices/lab_wire.sym} 630 -260 2 0 {name=p15 sig_type=std_logic lab=VcmmOut}
C {devices/lab_wire.sym} 840 -220 2 1 {name=p22 sig_type=std_logic lab=VcmmOut}
C {devices/iopin.sym} 1300 -160 1 0 {name=p1 lab=Vss}
C {devices/iopin.sym} 1280 -370 3 0 {name=p2 lab=Vdd}
C {devices/lab_wire.sym} 320 -60 3 0 {name=p3 sig_type=std_logic lab=Vss}
C {devices/lab_wire.sym} 320 -450 1 0 {name=p4 sig_type=std_logic lab=Vss}
C {/home/jakob/Documents/AutomatedLayoutGeneration/Circuits/MillerOpAmpCMMFB/DiffAmp.sym} 1120 -230 0 0 {name=x1}
