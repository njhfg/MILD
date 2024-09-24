#! /bin/sh 

cp -r /home/sdkuser/local/PsdGradFiles /home/sdkuser/PsdGradFiles

pcvipr_recon_binary -f /home/sdkuser/local/data/ScanArchive_RTD01203_*.h5 -out_folder /home/sdkuser/local/data -dat_plus_dicom -export_kdata

LINES=$(find /home/sdkuser -name "*.dcm")
echo $LINES
if [ -z "$LINES" ] #-z checks if a variable is empty
then
	echo "Did not find DICOM files"
else
	echo "Found DICOM files"
fi
mkdir /home/sdkuser/local/data/dicom
chmod 777 /home/sdkuser/local/data/dicom 
find /home/sdkuser -name "*.dcm" -exec mv {} /home/sdkuser/local/data/dicom \; 

