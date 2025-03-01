#!/usr/bin/env python

from etabli import *


# !SECTION! Styling the output


# !SUBSECTION! Basic constants and helper functions 

# -- colors
ACTIVE_COLOR = "#C00000"
ACTIVE_LEVEL_COLOR = "#883333"
SEPARATOR_COLOR = "#DDDDDD"
REGULAR_COLOR = "#252525"
REGULAR_LEVEL_COLOR = "#666666"

# -- separators
LEVEL_SEPARATOR = "<span color='{}'>⋅</span>".format(SEPARATOR_COLOR)

# -- decorating functions
def weight_selector(active):
    if active:
        return "normal" # <-- change this line to "bold" to have the current workspace be bold
    else:
        return "normal"

def color_selector_workspace(active, in_level=False):
    if active:
        return ACTIVE_COLOR
    elif in_level:
        return REGULAR_COLOR
    else:
        return REGULAR_LEVEL_COLOR

def color_selector_level(active):
    if active:
        return ACTIVE_LEVEL_COLOR
    else:
        return REGULAR_COLOR

    
# !SUBSECTION! Styling an entire level

def pretty_level(lev, indices, current):
    """Formats the description of a level as a string with HTML spans to make it prettier.

    - `lev` is the name of the level (string),
    - `indices` is a list containing its workspaces, and
    - `current` is the current workspace as pair (level, index)
    """
    if len(indices) == 1: # case of a single workspace level
        active = (current[0] == lev)
        return " <span weight='{}' color='{}'>{}</span> ".format(
            weight_selector(True),
            color_selector_workspace(active, in_level=True),
            lev
        )
    else:
        active_level = (lev == current[0])
        result = "<span color='{}'> [</span>".format(
            ACTIVE_COLOR if (active_level) else SEPARATOR_COLOR
        )
        result += "<span style='italic' color='{}'>{}</span>".format(
            color_selector_level(active_level),
            lev
        )
        for index in sorted(indices, key=str.casefold):
            active =  (lev == current[0] and index == current[1])
            result += "<span weight='{}' color='{}'> {} </span>".format(
                weight_selector(active),
                color_selector_workspace(active, in_level=active_level),
                index
            )        
        result += "<span color='{}'>] </span>".format(
            ACTIVE_COLOR if (active_level) else SEPARATOR_COLOR
        )
        return result
        

# !SECTION! The Etabli class

# Stores the content of all the workspaces and stores it in an easy to use data structure.
    
class Etabli:
    def __init__(self, wm):
        self.wm = wm

        
    def set_state_from_wm(self, output=None):
        self.levels = {}
        self.current = [None, None]
        for sp in self.wm.get_workspaces():
            if output == None or sp.output == output:
                name = sp.name
                lev, index = split_workspace_name(name)
                if lev in self.levels.keys():
                    self.levels[lev].append(index)
                else:
                    self.levels[lev] = [index]
                if sp.focused:
                    self.current = [lev, index]
                

    def html_formatted(self):
        result = ""
        all_levels = list(self.levels.keys())
        all_levels.sort(key=str.casefold)
        for lev in all_levels:
            result += pretty_level(lev, self.levels[lev], self.current)
            # writing a separator, unless we are at the end
            if lev != all_levels[-1] :
                result += LEVEL_SEPARATOR
        return result

    
def print_waybar_input(eta):
    """Outputs on stdout the output of eta.html_formatted as a json
    formatted string containing all that waybar needs. It in
    particular sets the CSS class to be "custom-etabli".

    The current output is found so we can filter the given Etabli
    content.

    """
    current_output = None
    for o in SWAY.get_outputs():
        if o.focused:
            current_output = o.name
            break
    if current_output == None:
        raise Exception("no active output found!")
    else:
        eta.set_state_from_wm(output=current_output)
        output = '"text" : "{}", "tooltip": false, "percentage": 0.0, "class" : "custom-etabli"'.format(eta.html_formatted())
        print( '{' + output + '}', flush=True)

    
def wrapped_printing(SWAY, e):
    """This function's only purpose is to have the correct interface
    for it to to be called when an event is triggered.

    """
    print_waybar_input(MAIN_ETABLI)


# !SECTION! Main function 

if __name__ == "__main__":
    MAIN_ETABLI = Etabli(SWAY) # setting up global variable
    # re-printing is triggered by a change of workspace, and a change of workspace name.
    SWAY.on(Event.WORKSPACE_FOCUS, wrapped_printing)
    SWAY.on(Event.WORKSPACE_RENAME, wrapped_printing)
    # we print a first version of the current Etabli to get going
    print_waybar_input(MAIN_ETABLI)
    SWAY.main()

