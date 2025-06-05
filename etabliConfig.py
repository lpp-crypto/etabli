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
            cmd += ["--daemon={}".format(daemon_name)] 
            try:
                p = Popen(cmd)
                EDITOR_SESSIONS[daemon_name] = p.pid
                LOG.info("Ran {}; pid={}".format(cmd, p.pid))
            except:
                LOG.error("Couldn't run {}".format(cmd))
        else:
            LOG.info("Chose not to start emacs server {}".format(daemon_name))


# !SECTION! Describeing the mapping between level names and the functions that must be run when they are created

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

# !TODO! add something to "re-attach" loose emacs servers 



# !SECTION!  Suggesting a name for a workspace within a level

def rename_workspace_by_guessing():
    focused = SWAY.get_tree().find_focused()
    # finding potential name, modify this part to have other names!
    new_name = "New"
    if "emacs" in focused.app_id:
        current_file_extension = focused.name.split(".")[-1]
        if "tex" in current_file_extension:
            new_name = "writing"
        elif "org" in current_file_extension:
            new_name = "org"
        else:
            new_name = "code"
    elif "kitty" in focused.app_id:
        new_name = "term"
    elif "firefox" in focused.app_id:
        if "youtube" in focused.name.lower():
            new_name = "youtube"
        else:
            new_name = "firefox"
    elif "evince" in focused.app_id:
        new_name = "pdf"
    elif "rhythmbox" in focused.app_id:
        new_name = "music"
    # ensuring that it is not already taken
    current_level = current_level_name()
    current_level_content = [x[1] for x in get_level(current_level)]
    if new_name in current_level_content:
        diversifier = 0
        potential_new_name = new_name
        while potential_new_name in current_level_content:
            diversifier += 1
            potential_new_name = new_name + "-{:d}".format(diversifier)
        new_name = potential_new_name
    SWAY.command("rename workspace to {}".format(
        format_workspace_name(current_level, new_name)
    ))


# !SECTION! Testing
    
if __name__ == "__main__":
    rename_workspace_by_guessing()
