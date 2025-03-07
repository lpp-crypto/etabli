#!/usr/bin/env python

from i3ipc import Connection, Event
from subprocess import Popen
from time import sleep
from sys import argv

#from workspace_commands import *

SWAY = Connection()
SEPARATOR = "/"
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
    

# !SUBSECTION! Dealing with levels 

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
            

# !SECTION! Creating new workspaces
    
def launch_chain(instructions):
    result = KEEP_GOING
    for inst in instructions:
        result = inst()
        if result == DONE:
            return DONE
    return KEEP_GOING


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

def cycle_workspace_in_level(amount):
    current_name = current_workspace_name()
    current, index = split_workspace_name(current_name)
    current_level = get_level(current)
    next_space = current_level[
        (current_level.index((current, index)) + amount) % len(current_level)
    ]
    focus_workspace(format_workspace_name(next_space[0], next_space[1]))


def next_workspace_in_level():
    cycle_workspace_in_level(1)

    
def previous_workspace_in_level():
    cycle_workspace_in_level(-1)

        
def new_workspace_in_level():
    current, index = split_workspace_name(current_workspace_name())
    current_level = get_level(current)
    for i in range(0, len(current_level)+1):
        if (current, str(i)) not in current_level:
            focus_workspace(format_workspace_name(current, str(i)))
            break


# !SECTION! Sorting workspaces

def current_output():
    for o in SWAY.get_outputs():
        if o.focused:
            return o.name
    raise Exception("no active output found!")


def workspaces_in_current_output():
    c_o = current_output()
    result = []
    for sp in SWAY.get_workspaces():
        if sp.output == c_o:
            result.append( sp.name )
    result.sort(key=str.casefold) # to have case insensitive sorting
    return result


def cycle_workspace_in_output(amount):
    names = workspaces_in_current_output()
    current_name = current_workspace_name()
    focus_workspace(names[(names.index(current_name)+amount) % len(names)])

        
def next_workspace():
    cycle_workspace_in_output(1)

    
def prev_workspace():
    cycle_workspace_in_output(-1)


# !SECTION! Utilities 

def print_workspaces_in_current_output():
    names = workspaces_in_current_output()
    for n in names:
        print(n)

def print_workspaces():
    names = [o.name for o in SWAY.get_workspaces()]
    names.sort(key=str.casefold) # to have case insensitive sorting
    for n in names:
        print(n)
        

# !SECTION! Main program 

if __name__ == "__main__":
    # general cycling
    if argv[1] == "next_workspace":
        next_workspace()
    elif argv[1] == "prev_workspace":
        prev_workspace()
    # by level
    elif argv[1] == "next_workspace_in_level":
        next_workspace_in_level()
    elif argv[1] == "previous_workspace_in_level":
        previous_workspace_in_level()
    elif argv[1] == "new_workspace_in_level":
        new_workspace_in_level()
    # general utilities
    elif argv[1] == "get_workspaces_in_output":
        print_workspaces_in_output()
    elif argv[1] == "get_workspaces":
        print_workspaces()
    elif argv[1] == "current_workspace":
        print(current_workspace_name())
    else:
        raise Exception("unknown input: {}".format(argv[1]))

    # !TODO! change logic: win+horizontal arrows cycles within a level, vertical arrows cycles between levels 


    # !TODO! take current output into account when cycling


