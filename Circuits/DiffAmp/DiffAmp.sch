v {xschem version=3.4.1 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 370 -270 420 -270 {
lab=Vo1_p}
N 420 -270 420 -190 {
lab=Vo1_p}
N 400 -190 420 -190 {
lab=Vo1_p}
N 370 -290 440 -290 {
lab=Vo_n}
N 440 -290 440 -170 {
lab=Vo_n}
N 400 -170 440 -170 {
lab=Vo_n}
N 400 -130 430 -130 {
lab=Vmid}
N 10 -100 80 -100 {
lab=Vbias}
N 80 -100 80 -40 {
lab=Vbias}
N 80 -40 100 -40 {
lab=Vbias}
N 10 -340 10 -120 {
lab=Vdd}
N 10 -340 390 -340 {
lab=Vdd}
N 390 -340 390 -310 {
lab=Vdd}
N 370 -310 390 -310 {
lab=Vdd}
N 390 -370 390 -340 {
lab=Vdd}
N 10 -80 30 -80 {
lab=Vss}
N 30 -80 30 0 {
lab=Vss}
N 60 -190 100 -190 {
lab=Vp}
N 60 -170 100 -170 {
lab=Vn}
N 30 0 400 0 {
lab=Vss}
N 400 -20 400 0 {
lab=Vss}
N 400 -150 480 -150 {
lab=Vss}
N 480 -150 480 -0 {
lab=Vss}
N 400 -0 480 -0 {
lab=Vss}
N 400 -0 400 20 {
lab=Vss}
N 440 -220 560 -220 {
lab=Vo_n}
N 100 -40 190 -40 {
lab=Vbias}
N 230 -10 230 -0 {
lab=Vss}
N 230 -80 230 -70 {
lab=Vmid}
N 230 -80 400 -80 {
lab=Vmid}
N 400 -40 400 -20 {
lab=Vss}
N 230 -40 400 -40 {
lab=Vss}
N 400 -80 430 -80 {
lab=Vmid}
N 430 -130 430 -80 {
lab=Vmid}
C {/home/jakob/Documents/AutomatedLayoutGeneration/Circuits/DiffAmp/DiffPair.sym} 250 -160 0 0 {name=xDiffPair}
C {/home/jakob/Documents/AutomatedLayoutGeneration/Circuits/DiffAmp/Curr_Biasing.sym} -140 -100 0 0 {name=xBias}
C {/home/jakob/Documents/AutomatedLayoutGeneration/Circuits/DiffAmp/PMOS_Load.sym} 220 -290 0 0 {name=xLoad}
C {devices/ipin.sym} 60 -190 0 0 {name=p1 lab=Vp}
C {devices/ipin.sym} 60 -170 0 0 {name=p2 lab=Vn}
C {devices/lab_wire.sym} 80 -90 2 0 {name=p4 sig_type=std_logic lab=Vbias}
C {devices/lab_wire.sym} 430 -110 2 0 {name=p5 sig_type=std_logic lab=Vmid}
C {devices/lab_wire.sym} 420 -250 2 1 {name=p7 sig_type=std_logic lab=Vo1_p}
C {devices/iopin.sym} 390 -370 3 0 {name=p3 lab=Vdd}
C {devices/iopin.sym} 400 20 1 0 {name=p8 lab=Vss}
C {devices/opin.sym} 560 -220 0 0 {name=p9 lab=Vo_n}
C {sky130_fd_pr/nfet_01v8.sym} 210 -40 0 0 {name=M3
L=1
W=12
nf=2 
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
