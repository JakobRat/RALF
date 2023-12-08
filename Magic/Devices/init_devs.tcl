load XM1_x3_x1_x1 -silent -quiet
box 0 0 0 0
::sky130::sky130_fd_pr__pfet_01v8_draw {w 8.0 l 1 m 1 nf 1 diffcov 100 polycov 100 guard 1 glc 0 grc 0 gtc 0 gbc 1 tbcov 100 rlcov 100 topc 1 botc 0 poverlap 0 doverlap 1 lmin 0.15 wmin 0.42 full_metal 1 viasrc 0 viadrn 0 viagate 0 viagb 0 viagr 0 viagl 0 viagt 0}
select cell XM1_x3_x1_x1
save XM1_x3_x1_x1
load XM2_x3_x1_x1 -silent -quiet
box 0 0 0 0
::sky130::sky130_fd_pr__nfet_01v8_draw {w 10.0 l 2 m 1 nf 1 diffcov 100 polycov 100 guard 1 glc 0 grc 0 gtc 0 gbc 1 tbcov 100 rlcov 100 topc 1 botc 0 poverlap 0 doverlap 1 lmin 0.15 wmin 0.42 full_metal 1 viasrc 0 viadrn 0 viagate 0 viagb 0 viagr 0 viagl 0 viagt 0}
select cell XM2_x3_x1_x1
save XM2_x3_x1_x1
load XM3_x3_x1_x1 -silent -quiet
box 0 0 0 0
::sky130::sky130_fd_pr__pfet_01v8_draw {w 8.0 l 1 m 1 nf 1 diffcov 100 polycov 100 guard 1 glc 0 grc 0 gtc 0 gbc 1 tbcov 100 rlcov 100 topc 1 botc 0 poverlap 0 doverlap 1 lmin 0.15 wmin 0.42 full_metal 1 viasrc 0 viadrn 0 viagate 0 viagb 0 viagr 0 viagl 0 viagt 0}
select cell XM3_x3_x1_x1
save XM3_x3_x1_x1
load XM4_x3_x1_x1 -silent -quiet
box 0 0 0 0
::sky130::sky130_fd_pr__nfet_01v8_draw {w 10.0 l 2 m 1 nf 1 diffcov 100 polycov 100 guard 1 glc 0 grc 0 gtc 0 gbc 1 tbcov 100 rlcov 100 topc 1 botc 0 poverlap 0 doverlap 1 lmin 0.15 wmin 0.42 full_metal 1 viasrc 0 viadrn 0 viagate 0 viagb 0 viagr 0 viagl 0 viagt 0}
select cell XM4_x3_x1_x1
save XM4_x3_x1_x1
quit -noprompt
