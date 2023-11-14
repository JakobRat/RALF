#!/bin/sh
# ========================================================================
# DRC (Design Rule Check) Script for Open-Source IC Design
#
# SPDX-FileCopyrightText: 2021-2023 Harald Pretl
# Johannes Kepler University, Institute for Integrated Circuits
#
# SPDX-FileCopyrightText: 2023 Jakob Ratschenberger
# Johannes Kepler University, Institute for Integrated Circuits
#
# Modified for usage with python.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# SPDX-License-Identifier: Apache-2.0
#
# ========================================================================

ERR_DRC=1
ERR_FILE_NOT_FOUND=2
ERR_NO_PARAM=3
ERR_CMD_NOT_FOUND=4
ERR_UNKNOWN_FILE=5
ERR_PDK_NOT_SUPPORTED=6

if [ $# -eq 0 ]; then
	echo
	echo "DRC script for Magic-VLSI (IIC@JKU)"
	echo
	echo "Usage: $0 [-d] [-c] [-b] [-w workdir] <cellname>"
	echo "		 -b Check area under box"
	echo "       -c Clean output files"
	echo "       -w Use <workdir> to store result files (default current dir)"
	echo "       -d Enable debug information"
	echo
	exit $ERR_NO_PARAM
fi

# set the default behavior
# ------------------------

RUN_MAGIC=1
RUN_CLEAN=0
DEBUG=0
DRC_CLEAN=1
RESDIR=$PWD
CHECK_BOX=0
BOX=()

# check if the PDK is already supported by this script
# ----------------------------------------------------

if echo "$PDK" | grep -q -i "sky130"; then
	[ $DEBUG -eq 1 ] && echo "[INFO] sky130 PDK selected."
else
	echo "[ERROR] The PDK $PDK is not yet supported!"
	exit $ERR_PDK_NOT_SUPPORTED
fi

# check flags
# -----------

while getopts "cw:b:d" flag; do
	case $flag in
		c)
			[ $DEBUG -eq 1 ] && echo "[INFO] flag -c is set."
			RUN_CLEAN=1
			;;
		w)
			[ $DEBUG -eq 1 ] && echo "[INFO] flag -w is set to <$OPTARG>."
			RESDIR=$OPTARG
			;;
		d)
			echo "[INFO] DEBUG is enabled!"
			DEBUG=1
			;;
		b) 
			echo "[INFO] BOX"
			CHECK_BOX=1
			BOX+=("$OPTARG")
			;;
		*)
			;;
    esac
done
shift $((OPTIND-1))

[ ! -d "$RESDIR" ] && mkdir -p "$RESDIR"
if [ $RUN_CLEAN -eq 1 ]; then
	rm -- -f "$RESDIR"/*.magic.*.rpt
fi 

# define useful variables
# -----------------------

FBASENAME=$(basename "$1" | cut -d. -f1)
EXT_SCRIPT="$RESDIR/drc_$FBASENAME.tcl"

# check if the input file exists
# ------------------------------

if [ -f "$1" ]; then
	CELL_LAY="$1"
elif [ -f "$1.mag" ]; then
	CELL_LAY="$1.mag"
else
	echo "[ERROR] Layout <$CELL_LAY> not found!"
    exit $ERR_FILE_NOT_FOUND
fi

if [ $CHECK_BOX -eq 1 ]; then
	echo "BOX: ${BOX[@]}"
	if [ ${#BOX[@]} -ne 4 ]; then
		echo "[ERROR] Specified box has not 4 entries!"
		exit $ERR_NO_PARAM
	fi
fi

[ $DEBUG -eq 1 ] && echo "[INFO] CELL_LAY=$CELL_LAY"

# check if commands exist in the path
# -----------------------------------

if [ $RUN_MAGIC -eq 1 ]; then
	if [ ! -x "$(command -v magic)" ]; then
    	echo "[ERROR] Magic executable could not be found!"
    	exit $ERR_CMD_NOT_FOUND
	fi
fi

#echo "[INFO] Results are put into <$RESDIR>."
CELL_NAME=$(basename "$CELL_LAY" | cut -d. -f1)

#echo "[INFO] Launching Magic DRC..."

# remove old result files
rm -f "$RESDIR/$CELL_NAME.magic.drc.rpt"
# remove old tcl
rm -f "$RESDIR/drc_$CELL_NAME.tcl"

{
	echo "crashbackups stop"
	echo "load $CELL_LAY"
	echo "set drc_rpt_path $RESDIR/$CELL_NAME.magic.drc.rpt"
	# shellcheck disable=SC2016
	echo 'set fout [open $drc_rpt_path w]'
	echo 'set oscale [cif scale out]'
	echo "set cell_name $CELL_NAME"
} >> $EXT_SCRIPT

if [ $CHECK_BOX -eq 1 ]; then
{
	echo "box ${BOX[0]} ${BOX[1]} ${BOX[2]} ${BOX[3]}"
} >> $EXT_SCRIPT
else
{
	echo 'select top cell'
} >> $EXT_SCRIPT
fi

{
	echo 'drc euclidean on'
	echo 'drc style drc(full)'
	echo 'drc check'
	echo 'set drcresult [drc listall why]'

	echo 'set count 0'
	# shellcheck disable=SC2016
	echo 'puts $fout "$cell_name"'
	# shellcheck disable=SC2016
	echo 'puts $fout "----------------------------------------"'
	# shellcheck disable=SC2016
	echo 'foreach {errtype coordlist} $drcresult {'
	# shellcheck disable=SC2016
	echo '  puts $fout $errtype'
	# shellcheck disable=SC2016
	echo '  puts $fout "----------------------------------------"'
	# shellcheck disable=SC2016
	echo '  foreach coord $coordlist {'
	# shellcheck disable=SC2016
	echo '    set bllx [expr {$oscale * [lindex $coord 0]}]'
	# shellcheck disable=SC2016
	echo '    set blly [expr {$oscale * [lindex $coord 1]}]'
	# shellcheck disable=SC2016
	echo '    set burx [expr {$oscale * [lindex $coord 2]}]'
	# shellcheck disable=SC2016
	echo '    set bury [expr {$oscale * [lindex $coord 3]}]'
	# shellcheck disable=SC2016
	echo '    set coords [format " %.3fum %.3fum %.3fum %.3fum" $bllx $blly $burx $bury]'
	# shellcheck disable=SC2016
	echo '    puts $fout "$coords"'
	# shellcheck disable=SC2016
	echo '    set count [expr {$count + 1} ]'
	echo '  }'
	# shellcheck disable=SC2016
	echo '  puts $fout "----------------------------------------"'
	echo '}'
	# shellcheck disable=SC2016
	echo 'puts $fout "$count"'
	# shellcheck disable=SC2016
	#echo 'puts $fout "\[INFO\] Should be divided by 3 or 4"'
	# shellcheck disable=SC2016
	#echo 'puts $fout ""'
	# shellcheck disable=SC2016
	echo 'close $fout'
	# shellcheck disable=SC2016
	#echo 'puts stdout "$count DRC errors found! (should be divided by 3 or 4)"'
	echo 'quit -nocheck'
} >> "$EXT_SCRIPT"

# run it 
magic -dnull -noconsole \
	-rcfile "$PDKPATH/libs.tech/magic/$PDK.magicrc" \
	"$EXT_SCRIPT" \
	> /dev/null 2> /dev/null &
wait
#echo "---"
	
#count=$( tail -n 1 $RESDIR/$CELL_NAME.magic.drc.rpt )
#count=$((count))
#echo 'Count:' $count
