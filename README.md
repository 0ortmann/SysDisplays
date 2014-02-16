VolumeDisplay
=============

Small gtk popup for displaying current system volume.
-----------------------------------------------------




The idea and why is it done this way?
-------------------------------------

This script is meant to actually only display volume information, not manipulate anything by itself.
Since I mapped volume changes to the thinkpad-volume buttons via xbindkeys in my arch linux, I did not
need any other software handling volume changes for me. I only needed a display.


How to use it?
--------------

Put the script where you want it to be and edit your xbindkeys config file. 
When pressing the audio keys, the display shall - well, get displayd.
A sample xbindkeys entry could look like

#Decrease Volume Master
"amixer sset Master 2-; python /home/flx/workspace/python/VolumeDisplay/volume_display.py"
  XF86AudioLowerVolume

#Increase Volume Master
"amixer sset Master 2+; python /home/flx/workspace/python/VolumeDisplay/volume_display.py"
  XF86AudioRaiseVolume

Replace the path with your proper path. Replace the keyname (here 'XF86AudioRaiseVolume' or 'XF86AudioLowerVolume') with the key you need it to map against.


How it works:
-------------

The script fetches the master volume of the alsamixer and displays it in a progressbar. After a delay of (per default) 2,5 seconds, the display vanishes. If no display can be seen, no precess is running. 
When the key is pressed again while the window is visble, no new script instance will get started. The existing display will prolong its display time for another (per default) 2,5 seconds. 
The living time can be changed. Change the constant "DISPLAY_DURATION" at the top of the file to the amount of milliseconds you want.