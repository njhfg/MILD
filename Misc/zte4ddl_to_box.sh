#!/bin/bash
################################################################
# This is a script to upload ScanArchive to BOX cloud drive
# This relies on rclone: https://rclone.org/
#
# 1) Search directory for new files
# 2) Move largest to BOX remote directory using rclone
# 3) Move archive once done
#
# Run this via cronjob periodically
#
# F.Callaghan 02.2023
##############################################################

ZTEScanArchiveDir="/media/data/cristina_data/ZTE/Exam14361/Series10"

cd "$ZTEScanArchiveDir"

for FILE in *; do
	if [[$FILE == ScanArchive* ]]; then
		FULLDIR="$ZTEScanArchiveDir/$FILE";
		RES=$(find $FULLDIR -type f -printf '%s %p\n' | sort -nr | head -1) #sort -nr numerical value reverse head -1 select the last one
		read -a strarr <<< "$RES" #????
		LARGESTH5=${strarr[1]} #????
		echo $LARGESTH5
		#rclone copy 

