#!/usr/bin/env python

from etabliLib import *
from etabliOrg import *

EDITOR = "sh ~/new-emacs/scripts/editor"

EDITOR_SESSIONS = {}

class StartEmacsServerInLevel:
    def __init__(self):
        self.command = EDITOR + " --daemon={}"

    def __call__(self):
        cur_lev = current_level_name()
        print(EDITOR_SESSIONS)
        if cur_lev not in EDITOR_SESSIONS:
            cmd = self.command.format(current_level_name())
            print(cmd)
            p = Popen(cmd, shell=True)
            EDITOR_SESSIONS[cur_lev] = p.pid

            # !TODO! create an etabli log 


launch_table = {
    "firefox" : [IfEmpty(),
                 Notification("Firefox web browser"),
                 SHexec("firefox"), ],
    "emacs" : [IfEmpty(),
               Notification("Starting EMACS Server"),
               StartEmacsServerInLevel()],
    "civ" : [IfEmpty(),
             Notification("Steam and Civilisation V"),
             SHexec("steam steam://rungameid/8930")],
    "comms" : [
        IfEmpty(),
        Notification("All communications apps"),
        Tiling((
            [SHexec("thunderbird"),
             SHexec('signal-desktop --password-store="gnome-libsecret"')
             ],
            SHexec("chromium-browser https://naro.brute-force.eu/element/#/home")
        ))
    ]
}



