#!/usr/bin/env python

from etabliLib import *
from etabliOrg import *
from emacsServerHandler import *



# !SECTION! Configuration


# !SUBSECTION! Style of the waybar widget


# !SUBSUBSECTION! Style descriptions

grey_red_theme = {
    "sp" : {
        "FOCUSED": "#C00000",
        "SAME_LEVEL": "#252525",
        "SAME_OUTPUT":  "#707070",
        "OTHER_OUTPUT":  "#DDDDDD",
    },
    "lvl" : {
        "FOCUSED": "#883333",
        "SAME_OUTPUT": "#252525",
        "OTHER_OUTPUT": "#707070",
    },
    "sbl" : {
        "ACTIVE": "#C00000",
        "INACTIVE": "#DDDDDD",
    }
}


thm = grey_red_theme # <---- change this to change the color_scheme


# !SUBSUBSECTION! Style application functions

def open_level(level_name, symbol_color, name_color):
    delimiter = " <span color=\"{}\">[</span>".format(symbol_color)
    return delimiter + "<span color=\"{}\" style=\"bold\">{}</span>".format(
        name_color,
        level_name
    )


def open_visible_level(level_name):
    return open_level(level_name,
                      thm["sbl"]["ACTIVE"],
                      thm["lvl"]["ACTIVE"])


def open_current_output_level(level_name):
    return open_level(level_name,
                      thm["sbl"]["INACTIVE"],
                      thm["lvl"]["SAME_OUTPUT"])


def open_other_output_level(level_name):
    return open_level(level_name,
                      thm["sbl"]["INACTIVE"],
                      thm["lvl"]["OTHER_OUTPUT"])


def close_level(symbol_color):
    return "<span color=\"{}\">]</span>".format(symbol_color)


def close_visible_level():
    return close_level(thm["sbl"]["ACTIVE"])


def close_current_output_level():
    return close_level(thm["sbl"]["SAME_LEVEL"])


def close_other_output_level():
    return close_level(thm["sbl"]["INACTIVE"])



def style_workspace(sp_name, color):
    return "<span color=\"{}\">{}</span>".format(color, sp_name)


def current_workspace(sp_name):
    return style_workspace(thm["sp"]["ACTIVE"], sp_name)


def current_level_workspace(sp_name):
    return style_workspace(thm["sp"]["CURRENT_LEVEL"], sp_name)


def same_output_workspace(sp_name):
    return style_workspace(thm["sp"]["SAME_OUTPUT"], sp_name)


def other_output_workspace(sp_name):
    return style_workspace(thm["sp"]["OTHER_OUTPUT"], sp_name)



# !SUBSECTION! Describing the mapping between level names and the functions that must be run when they are created


launch_table = {
    "firefox" : [IfEmpty(),
                 Notification("Firefox web browser"),
                 SHexec(["firefox"]), ],
    "emacs" : [IfEmpty(),
               Notification("Starting EMACS Server"),
               EmacsServer(additional_args=["--funcall=basic-theme"]),
               SetLevelVar("emacs")
               ],
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



# !SUBSECTION!  Suggesting a name for a workspace within a level

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
    s = SetLevelVar("test")
    e = EmacsServer(additional_args=["--funcall=basic-theme"],
                  daemon_name="blublu")
    s(e(None))
