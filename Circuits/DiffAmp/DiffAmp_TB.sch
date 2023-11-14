v {xschem version=3.4.1 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N -70 -180 0 -180 {
lab=GND}
N -70 -220 0 -220 {
lab=Vd}
N -110 -170 -110 -130 {
lab=#net1}
N -110 -130 40 -130 {
lab=#net1}
N 40 -170 40 -130 {
lab=#net1}
N -40 -130 -40 -90 {
lab=#net1}
N -40 -30 -40 -0 {
lab=GND}
N -110 -280 -110 -230 {
lab=#net2}
N 40 -280 40 -230 {
lab=#net3}
N -40 -180 -40 -170 {
lab=GND}
N -40 -240 -40 -220 {
lab=Vd}
N 70 -30 70 0 {
lab=GND}
N 70 -120 70 -90 {
lab=Vd}
N 40 -280 160 -280 {
lab=#net3}
N 160 -280 160 -200 {
lab=#net3}
N 160 -200 210 -200 {
lab=#net3}
N 210 -330 210 -220 {
lab=#net2}
N -110 -330 210 -330 {
lab=#net2}
N -110 -330 -110 -280 {
lab=#net2}
N 510 -220 570 -220 {
lab=Vout}
N -280 -30 -280 0 {
lab=GND}
N -280 -110 -280 -90 {
lab=VDD}
C {/home/jakob/Documents/AutomatedLayoutGeneration/Circuits/DiffAmp/TwoStageDiffAmp.sym} 360 -210 0 0 {name=x1}
C {devices/vsource.sym} -40 -60 0 0 {name=V1 value=0.9}
C {devices/vcvs.sym} -110 -200 0 1 {name=E1 value=0.5}
C {devices/vcvs.sym} 40 -200 0 0 {name=E2 value=-0.5}
C {devices/gnd.sym} -40 0 0 0 {name=l1 lab=GND}
C {devices/gnd.sym} -40 -170 0 0 {name=l2 lab=GND}
C {devices/vsource.sym} 70 -60 0 0 {name=Vd value=0}
C {devices/gnd.sym} 70 0 0 0 {name=l3 lab=GND}
C {devices/lab_wire.sym} 70 -120 0 1 {name=p1 sig_type=std_logic lab=Vd}
C {devices/lab_wire.sym} -40 -240 0 1 {name=p2 sig_type=std_logic lab=Vd}
C {devices/vsource.sym} -280 -60 0 0 {name=V2 value=1.8}
C {devices/gnd.sym} -280 0 0 0 {name=l4 lab=GND}
C {devices/vdd.sym} -280 -110 0 0 {name=l5 lab=VDD}
C {devices/lab_wire.sym} 570 -220 0 1 {name=p3 sig_type=std_logic lab=Vout}
C {devices/code_shown.sym} -390 -590 0 0 {name=NGSPICE
only_toplevel=true
value="
.control
save all
dc Vd -0.1 0.1 0.001
plot deriv(v(Vout))
.endc
" }
C {devices/code.sym} -340 -380 0 0 {name=TT_MODELS
only_toplevel=true
format="tcleval( @value )"
value="
** opencircuitdesign pdks install
.lib $::SKYWATER_MODELS/sky130.lib.spice tt

"
spice_ignore=false}
