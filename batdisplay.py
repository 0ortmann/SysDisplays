#!/usr/bin/python

import os  # for instance management
from gi.repository import Gtk, Gdk, GObject

# milliseconds of window getting displayed
DISPLAY_DURATION = 4000

# this will get set in order to keep this obj. alive while
LIVING_ID = False

# path to a temporary file for a pid.
MY_BAT_WARNING_PATH = "/tmp/battery_warning_active.tmp"

WARNING_TEXT = "Idiot, ur battery is dying!"


class WarningDisplay(Gtk.Window):

    def __init__(self, xdist, ydist):
        Gtk.Window.__init__(self, type=Gtk.WindowType.POPUP)

        self.set_border_width(15)
        self.set_default_size(300, 70)
        self.set_decorated(False)
        self.move(xdist, ydist)  # distance to top left corner
        # little greyish
        self.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse("#222"))

        hbox = Gtk.Box(spacing=20)
        self.add(hbox)
        self.label = Gtk.Label(WARNING_TEXT)
        self.label.set_markup(
            '<span foreground="#00FFCC" size="medium" face="cursive">' + WARNING_TEXT + '</span>')

        hbox.pack_start(self.label, True, True, 0)


def constructWindow():
    """ construct a window and place pid file. Note the timeout ID in LIVING_ID global var."""
    global LIVING_ID, DISPLAY_DURATION

    # add self destruction after DISPLAY_DURATION milliseconds
    LIVING_ID = GObject.timeout_add(DISPLAY_DURATION, destroyWindow)

    open(MY_BAT_WARNING_PATH, 'w').write(str(os.getpid()))
    window = WarningDisplay(50, 125)

    window.connect("delete-event", Gtk.main_quit)
    window.show_all()

    Gtk.main()


def destroyWindow():
    """ Rules for destroying the window. Remove pid file and exit gtk main loop. """
    os.remove(MY_BAT_WARNING_PATH)
    Gtk.main_quit()


if not os.path.exists(MY_BAT_WARNING_PATH):
    constructWindow()

else:
    pid = int(open(MY_BAT_WARNING_PATH).read())
    try:
        # check if pid is running:
        os.kill(pid, 0)
    except OSError:
        # is not running, stale temp file found...... however:
        constructWindow()
    else:
        # is running! do nothing
        exit()
