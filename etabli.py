#!/usr/bin/env python
# Time-stamp: <2025-07-07 18:47:09>

from etabliConfig import *


# !SECTION! Basic functions called directly from the CLI 

def cycle_workspace_in_output(amount):
    names = workspaces_in_current_output()
    current_name = current_workspace_name()
    focus_workspace(names[(names.index(current_name)+amount) % len(names)])

        
def next_workspace():
    cycle_workspace_in_output(1)

    
def prev_workspace():
    cycle_workspace_in_output(-1)


def print_workspaces_in_current_output():
    names = workspaces_in_current_output()
    for n in names:
        print(n)

def print_potential_preparations():
    if len(launch_table.keys()) > 0:
        print(HRULE)
        cur_lev = current_level_name()
        cur_workspaces = all_workspaces()
        for k in launch_table.keys():
            potential_new = "{}{}{}".format(
                cur_lev,
                SEPARATOR,
                k
            )
            if potential_new not in cur_workspaces:
                print("Prepare {}".format(potential_new))


def print_workspaces():
    names = [o.name for o in SWAY.get_workspaces()]
    names.sort(key=str.casefold) # to have case insensitive sorting
    for n in names:
        print(n)
    print_potential_preparations()

    
def get_level_variable(key):
    with etabli_shelf() as s:
        print(s.get(current_level_name(), key))
    
def set_level_variable(key, val):
    with etabli_shelf() as s:
        s.set(current_level_name(), key, val)
    

# !SECTION! Main program


# !TODO! switch to argparse

# !TODO! add a function to rename a level


# arg_function_map = {
#     "next_workspace" : next_workspace,
#     "prev_workspace" : prev_workspace,
#     "next_workspace_in_level" : next_workspace_in_level,
#     "prev_workspace_in_level" : prev_workspace_in_level,
#     "new_workspace_in_level" : new_workspace_in_level,
#     "list_windows" : print_all_windows,
#     "focus_window" : focus_window
# }

# !CONTINUE! finish the argv to function dictionnary


if __name__ == "__main__":
    eta = Etabli(SWAY, current_output())
    eta.set_state_from_wm()

    # general cycling
    if argv[1] == "next_workspace":
        eta.cycle_within_current_output(1)
    elif argv[1] == "prev_workspace":
        eta.cycle_within_current_output(-1)
    # by level
    elif argv[1] == "next_workspace_in_level":
        eta.cycle_within_current_level(1)
    elif argv[1] == "prev_workspace_in_level":
        eta.cycle_within_current_level(-1)
    elif argv[1] == "new_workspace_in_level":
        eta.new_workspace_within_level()
    elif argv[1] == "next_level":
        eta.cycle_level(1)
    elif argv[1] == "prev_level":
        eta.cycle_level(-1)
    # dealing with windows
    elif argv[1] == "list_windows":
        print_all_windows()
    elif argv[1] == "focus_window":
        focus_window(argv[2])
    # general utilities
    elif argv[1] == "get_workspaces_in_output":
        print_workspaces_in_output()
    elif argv[1] == "get_workspaces":
        print_workspaces()
    elif argv[1] == "current_workspace":
        print(current_workspace_name())
    elif argv[1] == "current_level":
        print(current_level_name())
    # workspaces within a level
    elif argv[1] == "name_next_workspace_in_level":
        print(name_next_workspace_in_level())
    elif argv[1] == "name_previous_workspace_in_level":
        print(name_prev_workspace_in_level())
    elif argv[1] == "name_new_workspace_in_level":
        print(name_new_workspace_in_level())
    elif argv[1] == "rename_current_workspace":
        print(rename_workspace_by_guessing())
    # etabli shelf
    elif argv[1] == "get_level_variable":
        get_level_variable(argv[2])
    elif argv[1] == "set_level_variable":
        set_level_variable(argv[2], argv[3])
    # prepare
    elif argv[1] == "prepare":
        print_potential_preparations()
    else:
        raise Exception("unknown input: {}".format(argv[1]))

