#!/usr/bin/env python

from etabli import *
from sys import argv


# !SECTION! Styling the output


# !SUBSECTION! Color scheme


grey_red_theme = {
    "sp" : {
        FOCUSED: "#C00000",
        FOCUSED_LEVEL: "#252525",
        VISIBLE_LEVEL_OTHER_OUTPUT:  "#707070",
        NOT_VISIBLE_CURRENT_OUTPUT: "#707070",
        NOT_VISIBLE_OTHER_OUTPUT:  "#DDDDDD",
    },
    "lvl" : {
        FOCUSED_LEVEL: "#881144",
        VISIBLE_LEVEL_OTHER_OUTPUT:  "#881144",
        NOT_VISIBLE_CURRENT_OUTPUT: "#252525",
        NOT_VISIBLE_OTHER_OUTPUT:  "#707070",
    },
    "sbl" : {
        FOCUSED_LEVEL: "#881144",
        VISIBLE_LEVEL_OTHER_OUTPUT:  "#881144",
        NOT_VISIBLE_CURRENT_OUTPUT: "#DDDDDD",
        NOT_VISIBLE_OTHER_OUTPUT:  "#DDDDDD",
    },
    # !CONTINUE! check if the current theme is the current one 
    "dlm": ["(", ")"],
}

THEME = grey_red_theme


    
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
        MAIN_ETABLI = Etabli(SWAY, argv[1], theme=THEME)
    else:
        # case where want all workspaces, regardless of output
        MAIN_ETABLI = Etabli(SWAY, None, theme=THEME)
        
    # re-printing is triggered by a change of workspace, and a change of workspace name.
    SWAY.on(Event.WORKSPACE_FOCUS, wrapped_printing)
    SWAY.on(Event.WORKSPACE_RENAME, wrapped_printing)
    # we print a first version of the current Etabli to get going
    print_waybar_input(MAIN_ETABLI)
    SWAY.main()

