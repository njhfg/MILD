zone="Z1";

kernel=newArray(3); kernel[0]="Bl"; kernel[1]="Br"; kernel[2]="Qr";
slice=newArray(3); slice[0]="0.2"; slice[1]="0.6"; slice[2]="1";
kernel_number=newArray(3); kernel_number[0]="56"; kernel_number[1]="60"; kernel_number[2]="64";

r="Q2";
k="Bl";

for(i=0;i<3;i++)
	{k_no=kernel_number[i];
	for(j=0;j<3;j++)
		{s=slice[j];
		name=zone+"_"+k+k_no+"_"+s+"_"+r+".tif";
		path="//cifs.research.erasmusmc.nl/mrpg0002/Cristina/Ieva/Asthma_patient_cut/"+name;
		open(path);
		selectImage(name);
		run("Window/Level...");
		setMinAndMax(-1350, 150);}}
run("Images to Stack", "method=[Scale (largest)] use");
run("Make Montage...", "columns=3 rows=3 scale=1 "); //add or remove label
setOption("ScaleConversions", true);
run("16-bit");
saveAs("Tiff", "//cifs.research.erasmusmc.nl/mrpg0002/Cristina/Ieva/Montage.tif");
close("Stack");
//close("Montage.tif");
