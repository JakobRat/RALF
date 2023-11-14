v {xschem version=3.4.1 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 0 0 320 0 {
lab=VGND}
N 0 -560 260 -560 {
lab=VPWR}
N 0 -560 1340 -560 {
lab=VPWR}
N 320 0 1170 0 {
lab=VGND}
N 1640 -460 1660 -460 {
lab=outp_nb}
N 1640 -440 1660 -440 {
lab=outn_nb}
N 690 -320 690 -300 {
lab=on}
N 870 -320 870 -300 {
lab=op}
N 690 -420 690 -320 {
lab=on}
N 870 -400 870 -320 {
lab=op}
N 690 -240 690 -180 {
lab=VGND}
N 870 -240 870 -180 {
lab=VGND}
N 690 -180 690 0 {
lab=VGND}
N 870 -180 870 0 {
lab=VGND}
N 60 -310 100 -310 {
lab=clk}
N 0 -270 100 -270 {
lab=inn}
N 20 -250 100 -250 {
lab=inp}
N 20 -250 20 -240 {
lab=inp}
N 0 -240 20 -240 {
lab=inp}
N 400 -310 450 -310 {
lab=VPWR}
N 450 -560 450 -310 {
lab=VPWR}
N 400 -290 510 -290 {
lab=on}
N 510 -420 510 -290 {
lab=on}
N 400 -270 540 -270 {
lab=op}
N 540 -400 540 -270 {
lab=op}
N 510 -420 1290 -420 {
lab=on}
N 870 -400 1280 -400 {
lab=op}
N 540 -400 870 -400 {
lab=op}
N 400 -250 450 -250 {
lab=VGND}
N 450 -250 450 -0 {
lab=VGND}
N 1290 -420 1340 -420 {
lab=on}
N 1280 -440 1340 -440 {
lab=op}
N 1280 -440 1280 -400 {
lab=op}
N 1300 -460 1340 -460 {
lab=nclk}
N 1340 -560 1660 -560 {
lab=VPWR}
N 1660 -560 1660 -480 {
lab=VPWR}
N 1640 -480 1660 -480 {
lab=VPWR}
N 1170 0 1670 0 {
lab=VGND}
N 1670 -420 1670 0 {
lab=VGND}
N 1640 -420 1670 -420 {
lab=VGND}
N 1660 -460 1700 -460 {
lab=outp_nb}
N 1700 -480 1700 -460 {
lab=outp_nb}
N 1700 -480 1750 -480 {
lab=outp_nb}
N 1850 -480 1950 -480 {
lab=outp}
N 1850 -320 1940 -320 {
lab=outn}
N 1660 -440 1700 -440 {
lab=outn_nb}
N 1700 -440 1700 -320 {
lab=outn_nb}
N 1700 -320 1750 -320 {
lab=outn_nb}
N 1800 -560 1800 -530 {
lab=VPWR}
N 1660 -560 1800 -560 {
lab=VPWR}
N 1800 -270 1800 -0 {
lab=VGND}
N 1670 -0 1800 -0 {
lab=VGND}
N 1800 -430 1800 -410 {
lab=VGND}
N 1800 -410 1880 -410 {
lab=VGND}
N 1880 -410 1880 -240 {
lab=VGND}
N 1800 -240 1880 -240 {
lab=VGND}
N 1800 -390 1800 -370 {
lab=VPWR}
N 1730 -390 1800 -390 {
lab=VPWR}
N 1730 -560 1730 -390 {
lab=VPWR}
C {devices/iopin.sym} 0 -560 0 1 {name=p1 lab=VPWR}
C {devices/iopin.sym} 0 0 0 1 {name=p2 lab=VGND}
C {devices/ipin.sym} 0 -620 0 0 {name=p5 lab=clk}
C {devices/ipin.sym} 0 -600 0 0 {name=p6 lab=nclk}
C {devices/ipin.sym} 0 -240 0 0 {name=p3 lab=inp}
C {devices/ipin.sym} 0 -270 0 0 {name=p4 lab=inn}
C {devices/opin.sym} 1950 -480 0 0 {name=p7 lab=outp}
C {devices/opin.sym} 1940 -320 0 0 {name=p8 lab=outn}
C {devices/lab_wire.sym} 920 -420 0 0 {name=l2 sig_type=std_logic lab=on}
C {devices/lab_wire.sym} 920 -400 2 1 {name=l3 sig_type=std_logic lab=op}
C {sky130_fd_pr/cap_mim_m3_1.sym} 690 -270 0 0 {name=C1 model=cap_mim_m3_1 W=18.9 L=5.1 MF=1 spiceprefix=X}
C {sky130_fd_pr/cap_mim_m3_1.sym} 870 -270 0 0 {name=C2 model=cap_mim_m3_1 W=18.9 L=5.1 MF=1 spiceprefix=X}
C {/home/jakob/Documents/AutomatedLayoutGeneration/Circuits/Comparator/DiffAmp.sym} 250 -280 0 0 {name=x1}
C {devices/lab_wire.sym} 60 -310 0 0 {name=l4 sig_type=std_logic lab=clk}
C {/home/jakob/Documents/AutomatedLayoutGeneration/Circuits/Comparator/Comp.sym} 1490 -450 0 0 {name=x2}
C {devices/lab_wire.sym} 1300 -460 0 0 {name=l5 sig_type=std_logic lab=nclk}
C {adc_comp_buffer.sym} 1790 -480 0 0 {name=x3}
C {adc_comp_buffer.sym} 1790 -320 0 0 {name=x4}
C {devices/lab_wire.sym} 1710 -480 0 0 {name=l7 sig_type=std_logic lab=outp_nb}
C {devices/lab_wire.sym} 1700 -440 0 0 {name=l8 sig_type=std_logic lab=outn_nb}
