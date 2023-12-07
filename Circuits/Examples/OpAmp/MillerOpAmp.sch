v {xschem version=3.4.1 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 1010 -500 1070 -500 {
lab=Von}
N 1010 -320 1060 -320 {
lab=Vop}
N 170 -440 270 -440 {
lab=Vp}
N 170 -420 270 -420 {
lab=Vn}
N 170 -400 270 -400 {
lab=Vbdan}
N 290 -280 290 -220 {
lab=von1}
N 290 -160 290 -100 {
lab=Von}
N 470 -280 470 -220 {
lab=vop1}
N 470 -160 470 -100 {
lab=Vop}
N 170 -80 260 -80 {
lab=VGND}
N 250 -460 270 -460 {
lab=Vbdap}
N 170 -460 250 -460 {
lab=Vbdap}
N 570 -440 650 -440 {
lab=von1}
N 650 -520 650 -440 {
lab=von1}
N 650 -520 710 -520 {
lab=von1}
N 570 -420 650 -420 {
lab=vop1}
N 650 -420 650 -340 {
lab=vop1}
N 650 -340 710 -340 {
lab=vop1}
N 690 -500 710 -500 {
lab=Vbcsn}
N 690 -500 690 -320 {
lab=Vbcsn}
N 690 -320 710 -320 {
lab=Vbcsn}
N 170 -320 690 -320 {
lab=Vbcsn}
N 170 -580 590 -580 {
lab=VPWR}
N 590 -580 590 -460 {
lab=VPWR}
N 570 -460 590 -460 {
lab=VPWR}
N 590 -580 1030 -580 {
lab=VPWR}
N 1030 -580 1030 -520 {
lab=VPWR}
N 1010 -520 1030 -520 {
lab=VPWR}
N 1030 -520 1030 -340 {
lab=VPWR}
N 1010 -340 1030 -340 {
lab=VPWR}
N 260 -80 1020 -80 {
lab=VGND}
N 1020 -300 1020 -80 {
lab=VGND}
N 1010 -300 1020 -300 {
lab=VGND}
N 1020 -480 1020 -300 {
lab=VGND}
N 1010 -480 1020 -480 {
lab=VGND}
N 570 -400 590 -400 {
lab=VGND}
N 590 -400 590 -80 {
lab=VGND}
N 1060 -320 1070 -320 {
lab=Vop}
C {sky130_fd_pr/cap_mim_m3_1.sym} 290 -190 0 0 {name=C1 model=cap_mim_m3_1 W=4 L=4 MF=1 spiceprefix=X}
C {sky130_fd_pr/cap_mim_m3_1.sym} 470 -190 0 0 {name=C2 model=cap_mim_m3_1 W=4 L=4 MF=1 spiceprefix=X}
C {devices/opin.sym} 1070 -500 0 0 {name=p1 lab=Von}
C {devices/opin.sym} 1070 -320 0 0 {name=p2 lab=Vop}
C {devices/lab_wire.sym} 650 -520 0 0 {name=p3 sig_type=std_logic lab=von1}
C {devices/lab_wire.sym} 290 -280 0 0 {name=p5 sig_type=std_logic lab=von1}
C {devices/lab_wire.sym} 470 -280 0 0 {name=p6 sig_type=std_logic lab=vop1}
C {devices/lab_wire.sym} 470 -100 0 0 {name=p7 sig_type=std_logic lab=Vop}
C {devices/lab_wire.sym} 290 -100 0 0 {name=p8 sig_type=std_logic lab=Von}
C {devices/ipin.sym} 170 -320 0 0 {name=p9 lab=Vbcsn}
C {devices/ipin.sym} 170 -440 0 0 {name=p10 lab=Vp}
C {devices/ipin.sym} 170 -420 0 0 {name=p11 lab=Vn}
C {devices/ipin.sym} 170 -400 0 0 {name=p12 lab=Vbdan}
C {devices/iopin.sym} 170 -580 2 0 {name=p13 lab=VPWR}
C {devices/iopin.sym} 170 -80 2 0 {name=p14 lab=VGND}
C {devices/ipin.sym} 170 -460 0 0 {name=p15 lab=Vbdap}
C {devices/lab_wire.sym} 650 -340 0 0 {name=p16 sig_type=std_logic lab=vop1}
C {devices/title.sym} 160 0 0 0 {name=l1 author="Jakob Ratschenberger"}
C {/home/jakob/Documents/RALF/Circuits/Examples/OpAmp/DiffAmp.sym} 420 -430 0 0 {name=x1}
C {/home/jakob/Documents/RALF/Circuits/Examples/OpAmp/CSAmp.sym} 860 -500 0 0 {name=x2}
C {/home/jakob/Documents/RALF/Circuits/Examples/OpAmp/CSAmp.sym} 860 -320 0 0 {name=x3}
