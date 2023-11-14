v {xschem version=3.4.1 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 780 -360 840 -360 {
lab=Vop1}
N 840 -360 840 -350 {
lab=Vop1}
N 840 -350 890 -350 {
lab=Vop1}
N 780 -380 840 -380 {
lab=Von1}
N 840 -440 840 -380 {
lab=Von1}
N 840 -440 890 -440 {
lab=Von1}
N 780 -400 800 -400 {
lab=xxx}
N 800 -480 800 -400 {
lab=xxx}
N 780 -340 800 -340 {
lab=VGND}
N 800 -340 800 -240 {
lab=VGND}
N 800 -540 800 -480 {
lab=xxx}
N 800 -540 1240 -540 {
lab=xxx}
N 1240 -540 1240 -440 {
lab=xxx}
N 1190 -440 1240 -440 {
lab=xxx}
N 1240 -440 1240 -350 {
lab=xxx}
N 1190 -350 1240 -350 {
lab=xxx}
N 800 -240 800 -220 {
lab=VGND}
N 800 -220 1220 -220 {
lab=VGND}
N 1220 -310 1220 -220 {
lab=VGND}
N 1190 -310 1220 -310 {
lab=VGND}
N 1220 -400 1220 -310 {
lab=VGND}
N 1190 -400 1220 -400 {
lab=VGND}
N 1190 -420 1330 -420 {
lab=Von}
N 1190 -330 1320 -330 {
lab=Vop}
N 410 -400 480 -400 {
lab=Vbias2}
N 410 -380 480 -380 {
lab=Vp}
N 410 -360 480 -360 {
lab=Vn}
N 410 -340 480 -340 {
lab=Vbias1}
N 460 -340 460 -280 {
lab=Vbias1}
N 460 -280 880 -280 {
lab=Vbias1}
N 880 -330 880 -280 {
lab=Vbias1}
N 880 -330 890 -330 {
lab=Vbias1}
N 880 -420 880 -330 {
lab=Vbias1}
N 880 -420 890 -420 {
lab=Vbias1}
N 1580 -380 1580 -320 {
lab=Von1}
N 1580 -260 1580 -200 {
lab=Von}
N 1760 -380 1760 -320 {
lab=Vop1}
N 1760 -260 1760 -200 {
lab=Vop}
N 1020 -600 1020 -540 {
lab=xxx}
N 1040 -220 1040 -140 {
lab=VGND}
C {/home/jakob/Documents/AutomatedLayoutGeneration/Circuits/MillerOpAmp/DiffAmp.sym} 630 -370 0 0 {name=x1}
C {/home/jakob/Documents/AutomatedLayoutGeneration/Circuits/MillerOpAmp/CSAmp.sym} 1040 -420 0 0 {name=x2}
C {/home/jakob/Documents/AutomatedLayoutGeneration/Circuits/MillerOpAmp/CSAmp.sym} 1040 -330 0 0 {name=x3}
C {sky130_fd_pr/cap_mim_m3_1.sym} 1580 -290 0 0 {name=C1 model=cap_mim_m3_1 W=5 L=5 MF=1 spiceprefix=X}
C {sky130_fd_pr/cap_mim_m3_1.sym} 1760 -290 0 0 {name=C2 model=cap_mim_m3_1 W=5 L=5 MF=1 spiceprefix=X}
C {devices/opin.sym} 1330 -420 0 0 {name=p1 lab=Von}
C {devices/opin.sym} 1320 -330 0 0 {name=p2 lab=Vop}
C {devices/lab_wire.sym} 850 -440 0 0 {name=p3 sig_type=std_logic lab=Von1}
C {devices/lab_wire.sym} 860 -350 0 0 {name=p4 sig_type=std_logic lab=Vop1}
C {devices/lab_wire.sym} 1580 -380 0 0 {name=p5 sig_type=std_logic lab=Von1}
C {devices/lab_wire.sym} 1760 -380 0 0 {name=p6 sig_type=std_logic lab=Vop1}
C {devices/lab_wire.sym} 1760 -200 0 0 {name=p7 sig_type=std_logic lab=Vop}
C {devices/lab_wire.sym} 1580 -200 0 0 {name=p8 sig_type=std_logic lab=Von}
C {devices/ipin.sym} 410 -400 0 0 {name=p9 lab=Vbias2}
C {devices/ipin.sym} 410 -380 0 0 {name=p10 lab=Vp}
C {devices/ipin.sym} 410 -360 0 0 {name=p11 lab=Vn}
C {devices/ipin.sym} 410 -340 0 0 {name=p12 lab=Vbias1}
C {devices/iopin.sym} 1020 -600 3 0 {name=p13 lab=VPWR}
C {devices/iopin.sym} 1040 -140 1 0 {name=p14 lab=VGND}
