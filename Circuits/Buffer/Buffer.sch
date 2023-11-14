v {xschem version=3.4.1 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 40 -100 80 -100 {
lab=in}
N 240 -100 280 -100 {
lab=vo1}
N 440 -100 480 -100 {
lab=out}
N 140 -200 140 -160 {
lab=VPWR}
N 140 -200 340 -200 {
lab=VPWR}
N 340 -200 340 -160 {
lab=VPWR}
N 240 -240 240 -200 {
lab=VPWR}
N 140 -40 140 -0 {
lab=xxx}
N 140 -0 340 -0 {
lab=xxx}
N 340 -40 340 -0 {
lab=xxx}
N 240 0 240 20 {
lab=xxx}
C {/home/jakob/Documents/AutomatedLayoutGeneration/Circuits/Buffer/inverter.sym} 100 -40 0 0 {name=x1}
C {/home/jakob/Documents/AutomatedLayoutGeneration/Circuits/Buffer/inverter.sym} 300 -40 0 0 {name=x2}
C {devices/lab_wire.sym} 270 -100 0 0 {name=p1 sig_type=std_logic lab=vo1}
C {devices/ipin.sym} 40 -100 0 0 {name=p2 lab=in}
C {devices/opin.sym} 480 -100 0 0 {name=p3 lab=out}
C {devices/iopin.sym} 240 -240 3 0 {name=p4 lab=VPWR}
C {devices/iopin.sym} 240 20 1 0 {name=p5 lab=VGND}
