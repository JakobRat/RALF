v {xschem version=3.4.1 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
T {   Copyright 2022 Manuel Moser

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.} 740 -220 0 0 0.2 0.2 {}
N -10 -310 40 -310 {
lab=#net1}
N 20 -260 150 -260 {
lab=#net1}
N 10 -260 20 -260 {
lab=#net1}
N 10 -310 10 -260 {
lab=#net1}
N -20 -310 -10 -310 {
lab=#net1}
N 750 -400 840 -400 {
lab=comp_outp}
N 750 -410 750 -400 {
lab=comp_outp}
N 720 -410 750 -410 {
lab=comp_outp}
N 720 -370 750 -370 {
lab=comp_outn}
N 750 -380 750 -370 {
lab=comp_outn}
N 750 -380 840 -380 {
lab=comp_outn}
N 150 -280 210 -280 {
lab=#net2}
N 150 -260 210 -260 {
lab=#net1}
N -80 -340 -80 -330 {
lab=VDD}
N -80 -290 -80 -280 {
lab=VSS}
N 90 -340 90 -330 {
lab=VDD}
N 90 -290 90 -280 {
lab=VSS}
N 560 -300 560 -290 {
lab=VDD}
N 560 -210 560 -200 {
lab=VSS}
N 910 -450 910 -440 {
lab=VDD}
N 910 -340 910 -330 {
lab=VSS}
N 870 -620 870 -610 {
lab=VDD}
N 870 -530 870 -520 {
lab=VSS}
N 810 -560 830 -560 {
lab=comp_outp}
N 810 -560 810 -400 {
lab=comp_outp}
N 780 -580 830 -580 {
lab=comp_outn}
N 780 -580 780 -380 {
lab=comp_outn}
N 150 -310 150 -280 {
lab=#net2}
N -150 -310 -130 -310 {
lab=clk}
N 920 -570 1040 -570 {
lab=comp_trig}
N 980 -400 1040 -400 {
lab=latch_qn}
N 980 -380 1040 -380 {
lab=latch_q}
N -80 -280 -80 -270 {
lab=VSS}
N -80 -350 -80 -340 {
lab=VDD}
N 90 -350 90 -340 {
lab=VDD}
N 560 -310 560 -300 {
lab=VDD}
N 870 -630 870 -620 {
lab=VDD}
N 540 -220 560 -220 {}
N 560 -220 560 -210 {}
N 560 -290 560 -280 {}
N 540 -280 560 -280 {}
N 650 -410 720 -410 {}
N 650 -410 650 -260 {}
N 540 -260 650 -260 {}
N 720 -370 720 -240 {}
N 540 -240 720 -240 {}
N 210 -280 240 -280 {}
N 210 -260 240 -260 {}
N 200 -240 240 -240 {}
N 200 -220 240 -220 {}
C {devices/title.sym} 150 -40 0 0 {name=l1 author="Manuel Moser"}
C {devices/iopin.sym} 200 -720 0 1 {name=p1 lab=VDD}
C {devices/iopin.sym} 200 -640 0 1 {name=p2 lab=VSS}
C {devices/ipin.sym} -150 -310 0 0 {name=p3 lab=clk}
C {devices/ipin.sym} 200 -220 0 0 {name=p4 lab=inp}
C {devices/ipin.sym} 200 -240 0 0 {name=p5 lab=inn}
C {devices/opin.sym} 1040 -570 0 0 {name=p6 lab=comp_trig}
C {devices/opin.sym} 1040 -400 0 0 {name=p7 lab=latch_qn}
C {devices/opin.sym} 1040 -380 0 0 {name=p8 lab=latch_q}
C {adc_inverter.sym} -80 -310 0 0 {name=x4}
C {adc_inverter.sym} 90 -310 0 0 {name=x5}
C {adc_nor.sym} 870 -570 0 0 {name=x3}
C {adc_nor_latch.sym} 910 -390 0 0 {name=x2}
C {devices/lab_wire.sym} 560 -310 0 0 {name=l3 sig_type=std_logic lab=VDD}
C {devices/lab_wire.sym} 870 -520 3 0 {name=l7 sig_type=std_logic lab=VSS}
C {devices/lab_wire.sym} 90 -350 0 0 {name=l4 sig_type=std_logic lab=VDD}
C {devices/lab_wire.sym} -80 -350 0 0 {name=l5 sig_type=std_logic lab=VDD}
C {devices/lab_wire.sym} 870 -630 0 0 {name=l6 sig_type=std_logic lab=VDD}
C {devices/lab_wire.sym} 910 -450 0 0 {name=l2 sig_type=std_logic lab=VDD}
C {devices/lab_wire.sym} 910 -330 3 0 {name=l8 sig_type=std_logic lab=VSS}
C {devices/lab_wire.sym} 560 -200 3 0 {name=l9 sig_type=std_logic lab=VSS}
C {devices/lab_wire.sym} 90 -280 3 0 {name=l10 sig_type=std_logic lab=VSS}
C {devices/lab_wire.sym} -80 -270 3 0 {name=l11 sig_type=std_logic lab=VSS}
C {devices/lab_wire.sym} 730 -410 0 1 {name=l12 sig_type=std_logic lab=comp_outp}
C {devices/lab_wire.sym} 730 -370 2 0 {name=l13 sig_type=std_logic lab=comp_outn}
C {/home/jakob/Documents/AutomatedLayoutGeneration/Circuits/Comparator/adc_comp.sym} 390 -250 0 0 {name=x1}
