#!/usr/bin/env python

from etabli import *
from sys import argv


# !SECTION! Styling the output


# !SUBSECTION! Basic constants and helper functions 

# -- colors
ACTIVE_COLOR = "#C00000"
ACTIVE_LEVEL_COLOR = "#883333"
SEPARATOR_COLOR = "#DDDDDD"
REGULAR_COLOR = "#252525"
REGULAR_LEVEL_COLOR = "#707070"

# -- separators
LEVEL_SEPARATOR = "" #"<span color='{}'>⋅</span>".format(SEPARATOR_COLOR)

# -- decorating functions
def weight_selector(active):
    if active:
        return "normal" # <-- change this line to "bold" to have the current workspace be bold
    else:
        return "normal"

def color_selector_workspace(focused, in_focused_output, in_level=False):
    if focused:
        return ACTIVE_COLOR
    elif in_focused_output:
        if in_level:
            return REGULAR_COLOR
        else:
            return REGULAR_LEVEL_COLOR
    else:
        if in_level:
            return REGULAR_LEVEL_COLOR
        else:
            return SEPARATOR_COLOR
            

def color_selector_level(focused, in_focused_output):
    if focused:
        return ACTIVE_LEVEL_COLOR
    elif in_focused_output:
        return REGULAR_COLOR
    else:
        return REGULAR_LEVEL_COLOR

    
# !SUBSECTION! Styling an entire level

def pretty_level(lev, indices, current):
    """Formats the description of a level as a string with HTML spans to make it prettier.

    - `lev` is the name of the level (string),
    - `indices` is a list containing its workspaces, and
    - `current` is the current workspace as a pair (level, index)
    """
    if len(indices) == 1: # case of a single workspace level
        focused = (current[0] == lev)
        return " <span weight='{}' color='{}'>{}</span> ".format(
            weight_selector(True),
            color_selector_workspace(focused,
                                     current[2],
                                     in_level=True),
            lev
        )
    else:
        visible = (lev == current[0])
        if current[2] and visible:
            delimiter_color = ACTIVE_COLOR
        else:
            delimiter_color = SEPARATOR_COLOR
        result = "<span color='{}'> [</span>".format(delimiter_color)
        result += "<span style='italic' color='{}'>{}</span>".format(
            color_selector_level(visible, current[2]),
            lev
        )
        for index in sorted(indices, key=str.casefold):
            focused =  (lev == current[0] and index == current[1])
            result += "<span weight='{}' color='{}'> {}</span>".format(
                weight_selector(focused),
                color_selector_workspace(focused, current[2], in_level=visible),
                index
            )        
        result += "<span color='{}'>]</span>".format(delimiter_color)
        return result
        

# !SECTION! The Etabli class

  
class Etabli:
    """Stores the content of all the workspaces associated to a given
    output and stores it in an easy to use data structure.

    """
    def __init__(self, wm, output):
        """Intializes an Etabli instance;

        `wm` is the i3ipc connection to use
        `output` is either `None` or the name of a specific output.
        
        """
        self.wm = wm
        self.output = output

        
    def set_state_from_wm(self):
        """Parses the list of workspaces and stores it int he internal
        state of the object.

        If `self.output` is set to `None`, then the workspaces on all
        outputs will be displayed. Otherwise, only those intended to
        appear on the given workspace are taken into account.

        """
        self.levels = {}
        self.current = [None, None]
        self.focused = None
        self.visible = None
        for sp in self.wm.get_workspaces():
            if (self.output) == None or (sp.output == self.output):
                name = sp.name
                lev, index = split_workspace_name(name)
                if lev in self.levels.keys():
                    self.levels[lev].append(index)
                else:
                    self.levels[lev] = [index]
                # figuring out the visible/focused workspace
                if sp.focused:
                    self.focused = lev
                    self.current = [lev, index, True]
                elif sp.visible:
                    self.visible = lev
                    self.current = [lev, index, False]
                

    def pango_formatted(self):
        """Returns the pango formatted string needed by waybar to
        display the state of the Etabli.

        """
        result = ""
        all_levels = list(self.levels.keys())
        all_levels.sort(key=str.casefold)
        for lev in all_levels:
            result += pretty_level(lev, self.levels[lev], self.current)
            # writing a separator, unless we are at the end
            if lev != all_levels[-1] :
                result += LEVEL_SEPARATOR
        return result

    
    def current_level_variables(self):
        result = ""
        if self.focused != None:
            with etabli_shelf() as var:
                local_vars = var(self.focused)
                for k in local_vars:
                    result += "({} {}), ".format(k, local_vars[k])
            if len(result) == 0:
                return "()"
            else:
                return result[:-2]

    
def print_waybar_input(eta):
    """Outputs on stdout the output of eta.pango_formatted as a json
    formatted string containing all that waybar needs. It in
    particular sets the CSS class to be "custom-etabli".

    The current output is found so we can filter the given Etabli
    content.

    """
    eta.set_state_from_wm()
    output = '"text" : "{}", "tooltip": "{}", "percentage": 0.0, "class" : "custom-etabli"'.format(
        eta.pango_formatted(),
        eta.current_level_variables(),
    )
    print( '{' + output + '}', flush=True)

    
def wrapped_printing(SWAY, e):
    """This function's only purpose is to have the correct interface
    for it to to be called when an event is triggered.

    """
    print_waybar_input(MAIN_ETABLI)


# !SECTION! Main function 

if __name__ == "__main__":
    if len(argv) > 1:
        # case where we only want the workspaces that correspond to a specific output
        MAIN_ETABLI = Etabli(SWAY, argv[1])
    else:
        # case where want all workspaces, regardless of output
        MAIN_ETABLI = Etabli(SWAY, None)
        
    # re-printing is triggered by a change of workspace, and a change of workspace name.
    SWAY.on(Event.WORKSPACE_FOCUS, wrapped_printing)
    SWAY.on(Event.WORKSPACE_RENAME, wrapped_printing)
    # we print a first version of the current Etabli to get going
    print_waybar_input(MAIN_ETABLI)
    SWAY.main()

