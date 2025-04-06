#!/usr/bin/env python

from etabliLib import *
from etabliOrg import *


# !TODO! add to the input of rofi entries that will create a new prepared workspace 

launch_table = {
    "firefox" : [Notification("Firefox web browser"),
                 SHexec("firefox"), ],
    "emacs" : [Notification("EMACS"),
               SHexec("emacs")],
    "civ" : [Notification("Steam and Civilisation V"),
             SHexec("steam steam://rungameid/8930")],
    "comms" : [
        Notification("All communications apps"),
        Tiling((
            [SHexec("thunderbird"),
             SHexec('signal-desktop --password-store="gnome-libsecret"')
             ],
            SHexec("chromium-browser https://naro.brute-force.eu/element/#/home")
        ))
    ]
}



