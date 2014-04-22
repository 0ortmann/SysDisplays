#!/usr/bin/python

import alsaaudio
import os  # for instance management
from gi.repository import Gtk, Gdk, GObject
import sys  # parameter parsing

# directory where the acpi / intel backlight control is sourced
BACKLIGHT_DIR = "/sys/class/backlight/acpi_video0/"

# files containing these values (they have to be found under BACKLIGHT_DIR):
ACTUAL_KEY = "actual_brightness"
MAXIMUM_KEY = "max_brightness"

# path to a temporary file for a pid.
MY_BACKLIGHT_PATH = "/tmp/backlight_display_running.tmp"
# path to a temporary file for a pid.
MY_VOL_PATH = "/tmp/volume_display_running.tmp"

# milliseconds of window getting displayed
DISPLAY_DURATION = 2500

# this will get set in order to keep this obj. alive while the user
# interacts with it.
LIVING_ID = False


class BarDisplay(Gtk.Window):

    """ Tiny popup window for displaying some value in a progress bar. """

    def __init__(self, xdist, ydist):
        Gtk.Window.__init__(self, type=Gtk.WindowType.POPUP)

        self._initFields()

        self.set_border_width(15)
        self.set_default_size(50, 230)
        self.set_decorated(False)
        self.move(xdist, ydist)  # distance to top left corner
        # little greyish
        self.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse("#222"))

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(vbox)
        self.volumeBar = Gtk.ProgressBar()
        self.volumeBar.set_orientation(Gtk.Orientation.VERTICAL)
        self.volumeBar.set_inverted(True)
        self.volumeBar.override_background_color(
            Gtk.StateFlags.NORMAL, Gdk.RGBA(0.1, 0.9, 0.5, 0.35))
        vbox.pack_end(self.volumeBar, True, True, 0)

        self.label = Gtk.Label()
        vbox.pack_start(self.label, False, True, 8)

        self.updateBar()

    def _initFields(self):
        """ Initialises the current and the max val fields for this display bar."""
        pass

    def updateBar(self):
        """ Updates the value in the bar """
        pass

    def prolongLiving(self):
        """ Prolongs the living time of this object. Therefore, the LIVING_ID will get removed from the timeout manager and 
            will get replaced by a new one. """
        global LIVING_ID, DISPLAY_DURATION
        if(LIVING_ID):
            GObject.source_remove(LIVING_ID)
            LIVING_ID = GObject.timeout_add(
                DISPLAY_DURATION, destroyWindow, self.windowType)

    def setColors(self, background, barR, barG, barB, barA):
        """ Set the colors for this windows background and the bar """
        self.volumeBar.override_background_color(
            Gtk.StateFlags.NORMAL, Gdk.RGBA(barR, barG, barB, barA))
        self.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse(background))


class BacklightDisplay(BarDisplay):

    """ Tiny window for displaying the current system screen brightness. """

    def __init__(self):
        super().__init__(150, 200)
        self.setColors("#222", 0.1, 0.9, 0.5, 0.35)

    def _initFields(self):
        """ Initialises the special fields for this display bar."""

        self.windowType = "backlight"

        global BACKLIGHT_DIR, MAXIMUM_KEY

        self.brightness = 0
        self.max = int(open(BACKLIGHT_DIR + MAXIMUM_KEY).read())

    def updateBar(self):
        """ Updates the value in the bar. """
        global BACKLIGHT_DIR, ACTUAL_KEY

        brightness = int(open(BACKLIGHT_DIR + ACTUAL_KEY).read())

        # update on changes and prolong living time of self.
        if self.brightness != brightness:
            self.brightness = brightness
            self.prolongLiving()

        self.volumeBar.set_fraction(self.brightness / self.max)
        self.label.set_markup(
            "<span foreground='white' size='small'>" + str(self.brightness) + "</span>")

        return True


class VolDisplay(BarDisplay):

    """ Tiny window for displaying the current system master volume. """

    def __init__(self):
        super().__init__(80, 200)
        self.setColors("#222", 0.3, 0.5, 0.85, 0.25)

    def _initFields(self):
        """ Initialises the special fields for this display bar."""
        self.windowType = "volume"

        self.masterVol = 0
        self.masterMute = 0

    def updateBar(self):
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
            self.label.set_markup(
                "<span foreground='white' size='small'>0</span>")
        else:
            self.volumeBar.set_fraction(self.masterVol / 100)
            if(self.masterVol == 100):
                self.label.set_markup(
                    "<span foreground='white' size='xx-small'>" + str(self.masterVol) + "</span>")
            else:
                self.label.set_markup(
                    "<span foreground='white' size='small'>" + str(self.masterVol) + "</span>")

        return True


def constructWindow(windowType):
    """ construct a window and place pid file. Note the timeout ID in LIVING_ID global var."""
    global LIVING_ID, DISPLAY_DURATION

    # add self destruction after DISPLAY_DURATION milliseconds
    LIVING_ID = GObject.timeout_add(
        DISPLAY_DURATION, destroyWindow, windowType)

    if windowType == "volume":
        open(MY_VOL_PATH, 'w').write(str(os.getpid()))
        window = VolDisplay()
    elif windowType == "backlight":
        open(MY_BACKLIGHT_PATH, 'w').write(str(os.getpid()))
        window = BacklightDisplay()

    window.connect("delete-event", Gtk.main_quit)
    window.show_all()

    # poll volume all xxx milliseconds
    GObject.timeout_add(50, window.updateBar)

    Gtk.main()


def destroyWindow(windowType):
    """ Rules for destroying the window. Remove pid file and exit gtk main loop. """
    if windowType == "volume":
        os.remove(MY_VOL_PATH)

    elif windowType == "backlight":
        os.remove(MY_BACKLIGHT_PATH)
    Gtk.main_quit()


path = ""
if sys.argv[1] == "volume":
        path = MY_VOL_PATH

elif sys.argv[1] == "backlight":
        path = MY_BACKLIGHT_PATH


if not os.path.exists(path):
    constructWindow(sys.argv[1])

else:
    pid = int(open(path).read())
    try:
        # check if pid is running:
        os.kill(pid, 0)
    except OSError:
        # is not running, stale temp file found...... however:
        constructWindow(sys.argv[1])
    else:
        # is running! do nothing
        exit()
