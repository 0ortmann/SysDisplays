#!/usr/bin/python

import alsaaudio
import os # for instance management
from gi.repository import Gtk, Gdk, GObject


# path to a temporary file for a pid.
MY_TEMP_PATH="/tmp/volume_display_running.tmp"

# milliseconds of window getting displayed
DISPLAY_DURATION=2500 

# this will get set in order to keep this obj. alive while the user interacts with it.
LIVING_ID = False 

class VolDisplay(Gtk.Window):
    """ Tiny window for displaying the current system master volume. """

    def __init__(self):
        Gtk.Window.__init__(self, type = Gtk.WindowType.POPUP)
        self.set_border_width(15)
        self.set_default_size(50, 230)
        self.set_decorated(False)
        self.move(80, 200) # distance to top left corner
        self.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse("#222")) ## little greyish


        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(vbox)
        self.volumeBar = Gtk.ProgressBar()
        self.volumeBar.set_orientation(Gtk.Orientation.VERTICAL)
        self.volumeBar.set_inverted(True)
        self.volumeBar.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.3, 0.5, 0.85, 0.25))
        vbox.pack_end(self.volumeBar, True, True, 0)


        self.masterVol = False
        self.masterMute = False
        
        self.label = Gtk.Label()
        vbox.pack_start(self.label, False, True, 8)

        self.updateVolumeBar()

    
    def updateVolumeBar(self):
        """ Updates the volume in the bar. """
        self.mixer = alsaaudio.Mixer()
        volumes = self.mixer.getvolume()
        mutes = self.mixer.getmute()

        # update on changes and prolong living time of self.
        if self.masterVol != volumes[0]:
            self.masterVol = volumes[0]
            self.prolongLiving()

        if self.masterMute != mutes[0]:
            self.masterMute = mutes[0]
            self.prolongLiving()

        if(self.masterMute == 1):
            self.volumeBar.set_fraction(0)
            self.label.set_markup("<span foreground='white' size='small'>0</span>")
        else:
            self.volumeBar.set_fraction(self.masterVol/100)
            if(self.masterVol == 100):
                self.label.set_markup("<span foreground='white' size='xx-small'>" + str(self.masterVol) + "</span>")
            else:
                self.label.set_markup("<span foreground='white' size='small'>" + str(self.masterVol) + "</span>")



        return True

    def prolongLiving(self):
        """ Prolongs the living time of this object. Therefore, the LIVING_ID will get removed from the timeout manager and 
            will get replaced by a new one. """
        global LIVING_ID, DISPLAY_DURATION
        if(LIVING_ID):
            GObject.source_remove(LIVING_ID)
            LIVING_ID = GObject.timeout_add(DISPLAY_DURATION, destroyWindow)


def constructWindow():
    """ construct a window and place pid file. Note the timeout ID in LIVING_ID global var."""
    global LIVING_ID, DISPLAY_DURATION

    # add self destruction after DISPLAY_DURATION milliseconds
    LIVING_ID = GObject.timeout_add(DISPLAY_DURATION, destroyWindow)
    
    open(MY_TEMP_PATH, 'w').write(str(os.getpid()))
    window = VolDisplay()
    window.connect("delete-event", Gtk.main_quit)
    window.show_all()

    # poll volume all xxx milliseconds
    GObject.timeout_add(50, window.updateVolumeBar)

    Gtk.main()


def destroyWindow():
    """ Rules for destroying the window. Remove pid file and exit gtk main loop. """
    os.remove(MY_TEMP_PATH)
    Gtk.main_quit()

if not os.path.exists(MY_TEMP_PATH):
    constructWindow()

else:
    pid = int(open(MY_TEMP_PATH).read())
    try:
        #check if pid is running:
        os.kill(pid, 0) 
    except OSError:
        # is not running, stale temp file found...... however:
        constructWindow()
    else:
        # is running! do nothing
        exit()




