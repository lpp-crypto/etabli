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

# visibilities
FOCUSED = 1
FOCUSED_LEVEL = 2
VISIBLE_LEVEL_OTHER_OUTPUT = 3
NOT_VISIBLE_CURRENT_OUTPUT = 4
NOT_VISIBLE_OTHER_OUTPUT = 5


# !SUBSECTION! Setting up logging 

logging.basicConfig(filename='log.log',
                    encoding='utf-8',
                    level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')
LOG = logging.getLogger(__name__)




# !SECTION! The =Etabli= class and its helpers


# !SUBSECTION! Formatting workspace names


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


def focus_workspace(name):
    SWAY.command("workspace {}".format(name))



# !SUBSECTION! The =Workspace= class 

class Workspace:
    def __init__(self, name, level, focused):
        """
        Args:
            name: the name (a string) of the workspace
            level: the Level instance containing this workspace
            focused: a boolean that is true if this workspace is visible
        """
        self.name = name
        self.level = level
        self.focused = focused

        
    def pango_formatted(self, theme):
        if self.focused:
            return " <span color='{}'>{}</span>".format(
                theme["sp"][FOCUSED],
                self.name
            )
        else:
            return " <span color='{}'>{}</span>".format(
                theme["sp"][self.level.visibility],
                self.name
            )

        
    def __str__(self):
        return self.name


    
# !SUBSECTION! The =Level= class 

class Level:
    def __init__(self, eta, name):
        self.spaces = {}
        self.etabli = eta
        self.name = name
        self.visibility = None

        
    def append(self, index, focused, visible):
        if focused:
            self.visibility = FOCUSED_LEVEL
            self.spaces[index] = Workspace(index, self, True)
        elif visible:
            self.visibility = VISIBLE_LEVEL_OTHER_OUTPUT
            self.spaces[index] = Workspace(index, self, True)
        else:
            self.spaces[index] = Workspace(index, self, False)

            
    def set_indices(self):
        self.sorted_indices = []
        for i in sorted(self.spaces.keys(), key=str.casefold):
            self.sorted_indices.append(i)

            
    def first(self):
        return self.sorted_indices[0]

    
    def last(self):
        return self.sorted_indices[-1]


    def index(self, name):
        return self.sorted_indices[name]
    
    
    def __len__(self):
        return len(self.spaces)

                
    def pango_formatted(self, theme):
        # opening delimiter
        result = " <span color='{}'>{}</span>".format(
            theme["sbl"][self.visibility],
            theme["dlm"][0]
        )
        # level name
        result += "<span color='{}' style='italic'>{}</span>".format(
            theme["lvl"][self.visibility],
            self.name
        )
        # workspaces names
        for index in sorted(self.spaces.keys(), key=str.casefold):
            result += self.spaces[index].pango_formatted(theme)
        # closing delimiter
        result += "<span color='{}'>{}</span>".format(
            theme["sbl"][self.visibility],
            theme["dlm"][1]
        )
        return result


    
# !SUBSECTION! The =Etabli= class itself

  
class Etabli:
    """Stores the content of all the workspaces associated to a given
    output and stores it in an easy to use data structure.

    """


    # !SUBSUBSECTION! Initializations
    
    def __init__(self, wm, output, theme={}):
        """Intializes an Etabli instance;

        `wm` is the i3ipc connection to use
        `output` is either `None` or the name of a specific output.
        
        """
        self.wm = wm
        self.theme = theme
        if output == None:
            self.output = None
        elif output[0] != "-":
            self.output = output
            self.take = True
        else:
            self.output = output[1:]
            self.take = False
        self.current_level_name = None
        self.current_index_name = None

        
    def set_state_from_wm(self):
        """Parses the list of workspaces and stores it int he internal
        state of the object.

        If `self.output` is set to `None`, then the workspaces on all
        outputs will be displayed. Otherwise, only those intended to
        appear on the given workspace are taken into account.

        """
        self.levels = {}
        self.on_current_output = False
        for sp in self.wm.get_workspaces():
            # checking whether this workspace belong to this etabli
            if (self.output) == None:
                valid = True
            elif self.take and self.output in sp.output:
                valid = True
            elif (not self.take) and (self.output not in sp.output):
                valid = True
            else:
                valid = False
            # if it does, we add it to its level (and create the level if need be)
            if  valid:
                name = sp.name
                lev, index = split_workspace_name(name)
                if lev not in self.levels:
                    self.levels[lev] = Level(self, lev)
                self.levels[lev].append(index, sp.focused, sp.visible)
                if sp.focused:
                    self.on_current_output = True
                    self.current_level_name = lev
                    self.current_index_name = index
        # adjusting the visibility of all levels now that we gather
        # all data, and giving index to all levels and indices
        self.sorted_levels = []
        self.length = 0
        for lev in sorted(self.levels.keys(), key=str.casefold):
            self.sorted_levels.append(lev)
            self.length += len(self.levels[lev])
            self.levels[lev].set_indices()
            if self.levels[lev].visibility == None:
                if self.on_current_output:
                    self.levels[lev].visibility = NOT_VISIBLE_CURRENT_OUTPUT
                else:
                    self.levels[lev].visibility = NOT_VISIBLE_OTHER_OUTPUT

                    
    def focus_workspace(self, name, index):
        self.wm.command("workspace {}".format(format_workspace_name(
            name,
            index
        )))


    # !SUBSUBSECTION! Getters/setters

    
    def workspace_super_index(self, name, index):
        lev_cursor = 0
        result = 0
        while self.sorted_levels[lev_cursor] != name:
            result += len(self.levels[self.sorted_levels[lev_cursor]])
            lev_cursor += 1
        return result + self.levels[self.sorted_levels[lev_cursor]].sorted_indices.index(index)

    
    def workspace_from_super_index(self, super_index):
        if super_index < 0:
            super_index = self.length - super_index
        lev_cursor = 0
        index_cursor = 0
        i = 0
        while i < super_index:
            index_cursor += 1
            i += 1
            if index_cursor == len(self.levels[self.sorted_levels[lev_cursor]]):
                lev_cursor += 1
                index_cursor = 0
        result_name  = self.sorted_levels[lev_cursor]
        result_index = self.levels[result_name].index(index_cursor)
        return [result_name, result_index]


    def current_level(self):
        return self.levels[self.current_level_name]
    
    
    # !SUBSUBSECTION! Cycling workspaces 
                    
    def cycle_within_current_level(self, amount):
        current_level_sorted_indices = self.levels[self.current_level_name].sorted_indices
        pos = current_level_sorted_indices.index(self.current_index_name)
        index_name = current_level_sorted_indices[
            (pos + amount) % len(current_level_sorted_indices)
        ]
        self.focus_workspace(self.current_level_name, index_name)


    def cycle_level(self, amount):
        pos = self.sorted_levels.index(self.current_level_name)
        level_name = self.sorted_levels[
            (pos + amount) % len(self.sorted_levels)
        ]
        self.focus_workspace(level_name, self.levels[level_name].first())

        
    def cycle_within_current_output(self, amount):
        target = self.workspace_super_index(
            self.current_level_name,
            self.current_index_name
        )
        target = (target + amount) % self.length
        target_name,target_index = self.workspace_from_super_index(target)
        self.focus_workspace(target_name, target_index)

        
    def new_workspace_within_level(self):
        index = 0
        print(self.sorted_levels)
        while str(index) in self.current_level().spaces:
            index += 1
        self.focus_workspace(self.current_level_name, str(index))

        
    # !SUBSUBSECTION! Printing
    
        
    def pango_formatted(self):
        """Returns the pango formatted string needed by waybar to
        display the state of the Etabli.

        """
        result = ""
        for lev in sorted(self.levels.keys(), key=str.casefold):
            result += self.levels[lev].pango_formatted(self.theme)
        return result 


    # !SUBSUBSECTION! Handling level variables 
    
    def current_level_variables(self):
        result = ""
        # !TODO!  fix current_level_variables
        # if self.focused != None:
        #     with etabli_shelf() as var:
        #         local_vars = var(self.focused)
        #         for k in local_vars:
        #             result += "({} '{}'), ".format(k, local_vars[k])
        #     if len(result) == 0:
        #         return "()"
        #     else:
        #         return result[:-2]
        return result


# !SECTION! Dealing with workspaces and their levels

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
    eta = Etabli(SWAY, "1")
    eta.set_state_from_wm()


