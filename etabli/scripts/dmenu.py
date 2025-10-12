#!/usr/bin/python

import subprocess
import argparse
from etabli import *


# !SECTION! Functions using dmenu 

# !SUBSECTION! Wrapping dmenu

def dmenu_get(dmenu, prompt, options, preset=""):
    possibilities = "\n".join(options)
    cmd = dmenu.split(" ") + [prompt]
    if preset != "":
        cmd +=  ["-filter", preset]
    p = subprocess.run(cmd,
                       input=possibilities.encode("UTF-8"),
                       capture_output=True)
    result = p.stdout.decode("UTF-8")[:-1] # removing final end-of-line
    if result in ["", " "]:
        raise Exception("Not doing anything")
    else:
        return result
    

# !SUBSECTION! High level functions using dmenu


def choose_workspace(conf, eta, prompt):
    current_level = conf.split_workspace_name(current_workspace_name())[0]
    candidates =  eta.list_workspaces()
    candidates.append(conf["hrule"])
    candidates += [
        "Prepare {}".format(conf.format_workspace_name(
            current_level,
            shortcut
        ))
        for shortcut in conf["prepare"]
    ]
    query = dmenu_get(conf["dmenu"],
                      prompt,
                      candidates
                      )
    next_ws = query.split(" ")[-1]
    return conf.split_workspace_name(next_ws)


def switch_workspace(conf, eta):
    try:
        lev, index = choose_workspace(conf, eta, "Go to workspace: ")
    except:
        lev, index = (False, False)
        raise Exception("Not doing anything")
    eta.focus_workspace(lev, index)


def switch_workspace_with_window(conf, eta):
    lev, index = choose_workspace(conf, eta, "Send and go to workspace: ")
    eta.send_window_to(lev, index)
    

def rename(conf, eta):
    current_level, current_index = conf.split_workspace_name(
        current_workspace_name()
    )
    candidates =  eta.list_workspaces()
    candidates.append(conf["hrule"])
    candidates += [
        "Prepare {}".format(conf.format_workspace_name(
            current_level,
            shortcut
        ))
        for shortcut in conf["prepare"]
    ]
    query = dmenu_get(conf["dmenu"],
                      "New name: ",
                      candidates,
                      preset=conf.format_workspace_name(current_level, "")
                      )
    next_name = query.split(" ")[-1]
    next_level, next_index = conf.split_workspace_name(next_name)
    msg = "rename workspace '{}' to '{}'".format(
        conf.format_workspace_name(current_level, current_index),
        next_name
    )
    WM.command(msg)
    eta.board.set_level_current_ws(next_level, next_index)
            


# !SECTION! Processing arguments 



def process_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config",
                        nargs="?",
                        type=str,
                        default=default_config_path,
                        help="Path to the configuration file")
    parser.add_argument("-w", "--choose_workspace",
                        action="store_true",
                        help="Prompts for the name of the workspace to switch to, then does just that")
    parser.add_argument("-ww", "--choose_workspace_with_window",
                        action="store_true",
                        help="Prompts for the name of the workspace to switch to, then does just that")
    parser.add_argument("-r", "--rename",
                        action="store_true",
                        help="Prompts for a new name for the current workspace, and then changes it.")
    return parser.parse_args()


# !SECTION! Main function 

def main_cli():
    args = process_arguments()
    conf = EtabliHandler(args.config)
    eta = Etabli(conf, current_output())
    eta.set_state()

    if args.choose_workspace:
        switch_workspace(conf, eta)
    elif args.choose_workspace_with_window:
        switch_workspace_with_window(conf, eta)
    elif args.rename:
        rename(conf, eta)


