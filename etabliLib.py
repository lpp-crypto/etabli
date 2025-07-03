#!/usr/bin/env python



# !SECTION! Set up

# !SUBSECTION! Importing modules

from i3ipc import Connection, Event
from subprocess import Popen
from time import sleep
from sys import argv
import logging
import os
from pathlib import Path
import pickle

# !SUBSECTION! Defining global variables and constants 

SWAY = Connection()
SEPARATOR = "/"
KEEP_GOING = True
DONE = False

NOTIF_TITLE="Etabli prepares..."
HRULE="⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯"


MAIN_SHELF_PATH = Path.home() / "etabli/shelf/db"


# !SUBSECTION! Setting up logging 

logging.basicConfig(filename='log.log',
                    encoding='utf-8',
                    level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')
LOG = logging.getLogger(__name__)


# !SECTION! Dealing with workspaces and their levels

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
    

def is_current_workspace_empty():
    root = SWAY.get_tree()
    for con in root:
        if con.name == current_workspace_name():
            if len(con.descendants()) == 0:
                return True
            else:
                return False
    raise Exception("current workspace couldn't be identified")


# !SUBSECTION! Dealing with levels

# !TODO! functions to cycle through levels 


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
            

# !SUBSECTION! Cycling workspaces

# !SUBSUBSECTION!  Within a level

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
    for i in range(1, len(current_level)+2):
        if (current, str(i)) not in current_level:
            focus_workspace(format_workspace_name(current, str(i)))
            break

# !SUBSUBSECTION! Whole levels 

# !TODO! the Etabli class from [[./waybar_daemon.py]] should probably be moved here, and used for the cycling operations

def cycle_level(amount):
    levels_in_output = {}
    c_o = current_output()
    for sp in SWAY.get_workspaces():
        if sp.output == c_o:
            lev, index = split_workspace_name(sp.name)
            if lev in levels_in_output:
                levels_in_output[lev].append(sp.name)
            else:
                levels_in_output[lev] = [ sp.name ]
        if sp.focused:
            c_s = sp.name
    sorted_levels = []
    c_i = None
    for lev in sorted(levels_in_output.keys(), key=str.casefold):
        sorted_levels.append(levels_in_output[lev])
        sorted_levels[-1].sort()
        if c_s in sorted_levels[-1]:
            c_i = len(sorted_levels) - 1
    focus_workspace(sorted_levels[(c_i + amount) % len(sorted_levels)][0])

    
def next_level():
    cycle_level(1)
    
def prev_level():
    cycle_level(-1)


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



def name_workspace_in_level(amount):
    current_name = current_workspace_name()
    current, index = split_workspace_name(current_name)
    current_level = get_level(current)
    next_space = current_level[
        (current_level.index((current, index)) + amount) % len(current_level)
    ]
    return format_workspace_name(next_space[0], next_space[1])


def name_next_workspace_in_level():
    return name_workspace_in_level(1)

    
def name_prev_workspace_in_level():
    return name_workspace_in_level(-1)

        
def name_new_workspace_in_level():
    current, index = split_workspace_name(current_workspace_name())
    current_level = get_level(current)
    for i in range(1, len(current_level)+1):
        if (current, str(i)) not in current_level:
            return format_workspace_name(current, str(i))



        
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

# !TODO!  add tools to automatically set whether the next window will be added horizontally or vertically


        
# !SECTION! =Prepare= utilities



# !SUBSECTION! Attaching variables to levels

class EtabliShelf:
    def __init__(self, shelf_path):
        self.path = shelf_path
        try:
            with open(self.path, "rb") as file:
                self.db = pickle.load(file)
        except:
            self.db = {}

            
    def __enter__(self):
        return self

    
    def save(self):
        with open(self.path, "wb+") as file:
            pickle.dump(self.db, file)
            file.flush()


    def __exit__(self, exc_type, exc_value, traceback):
        self.save()
        
                
    def __call__(self, lev):
        if lev in self.db.keys():
            return self.db[lev]
        else:
            return {}

    
    def get(self, lev, key):
        if lev not in self.db.keys():
            return ""
        elif key not in self.db[lev]:
            return ""
        else:
            return self.db[lev][key]

        
    def set(self, lev, key, val):
        str_key = str(key)
        if lev not in self.db.keys():
            self.db[lev] = {str_key: val}
        elif val == "":
            del self.db[lev][str_key]
        else:
            self.db[lev][str_key] = val
            
def etabli_shelf():
    return EtabliShelf(MAIN_SHELF_PATH)



# !SUBSECTION! Preparing entire levels

def give_time():
    sleep(0.25)
    

def launch_chain(instructions):
    LOG.info("launching {}".format(instructions))
    result = KEEP_GOING
    for inst in instructions:
        print(inst)
        result = inst(result)
        if result == DONE:
            print("early finish")
            print(inst)
            return DONE
    return KEEP_GOING


class SHexec:
    def __init__(self, command):
        self.command = command


    def __call__(self, dummy):
        LOG.debug("calling {}".format(self.command))
        try:
            p = Popen(self.command)
            pid = p.pid
            success = True
        except:
            pid = None
            success = False
        if success:
            LOG.info("SHexec( {} ), pid={}".format(self.command, pid))
            return KEEP_GOING
        else:
            LOG.info("Running {} failed!".format(self.command))
            return DONE

    def __str__(self):
        return "sh {}".format(self.command)

    
class Notification:
    def __init__(self, content):
        self.content = content
        self.inner_command = SHexec(
            ["notify-send",  NOTIF_TITLE, self.content, "-t", "3000"]
        )

    def __call__(self, dummy):
        try:
            self.inner_command()
        except:
            LOG.info("'{}' failed".format(self.__str__()))
        return KEEP_GOING

    def __str__(self):
        return "notification: " + self.content
        
    
    
class Tiling:
    def __init__(self, config):
        self.config = config

    def process_tiles(self, entry):
        if isinstance(entry, (list, tuple)):
            for tile in entry:
                give_time()
                self.process_tiles(tile)
        else:
            entry(None)
    
    def __call__(self, dummy):
        self.process_tiles(self.config)


class IfEmpty:
    def __init__(self):
        pass

    def __call__(self, dummy):
        give_time()
        if is_current_workspace_empty():
            return KEEP_GOING
        else:
            return DONE

class SetLevelVar:
    def __init__(self, key):
        self.key = key

    def __call__(self, val):
        print("setting '{}' to '{}'".format(self.key, val))
        try:
            with etabli_shelf() as e:
                e.set(current_level_name(), self.key, val)
                return KEEP_GOING
        except:
            return DONE



# !SECTION! Main function (for testing only)

if __name__ == "__main__":
    # with EtabliShelf(Path.home() / "etabli/shelf/db") as e:
    #     cur = current_level_name()
    #     e.set(cur, os.getpid(), "bla")
    #     print(e(cur))
    # #e.erase()
    n = Notification("bla bla")
    n("")
