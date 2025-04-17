#!/usr/bin/env python
# Time-stamp: <2025-04-17 11:35:02>



# !SECTION! Set up

# !SUBSECTION! Importing modules 

from i3ipc import Connection, Event
from subprocess import Popen
from time import sleep
from sys import argv


# !SUBSECTION! Defining global variables and constants 

SWAY = Connection()
SEPARATOR = "/"
KEEP_GOING = True
DONE = False

NOTIF_TITLE="Etabli prepares..."
HRULE="⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯"


# !SECTION! Dealing with workspaces and their levels

def give_time():
    sleep(0.5)
    

def focus_workspace(name):
    SWAY.command("workspace {}".format(name))


def all_workspaces():
    return [sp.name for sp in SWAY.get_workspaces()]

    
def current_workspace_name():
    for sp in SWAY.get_workspaces():
        if sp.focused:
            return sp.name
    raise Exception("somehow, no workspace was found!")
    
    
def current_level_name():
    for sp in SWAY.get_workspaces():
        if sp.focused:
            if SEPARATOR in sp.name:
                return split_workspace_name(sp.name)[0]
            else:
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
    sp_in_level = []
    for sp in SWAY.get_workspaces():
        if name in sp.name:
            sp_in_level.append(split_workspace_name(sp.name))
    level_sp_by_names = {entry[1] : entry for entry in sp_in_level}
    result = []
    for l in sorted(level_sp_by_names.keys(), key=str.casefold):
        result.append(level_sp_by_names[l])
    return result
            

# !SUBSECTION! Cycling within a level of workspaces

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

    
def prev_workspace_in_level():
    cycle_workspace_in_level(-1)

        
def new_workspace_in_level():
    current, index = split_workspace_name(current_workspace_name())
    current_level = get_level(current)
    for i in range(0, len(current_level)+1):
        if (current, str(i)) not in current_level:
            focus_workspace(format_workspace_name(current, str(i)))
            break


# !SUBSECTION! Sorting workspaces

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




# !SECTION! Preparing workspaces/full levels


def launch_chain(instructions):
    result = KEEP_GOING
    for inst in instructions:
        result = inst()
        if result == DONE:
            return DONE
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

    def __str__(self):
        return "sh {}".format(self.command)

    
class Notification:
    def __init__(self, content):
        self.content = content
        self.inner_command = SHexec(
            "notify-send '{}' '{}' -t 3000".format(
                NOTIF_TITLE,
                self.content
            ))

    def __call__(self):
        self.inner_command()

    def __str__(self):
        return "notification: " + self.content
        
    
    
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


def is_current_workspace_empty():
    root = SWAY.get_tree()
    for con in root:
        if con.name == current_workspace_name():
            if len(con.descendants()) == 0:
                return True
            else:
                return False
    raise Exception("current workspace couldn't be identified")


class IfEmpty:
    def __init__(self):
        pass

    def __call__(self):
        if is_current_workspace_empty():
            return KEEP_GOING
        else:
            return DONE

        
# !SECTION! Dealing with windows

def print_all_windows():
    root = SWAY.get_tree()
    rows = []
    for con in root:
        if len(con.descendants()) == 0:
            rows.append([con.workspace().name, con.name])
    rows.sort()
    max_length = 0
    for x in rows:
        max_length = max(max_length, len(x[0]))
    template = "{:" + str(max_length) + "s}\t{}"
    for x in rows:
        print(template.format(x[0], x[1]))

        
def focus_window(name):
    root = SWAY.get_tree()
    rows = []
    for con in root:
        if con.name == name:
            #print("focusing on {} ({}) {}".format(name, con.id, con.window_title))
            SWAY.command("[con_id={}] focus".format(con.id))
            
            break
          

if __name__ == "__main__":
    i = IfEmpty()
    i()
