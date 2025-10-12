#!/usr/bin/env python



# !SECTION! Importing modules

from i3ipc import Connection, Event
from subprocess import Popen
from time import sleep
import os
from pathlib import Path
import pickle
import toml


# !SECTION! Constants

# The variable storing the connection with i3/sway
WM = Connection()

# Constants used to store information about a workspace's visibility
FOCUSED = "FOCUSED"
FOCUSED_LEVEL = "FOCUSED_LEVEL"
VISIBLE_LEVEL_OTHER_OUTPUT = "VISIBLE_LEVEL_OTHER_OUTPUT"
NOT_VISIBLE_CURRENT_OUTPUT = "NOT_VISIBLE_CURRENT_OUTPUT"
NOT_VISIBLE_OTHER_OUTPUT = "NOT_VISIBLE_OTHER_OUTPUT"

# Constants used to decide whether a preparation should continue or stop
KEEP_GOING = True
DONE = False

default_config_path = Path.home() / ".etabli_config.toml"


# !SECTION! Parsing configuration file

DEFAULTS = {
    "board_path" : Path.home() / ".etabli_board",
    "separator" : "/",
    "notif_title" : "Etabli prepares...",
    "hrule" : "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯",
    "default_workspace_name" : "0",
    "theme": {
        "sp" : {
            "FOCUSED": "#C00000",
            "FOCUSED_LEVEL": "#252525",
            "VISIBLE_LEVEL_OTHER_OUTPUT":  "#707070",
            "NOT_VISIBLE_CURRENT_OUTPUT":  "#DDDDDD",
            "NOT_VISIBLE_OTHER_OUTPUT":  "#DDDDDD",
        },
        "lvl" : {
            "FOCUSED": "#883333",
            "FOCUSED_LEVEL": "#883333",
            "VISIBLE_LEVEL_OTHER_OUTPUT" : "#252525",
            "NOT_VISIBLE_CURRENT_OUTPUT" : "#707070",
            "NOT_VISIBLE_OTHER_OUTPUT": "#707070",
        },
        "sbl" : {
            "FOCUSED": "#330000",
            "FOCUSED_LEVEL": "#330000",
            "VISIBLE_LEVEL_OTHER_OUTPUT": "#883333",
            "NOT_VISIBLE_CURRENT_OUTPUT": "#DDDDDD",
            "NOT_VISIBLE_OTHER_OUTPUT": "#DDDDDD",
        },
        "dlm": {
            "open": "[",
            "closed": "]",
        },
        "brd" : {
            "color": "#00FFAA",
            "open": "{",
            "closed": "}",
        }
    }

}


class EtabliHandler:
    def __init__(self, path=Path.home() / ".etabli.toml"):
        path = Path(path).expanduser()
        with open(Path(path), "r") as f:
            # reading configuration file
            self.conf = toml.loads(f.read())
            # setting all defaults that were not set
            for k in DEFAULTS:
                if k not in self.conf:
                    self.conf[k] = DEFAULTS[k]

                    
    def __getitem__(self, x):
        return self.conf[x]

    
    def __contains__(self, x):
        return x in self.conf

    
    def format_workspace_name(self, name, index):
        if index == "0":
            return name
        else:
            return "{}{}{}".format(name,
                                   self.conf["separator"],
                                   index)

        
    def split_workspace_name(self, sp_name):
        if self.conf["separator"] in sp_name:
            splitted = sp_name.split(self.conf["separator"])
            return (splitted[0], splitted[1])
        else:
            return (sp_name, self.conf["default_workspace_name"])



# !SECTION! Helper functions

def current_workspace_name():
    for sp in WM.get_workspaces():
        if sp.focused:
            return sp.name
    raise Exception("somehow, no workspace was found!")


def current_workspace_is_empty():
    root = WM.get_tree()
    for con in root:
        if con.name == current_workspace_name():
            if len(con.descendants()) == 0:
                return True
            else:
                return False
    raise Exception("current workspace couldn't be identified")


def focus_workspace(ws):
    WM.command("workspace {}".format(ws))

    
def current_output():
    for o in WM.get_outputs():
        if o.focused:
            return o.name
    raise Exception("no active output found!")



# !SECTION! Helpers for rofi interaction

def print_potential_preparations(conf):
    current_level = conf.split_workspace_name(current_workspace_name())[0]
    if "prepare" in conf:
        for shortcut in conf["prepare"]:
            print("Prepare {}".format(conf.format_workspace_name(
                current_level,
                shortcut
            )))

                   

# !SECTION! A small test

if __name__ == "__main__":
    c = EtabliHandler("./data.toml")
    print(c.conf)

