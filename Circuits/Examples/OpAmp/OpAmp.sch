v {xschem version=3.4.1 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 70 -270 610 -270 {
lab=Vcmref}
N 70 -190 160 -190 {
lab=Vp}
N 70 -170 160 -170 {
lab=Vn}
N 940 -190 990 -190 {
lab=vcmfb}
N 940 -210 960 -210 {
lab=VPWR}
N 940 -170 960 -170 {
lab=VGND}
N 130 -110 610 -110 {
lab=vbias}
N 120 -150 160 -150 {
lab=vbias}
N 460 -210 490 -210 {
lab=VPWR}
N 490 -310 490 -210 {
lab=VPWR}
N 120 -130 120 -110 {
lab=vbias}
N 130 -210 160 -210 {
lab=vcmfb}
N 120 -150 120 -130 {
lab=vbias}
N 120 -130 160 -130 {
lab=vbias}
N 530 -210 530 -190 {
lab=Von}
N 460 -190 530 -190 {
lab=Von}
N 530 -190 640 -190 {
lab=Von}
N 570 -210 570 -170 {
lab=Vop}
N 460 -170 570 -170 {
lab=Vop}
N 570 -170 640 -170 {
lab=Vop}
N 610 -150 640 -150 {
lab=vbias}
N 610 -150 610 -110 {
lab=vbias}
N 460 -150 490 -150 {
lab=VGND}
N 490 -150 490 -70 {
lab=VGND}
N 610 -270 610 -210 {
lab=Vcmref}
N 610 -210 640 -210 {
lab=Vcmref}
N 1070 -170 1090 -170 {
lab=VGND}
N 1070 -170 1070 -70 {
lab=VGND}
N 960 -70 1070 -70 {
lab=VGND}
N 1070 -210 1090 -210 {
lab=VPWR}
N 1070 -310 1070 -210 {
lab=VPWR}
N 960 -310 1070 -310 {
lab=VPWR}
N 1050 -190 1090 -190 {
lab=vbias}
N 1050 -190 1050 -110 {
lab=vbias}
N 610 -110 1050 -110 {
lab=vbias}
N 120 -110 130 -110 {
lab=vbias}
N 490 -70 960 -70 {
lab=VGND}
N 490 -310 960 -310 {
lab=VPWR}
N 70 -310 490 -310 {
lab=VPWR}
N 960 -310 960 -210 {
lab=VPWR}
N 70 -70 490 -70 {
lab=VGND}
N 960 -170 960 -70 {
lab=VGND}
C {devices/lab_wire.sym} 990 -190 0 1 {name=p2 sig_type=std_logic lab=vcmfb}
C {devices/opin.sym} 530 -210 3 0 {name=p3 lab=Von}
C {devices/opin.sym} 570 -210 3 0 {name=p4 lab=Vop}
C {devices/lab_wire.sym} 1040 -110 0 0 {name=p5 sig_type=std_logic lab=vbias}
C {devices/ipin.sym} 70 -270 0 0 {name=p6 lab=Vocm}
C {devices/ipin.sym} 70 -190 0 0 {name=p7 lab=Vp}
C {devices/ipin.sym} 70 -170 0 0 {name=p8 lab=Vn}
C {devices/iopin.sym} 70 -310 0 1 {name=p9 lab=VPWR}
C {devices/iopin.sym} 70 -70 2 0 {name=p10 lab=VGND}
C {devices/lab_wire.sym} 130 -210 0 0 {name=p1 sig_type=std_logic lab=vcmfb}
C {devices/title.sym} 160 0 0 0 {name=l1 author="Jakob Ratschenberger"}
C {/home/jakob/Documents/RALF/Circuits/Examples/OpAmp/CMMFeedback.sym} 790 -180 0 0 {name=x2}
C {/home/jakob/Documents/RALF/Circuits/Examples/OpAmp/GmBias.sym} 1240 -190 0 1 {name=x3}
C {/home/jakob/Documents/RALF/Circuits/Examples/OpAmp/MillerOpAmp.sym} 310 -170 0 0 {name=x1}
