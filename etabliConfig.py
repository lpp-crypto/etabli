#!/usr/bin/env python

from etabliLib import *
from etabliOrg import *

EDITOR = ["sh", Path.home() / "new-emacs/scripts/editor"]

EDITOR_SESSIONS = {}

class StartEmacsServer:
    def __init__(self, daemon_name=None, additional_args=[]):
        self.editor = EDITOR
        self.daemon_name = daemon_name
        self.additional_args = additional_args

    def __call__(self):
        if self.daemon_name == None:
            daemon_name = current_level_name()
        else:
            daemon_name = self.daemon_name
        if daemon_name not in EDITOR_SESSIONS:
            cmd = self.editor + self.additional_args
            cmd += ["--daemon={}".format(self.daemon_name)] 
            try:
                p = Popen(cmd)
                EDITOR_SESSIONS[daemon_name] = p.pid
                LOG.info("Ran {}; pid={}".format(cmd, p.pid))
            except:
                LOG.error("Couldn't run {}".format(cmd))
        else:
            LOG.info("Chose not to start emacs server {}".format(daemon_name))


# !SECTION! The following table describes the mapping between level names and the functions that must be run when they are created

launch_table = {
    "firefox" : [IfEmpty(),
                 Notification("Firefox web browser"),
                 SHexec(["firefox"]), ],
    "emacs" : [IfEmpty(),
               Notification("Starting EMACS Server"),
               StartEmacsServer(additional_args=["--funcall=basic-theme"])],
    "steam" : [IfEmpty(),
             Notification("Steam and Civilisation V"),
             #SHexec("steam steam://rungameid/8930")], # starting civ
             SHexec(["steam"])],
    "comms" : [
        IfEmpty(),
        Notification("All communications apps"),
        Tiling((
            [SHexec(["thunderbird"]),
             SHexec(['signal-desktop', '--password-store=gnome-libsecret'])
             ],
            SHexec(["chromium-browser", "https://naro.brute-force.eu/element/#/home"])
        ))
    ]
}




if __name__ == "__main__":
    s = StartEmacsServer(daemon_name="test1")
    s()
    LOG.info("bleeeh")
