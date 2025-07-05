#!/usr/bin/env python

from etabli import *
from sys import argv


# !SECTION! Styling the output


# !SUBSECTION! Color scheme


FOCUSED = 1
FOCUSED_LEVEL = 2
VISIBLE_LEVEL_OTHER_OUTPUT = 3
NOT_VISIBLE_CURRENT_OUTPUT = 4
NOT_VISIBLE_OTHER_OUTPUT = 5


grey_red_theme = {
    "sp" : {
        FOCUSED: "#C00000",
        FOCUSED_LEVEL: "#252525",
        VISIBLE_LEVEL_OTHER_OUTPUT:  "#707070",
        NOT_VISIBLE_CURRENT_OUTPUT: "#707070",
        NOT_VISIBLE_OTHER_OUTPUT:  "#DDDDDD",
    },
    "lvl" : {
        FOCUSED_LEVEL: "#883333",
        VISIBLE_LEVEL_OTHER_OUTPUT:  "#883333",
        NOT_VISIBLE_CURRENT_OUTPUT: "#252525",
        NOT_VISIBLE_OTHER_OUTPUT:  "#707070",
    },
    "sbl" : {
        FOCUSED_LEVEL: "#C00000",
        VISIBLE_LEVEL_OTHER_OUTPUT:  "#DDDDDD",
        NOT_VISIBLE_CURRENT_OUTPUT: "#DDDDDD",
        NOT_VISIBLE_OTHER_OUTPUT:  "#DDDDDD",
    },
    "dlm": ["[", "]"],
}

THEME = grey_red_theme

# !SECTION! The Etabli class

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

  
class Etabli:
    """Stores the content of all the workspaces associated to a given
    output and stores it in an easy to use data structure.

    """
    def __init__(self, wm, output, theme=grey_red_theme):
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
        # adjusting the visibility of all levels now that we gather all data
        for lev in self.levels:
            if self.levels[lev].visibility == None:
                if self.on_current_output:
                    self.levels[lev].visibility = NOT_VISIBLE_CURRENT_OUTPUT
                else:
                    self.levels[lev].visibility = NOT_VISIBLE_OTHER_OUTPUT

        

    def pango_formatted(self):
        """Returns the pango formatted string needed by waybar to
        display the state of the Etabli.

        """
        result = ""
        for lev in sorted(self.levels.keys(), key=str.casefold):
            result += self.levels[lev].pango_formatted(self.theme)
        return result 

    
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

