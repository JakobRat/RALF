load XM5 -silent -quiet
box 0 0 0 0
::sky130::sky130_fd_pr__nfet_01v8_draw {w 1.0 l 2 m 1 nf 1 diffcov 100 polycov 100 guard 1 glc 0 grc 0 gtc 0 gbc 1 tbcov 100 rlcov 100 topc 1 botc 0 poverlap 0 doverlap 1 lmin 0.15 wmin 0.42 full_metal 1 viasrc 0 viadrn 0 viagate 0 viagb 0 viagr 0 viagl 0 viagt 0}
select cell XM5
save XM5
load XDP_XM1_XM2 -silent -quiet
box 0 0 0 0
::sky130::sky130_fd_pr__nfet_01v8_draw {w 1.0 l 1 m 1 nf 2 diffcov 100 polycov 100 guard 1 glc 0 grc 0 gtc 0 gbc 1 tbcov 100 rlcov 100 topc 1 botc 0 poverlap 0 doverlap 1 lmin 0.15 wmin 0.42 full_metal 1 viasrc 0 viadrn 0 viagate 0 viagb 0 viagr 0 viagl 0 viagt 0}
select cell XDP_XM1_XM2
save XDP_XM1_XM2
load XDL_XM3_XM4 -silent -quiet
box 0 0 0 0
::sky130::sky130_fd_pr__pfet_01v8_draw {w 2.0 l 1 m 2 nf 1 diffcov 100 polycov 100 guard 1 glc 0 grc 0 gtc 0 gbc 1 tbcov 100 rlcov 100 topc 1 botc 1 poverlap 0 doverlap 1 lmin 0.15 wmin 0.42 full_metal 1 viasrc 0 viadrn 0 viagate 0 viagb 0 viagr 0 viagl 0 viagt 0}
select cell XDL_XM3_XM4
save XDL_XM3_XM4
quit -noprompt
