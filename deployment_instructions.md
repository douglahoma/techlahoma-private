### UPDATING THE SITE ###

Currently, the most straightforward way to update the site involves building
the repo as a Python package using a tool called build which you can install like
any other Python package with the command:
```
pip3 install build
```
The files 'pyproject.toml' and 'MANIFEST.in' are instructions for build which tell
it the specifics of what we want our module to look like.

#### 1. CREATE THE PACKAGE ####
Assuming you have build installed, the first step is to build the module is to run the command
```
python3 -m build
```
from the root of the repo. This will end up making a folder called 'dist' which will contain a file
called 'techlahoma_checkin-0.0.1.tar.gz' -- which is the one we want.

#### 2. UPLOAD IT TO THE SITE ####
One we have a new version of 'techlahoma_checkin-0.0.1.tar.gz' go to https://www.pythonanywhere.com/
logging in using the credentials that Jon posted on slack. Click on the 'Files' tab and it will have 
GUI interface for navigating the file system. But 'techlahoma_checkin-0.0.1.tar.gz' just needs to go 
in the user home directory where the files tab opens up onto. Making sure you delete a previous version of 'techlahoma_checkin-0.0.1.tar.gz' that may or may not still be there, click the yellow "Upload a file" button and upload the new version of it.

#### 3. UNINSTALL AND REINSTALL THE MODULE 'techlahoma_checkin' ####
Once you have the new file on the server, there's a button at the top of the page which says
"Open Bash console here." Click that and type the command once the console opens up:
```
pip3 uninstall techlahoma_checkin
```
And then, once it's finished, basically just do the opposite and type the command:
```
pip3 install techlahoma_checkin-0.0.1.tar.gz
```
#### 4. RELOAD 'www.checklahoma.com' ####

After the new version of the module has been installed you should then be able to reload the site by clicking the 'web' tab at the top of the page and on the 'Web' page it navigates to click on the green button which says 'reload www.checklahoma.com' to make sure it starts serving the new version of the page.
