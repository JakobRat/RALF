v {xschem version=3.4.1 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 440 -200 500 -200 {
lab=#net1}
N 400 -20 470 -20 {
lab=GND}
N 800 -160 800 -20 {
lab=GND}
N 470 -20 800 -20 {
lab=GND}
N 800 -200 830 -200 {
lab=VDD}
N 830 -330 830 -200 {
lab=VDD}
N 830 -340 830 -330 {
lab=VDD}
N 390 -340 830 -340 {
lab=VDD}
N 470 -20 470 -0 {
lab=GND}
N 470 -0 470 20 {
lab=GND}
N 800 -180 880 -180 {
lab=Vout}
N 330 -200 440 -200 {
lab=#net1}
N 330 -220 380 -220 {
lab=VDD}
N 380 -340 380 -220 {
lab=VDD}
N 380 -340 390 -340 {
lab=VDD}
N 330 -180 380 -180 {
lab=GND}
N 380 -180 380 -20 {
lab=GND}
N 380 -20 400 -20 {
lab=GND}
N -0 -220 30 -220 {
lab=Vp}
N -0 -200 30 -200 {
lab=Vn}
N 380 -380 380 -340 {
lab=VDD}
N 460 -200 460 -150 {}
N 460 -90 460 -60 {}
N 460 -60 860 -60 {}
N 860 -180 860 -60 {}
C {/home/jakob/Documents/AutomatedLayoutGeneration/Circuits/DiffAmp/CMS_Amp.sym} 650 -180 0 0 {name=xCMS}
C {devices/opin.sym} 880 -180 2 1 {name=p3 lab=Vout}
C {devices/gnd.sym} 470 20 0 0 {name=l2 lab=GND}
C {/home/jakob/Documents/AutomatedLayoutGeneration/Circuits/DiffAmp/DiffAmp.sym} 180 -200 0 0 {name=xDiffAmp}
C {devices/vdd.sym} 380 -380 0 0 {name=l1 lab=VDD}
C {devices/ipin.sym} 0 -220 2 1 {name=p1 lab=Vp}
C {devices/ipin.sym} 0 -200 2 1 {name=p2 lab=Vn}
C {devices/lab_wire.sym} 420 -200 2 1 {name=p4 lab=Vo_n}
C {sky130_fd_pr/cap_mim_m3_1.sym} 460 -120 0 0 {name=C1 model=cap_mim_m3_1 W=10 L=10 MF=1 spiceprefix=X}
