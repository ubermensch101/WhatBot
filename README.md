New Instructions for loading desktop app-

Download and unzip the repository, and open it in a virtual environment. Enter the following commands in the (venv) terminal:


pip3 install alright

pip3 install openpyxl

pip3 install kivy

Run main.py

---------------------------------------------------------------------------------------------------------------------------------------------------------

Instructions for making the .exe file (Do this in the virutal environment):

1) Run the command "pyinstaller main.py -w" in the same folder as main.py

2) The above should create two folders, build and dist, and a main.spec file. Rewrite the .spec file using the one uploaded. (Provide correct paths wherever required and do not forget the double-slashes.

3) Now run "pyinstaller main.spec -y" (This is supposed to rewrite all the changes and add all the imports at the location of main.exe)
