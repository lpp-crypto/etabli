#!/usr/bin/env python

from i3ipc import Connection
from subprocess import Popen
from time import sleep
from sys import argv

from workspace_commands import *

SWAY = Connection()
SEPARATOR = "~"
KEEP_GOING = True
DONE = False


# !SECTION! Basic utilities

def give_time():
    sleep(0.5)
    

def focus_workspace(name):
    SWAY.command("workspace {}".format(name))

    
def current_workspace_name():
    for sp in SWAY.get_workspaces():
        if sp.focused:
            return sp.name
    raise Exception("somehow, no workspace was found!")
    
    
def launch_chain(instructions):
    result = KEEP_GOING
    for inst in instructions:
        result = inst()
        if result == DONE:
            return DONE
    return KEEP_GOING



# !SECTION! Creating new workspaces

class NewWorkspaceIfNotExists:
    def __init__(self, name):
        self.name = name

    def __call__(self):
        for sp in SWAY.get_workspaces():
            if self.name == sp.name:
                focus_workspace(self.name)
                return DONE
        focus_workspace(self.name)
        return KEEP_GOING
    

class SHexec:
    def __init__(self, command):
        self.command = command

    def __call__(self):
        try:
            Popen(self.command, shell=True)
            return KEEP_GOING
        except:
            return DONE


class Tiling:
    def __init__(self, config):
        self.config = config

    def process_tiles(self, entry):
        if isinstance(entry, list):
            for tile in entry:
                self.process_tiles(tile)
                give_time()
                SWAY.command("splitv")
        elif isinstance(entry, tuple):
            for tile in entry:
                self.process_tiles(tile)
                give_time()
                SWAY.command("splith")
        else:
            entry()
    
    def __call__(self):
        self.process_tiles(self.config)


# !SECTION! Cycling within a level of workspaces

def format_workspace_name(name, index):
    if index == "0":
        return name
    else:
        return "{}{}{}".format(name, SEPARATOR, index)
    

def split_workspace_name(sp_name):
    if SEPARATOR in sp_name:
        splitted = sp_name.split(SEPARATOR)
        return (splitted[0], splitted[1])
    else:
        return (sp_name, "0")

    
def get_level(name):
    result = []
    for sp in SWAY.get_workspaces():
        if name in sp.name:
            result.append(split_workspace_name(sp.name))
    result.sort()
    return result
            

def next_workspace_in_level():
    current_name = current_workspace_name()
    current, index = split_workspace_name(current_name)
    current_level = get_level(current)
    pos = 0
    while (current, index) != current_level[pos]:
        pos += 1
    next_space = current_level[(pos + 1) % len(current_level)]
    focus_workspace(format_workspace_name(next_space[0], next_space[1]))
    

    
    
def previous_workspace_in_level():
    current_name = current_workspace_name()
    current, index = split_workspace_name(current_name)
    current_level = get_level(current)
    pos = 0
    while (current, index) != current_level[pos]:
        pos += 1
    next_space = current_level[(pos - 1) % len(current_level)]
    focus_workspace(format_workspace_name(next_space[0], next_space[1]))
    

        
def new_workspace_in_level():
    current, index = split_workspace_name(current_workspace_name())
    current_level = get_level(current)
    for i in range(0, len(current_level)+1):
        if (current, i) not in current_level:
            focus_workspace(format_workspace_name(current, i))


# !SECTION! Main program 

if __name__ == "__main__":
    if argv[1] == "next_workspace_in_level":
        next_workspace_in_level()
    elif argv[1] == "previous_workspace_in_level":
        previous_workspace_in_level()
    elif argv[1] == "new_workspace_in_level":
        new_workspace_in_level()
    
