v {xschem version=3.4.1 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 870 -310 950 -310 {
lab=Von}
N 950 -310 950 -260 {
lab=Von}
N 950 -260 1050 -260 {
lab=Von}
N 1000 -320 1050 -320 {
lab=Vop}
N 1000 -320 1000 -290 {
lab=Vop}
N 870 -290 1000 -290 {
lab=Vop}
N 1020 -300 1050 -300 {
lab=Vcmm}
N 1020 -400 1020 -300 {
lab=Vcmm}
N 530 -400 1020 -400 {
lab=Vcmm}
N 530 -310 570 -310 {
lab=Vp}
N 530 -290 570 -290 {
lab=Vn}
N 530 -330 570 -330 {
lab=Vcmmfb}
N 1350 -300 1400 -300 {
lab=Vcmmfb}
N 1350 -320 1370 -320 {
lab=VPWR}
N 1370 -450 1370 -320 {
lab=VPWR}
N 1350 -280 1370 -280 {
lab=VGND}
N 1370 -280 1370 -170 {
lab=VGND}
N 1020 -280 1050 -280 {
lab=Vbias}
N 1020 -280 1020 -240 {
lab=Vbias}
N 540 -240 1020 -240 {
lab=Vbias}
N 560 -270 570 -270 {
lab=Vbias}
N 560 -270 560 -240 {
lab=Vbias}
N 360 -320 420 -320 {
lab=Vbias}
N 420 -320 420 -240 {
lab=Vbias}
N 420 -240 540 -240 {
lab=Vbias}
N 870 -270 880 -270 {
lab=VGND}
N 880 -270 880 -200 {
lab=VGND}
N 880 -200 1370 -200 {
lab=VGND}
N 360 -300 380 -300 {
lab=VGND}
N 380 -300 380 -200 {
lab=VGND}
N 380 -200 880 -200 {
lab=VGND}
N 360 -340 380 -340 {
lab=VPWR}
N 380 -440 380 -340 {
lab=VPWR}
N 380 -440 1370 -440 {
lab=VPWR}
N 1370 -480 1370 -450 {
lab=VPWR}
N 870 -330 900 -330 {
lab=VPWR}
N 900 -440 900 -330 {
lab=VPWR}
N 950 -310 960 -310 {
lab=Von}
N 960 -340 960 -310 {
lab=Von}
N 1000 -340 1000 -320 {
lab=Vop}
C {devices/lab_wire.sym} 530 -330 0 0 {name=p1 sig_type=std_logic lab=Vcmmfb}
C {devices/lab_wire.sym} 1400 -300 0 1 {name=p2 sig_type=std_logic lab=Vcmmfb}
C {devices/opin.sym} 960 -340 3 0 {name=p3 lab=Von}
C {devices/opin.sym} 1000 -340 3 0 {name=p4 lab=Vop}
C {devices/lab_wire.sym} 510 -240 0 0 {name=p5 sig_type=std_logic lab=Vbias}
C {devices/ipin.sym} 530 -400 0 0 {name=p6 lab=Vcmm}
C {devices/ipin.sym} 530 -310 0 0 {name=p7 lab=Vp}
C {devices/ipin.sym} 530 -290 0 0 {name=p8 lab=Vn}
C {devices/iopin.sym} 1370 -480 3 0 {name=p9 lab=VPWR}
C {devices/iopin.sym} 1370 -170 1 0 {name=p10 lab=VGND}
C {/home/jakob/Documents/AutomatedLayoutGeneration/Circuits/MillerOpAmpCMMFB/MillerOpAmp.sym} 720 -300 0 0 {name=x1}
C {/home/jakob/Documents/AutomatedLayoutGeneration/Circuits/MillerOpAmpCMMFB/CMMFeedback.sym} 1200 -290 0 0 {name=x2}
C {/home/jakob/Documents/AutomatedLayoutGeneration/Circuits/MillerOpAmpCMMFB/Bias.sym} 210 -320 0 0 {name=x3}
