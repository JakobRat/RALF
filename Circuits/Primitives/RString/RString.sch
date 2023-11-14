v {xschem version=3.4.1 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 20 -140 50 -140 {
lab=VB}
N 20 -140 20 -30 {
lab=VB}
N 20 -30 50 -30 {
lab=VB}
N 0 -90 20 -90 {
lab=VB}
N 70 -110 70 -60 {
lab=Vmid}
N 70 -80 100 -80 {
lab=Vmid}
N 70 -200 70 -170 {
lab=Vh}
N 70 0 70 30 {
lab=Vl}
C {devices/iopin.sym} 70 -200 3 0 {name=p1 lab=Vh}
C {devices/iopin.sym} 0 -90 2 0 {name=p2 lab=VB}
C {devices/iopin.sym} 100 -80 0 0 {name=p3 lab=Vmid}
C {devices/iopin.sym} 70 30 1 0 {name=p4 lab=Vl}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 70 -140 0 0 {name=R1
L=0.35
model=res_xhigh_po_0p35
spiceprefix=X
mult=1}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 70 -30 0 0 {name=R2
L=0.35
model=res_xhigh_po_0p35
spiceprefix=X
mult=1}
