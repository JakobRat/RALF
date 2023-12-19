v {xschem version=3.4.1 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 260 -390 350 -390 {
lab=Vp}
N 260 -370 350 -370 {
lab=Vn}
N 310 -350 350 -350 {
lab=vbias}
N 650 -410 680 -410 {
lab=VPWR}
N 320 -410 350 -410 {
lab=vcmfb}
N 310 -350 310 -330 {
lab=vbias}
N 310 -330 350 -330 {
lab=vbias}
N 650 -350 680 -350 {
lab=VGND}
N 270 -330 310 -330 {
lab=vbias}
N 650 -370 710 -370 {
lab=Vop}
N 710 -370 710 -240 {
lab=Vop}
N 710 -240 710 -220 {
lab=Vop}
N 650 -220 710 -220 {
lab=Vop}
N 650 -390 690 -390 {
lab=Von}
N 690 -390 690 -240 {
lab=Von}
N 650 -240 690 -240 {
lab=Von}
N 690 -390 750 -390 {
lab=Von}
N 710 -370 750 -370 {
lab=Vop}
N 300 -240 350 -240 {
lab=vcmfb}
N 270 -110 350 -110 {
lab=vbias}
N 260 -300 670 -300 {
lab=Vocm}
N 670 -300 670 -260 {
lab=Vocm}
N 650 -260 670 -260 {
lab=Vocm}
N 260 -460 310 -460 {
lab=VPWR}
N 310 -460 680 -460 {
lab=VPWR}
N 680 -460 680 -410 {
lab=VPWR}
N 330 -90 350 -90 {
lab=VGND}
N 650 -200 680 -200 {
lab=vbias}
N 680 -350 730 -350 {
lab=VGND}
N 730 -350 730 -60 {
lab=VGND}
N 330 -60 730 -60 {
lab=VGND}
N 330 -220 350 -220 {
lab=VGND}
N 330 -220 330 -90 {
lab=VGND}
N 310 -260 350 -260 {
lab=VPWR}
N 310 -260 310 -130 {
lab=VPWR}
N 310 -130 350 -130 {
lab=VPWR}
N 330 -90 330 -60 {
lab=VGND}
N 260 -60 330 -60 {
lab=VGND}
N 270 -190 310 -190 {
lab=VPWR}
N 270 -240 300 -240 {}
C {devices/lab_wire.sym} 270 -240 0 0 {name=p2 sig_type=std_logic lab=vcmfb}
C {devices/opin.sym} 750 -390 0 0 {name=p3 lab=Von}
C {devices/opin.sym} 750 -370 0 0 {name=p4 lab=Vop}
C {devices/ipin.sym} 260 -300 0 0 {name=p6 lab=Vocm}
C {devices/ipin.sym} 260 -390 0 0 {name=p7 lab=Vp}
C {devices/ipin.sym} 260 -370 0 0 {name=p8 lab=Vn}
C {devices/iopin.sym} 260 -460 0 1 {name=p9 lab=VPWR}
C {devices/iopin.sym} 260 -60 2 0 {name=p10 lab=VGND}
C {devices/lab_wire.sym} 320 -410 0 0 {name=p1 sig_type=std_logic lab=vcmfb}
C {devices/title.sym} 160 0 0 0 {name=l1 author="Jakob Ratschenberger"}
C {/home/jakob/Documents/RALF/Circuits/Examples/OpAmp/CMMFeedback.sym} 500 -230 0 1 {name=x2}
C {/home/jakob/Documents/RALF/Circuits/Examples/OpAmp/GmBias.sym} 500 -110 0 1 {name=x3}
C {/home/jakob/Documents/RALF/Circuits/Examples/OpAmp/MillerOpAmp.sym} 500 -370 0 0 {name=x1}
C {devices/lab_wire.sym} 270 -330 0 0 {name=p11 sig_type=std_logic lab=vbias}
C {devices/lab_wire.sym} 680 -200 0 1 {name=p12 sig_type=std_logic lab=vbias}
C {devices/lab_wire.sym} 270 -110 0 0 {name=p13 sig_type=std_logic lab=vbias}
C {devices/lab_wire.sym} 270 -190 0 0 {name=p14 sig_type=std_logic lab=VPWR}
