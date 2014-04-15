SysDisplays
===========

Small gtk popups for displaying some system informations.
This script can be called with the parameters "volume" and "backlight"



VolumeDisplay (python sysbars.py "volume"):
==========================================

Small gtk popup for displaying current system volume.


The idea and why is it done this way?


This script is meant to actually only display volume information, not manipulate anything by itself.
Since I mapped volume changes to the thinkpad-volume buttons via xbindkeys in my arch linux, I did not
need any other software handling volume changes for me. I only needed a display.


How to use it?


Put the script where you want it to be and edit your xbindkeys config file. 
When pressing the audio keys, the display shall - well, get displayd.
A sample xbindkeys entry could look like

```
#Decrease Volume Master
"amixer sset Master 2-; python /your/path/to/file/sysbars.py 'volume'"
  XF86AudioLowerVolume

#Increase Volume Master
"amixer sset Master 2+; python /your/path/to/file/sysbars.py 'volume'"
  XF86AudioRaiseVolume
```

Replace the path with your proper path. Replace the keyname (here 'XF86AudioRaiseVolume' or 'XF86AudioLowerVolume') with the key you need it to map against.


How it works:


The script fetches the master volume of the alsamixer and displays it in a progressbar. After a delay of (per default) 2,5 seconds, the display vanishes. If no display can be seen, no process is running. 
When the key is pressed again while the window is visble, no new script instance will get started. The existing display will prolong its display time for another (per default) 2,5 seconds. 
The living time can be changed. Change the constant "DISPLAY_DURATION" at the top of the file to the amount of milliseconds you want.





BacklightDisplay (python sysbars.py "backlight"):
==========================================

Small gtk popup for displaying current system screen brightness.

Mostly the same as VolumeDisplay, just that the bar is placed a little more to the right and reads from linux systems /sys/class/backlight. This is adjustable in the head of the file to freely map the scripts functionality to whatever driver one uses.


How to use it?

Same fish as for VolumeDisplay. Map it with xbindkeys:

Put the script where you want it to be and edit your xbindkeys config file.
When pressing the brightness keys, the display shall - well, get displayd.
A sample xbindkeys entry could look like

```
#Decrease Volume Master
"python /your/path/to/file/sysbars.py 'backlight'"
  XF86MonBrightnessDown

#Increase Volume Master
"python /your/path/to/file/sysbars.py 'backlight'"
  XF86MonBrightnessUp
```

How it works:

The script reads in the value of the 'actual_brightness' file under the systems backlight folder and displays it in a progressbar. After a delay of (per default) 2,5 seconds, the display vanishes. If no display can be seen, no process is running.
When the triggering key is pressed again while the window is visble, no new script instance will get started. The existing display will prolong its display time for another (per default) 2,5 seconds.
The living time can be changed. Change the constant "DISPLAY_DURATION" at the top of the file to the amount of milliseconds you want.


