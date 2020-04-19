# KiraGame Translation
## Setup
Create a "data" folder and copy the rom as "dn1.nds" in it.  
(Optional, only for PSD export) Install [ImageMagick](https://imagemagick.org/script/download.php#windows), check the "Add application directory to your system path" while installing.  
## Run from binary
Download the latest [release](https://github.com/Illidanz/MushishiTranslation/releases) outside the data folder.  
Run "tool extract" to extract everything and "tool repack" to repack after editing.  
Run "tool extract --help" or "tool repack --help" for more info.  
## Run from source
Install [Python 3.8](https://www.python.org/downloads/) and pipenv.  
Download [ndstool.exe](https://www.darkfader.net/ds/files/ndstool.exe).  
Download xdelta.exe.  
Run "pipenv install".  
Run the tool with "pipenv run tool.py" or build with "pipenv run pyinstaller tool.spec".  
## Text Editing
Rename the \*\_output.txt files to \*\_input.txt (bin_output.txt to bin_input.txt, etc) and add translations for each line after the "=" sign.  
To blank out a line, use a single "!". If just left empty, the line will be left untranslated.  
Comments can be added at the end of lines by using #  
## Image Editing
Rename the out\_\* folders to work\_\* (out_IMG to work_IMG, etc).  
Edit the images in the work folder(s). The palette on the right should be followed but the repacker will try to approximate other colors to the closest one.  
If an image doesn't require repacking, it should be deleted from the work folder.  