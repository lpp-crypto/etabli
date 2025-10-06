#!/usr/bin/env python

import argparse
from etabli import *



# !SECTION! Launching programs

def give_time():
    sleep(0.1)

    
def exec_cmd(command):
    return Popen(command)


class Launcher:
    def __init__(self, command):
        if isinstance(command, (str)):
            self.command = command.split(" ")
            self.sequence = False
        elif isinstance(command, (list)):
            self.command = [Launcher(cmd) for cmd in command]
            self.sequence = True
        else:
            raise Exception("wrong type input for Launcher: {}".format(type(command)))

            
    def start(self):
        if self.sequence:
            self.success = True
            for l in self.command:
                give_time()
                l.start()
                if not l.success:
                    self.success = False
        else:
            try:
                p = exec_cmd(self.command)
                self.pid = p.pid
                self.success = True
            except:
                self.pid = None
                self.success = False


    def __str__(self):
        return "sh {}".format(self.command)


    
# !SECTION! The daemon handling the prepare functionality 

PREP = None

class PrepareDaemon:
    def __init__(self, config):
        self.config = config
        self.commands = {}
        for ws_name in self.config["prepare"]:
            self.commands[ws_name] = Launcher(self.config["prepare"][ws_name])
            print(ws_name, self.commands[ws_name])

            
    def start(self):
        give_time()
        workspace_name = current_workspace_name()
        if current_workspace_is_empty():
            for ws_name in sorted(self.commands):
                if ws_name in workspace_name:
                    exec_cmd([
                        "notify-send",
                        "Preparing '{}'".format(ws_name),
                        "-t",
                        "3000"
                    ])
                    self.commands[ws_name].start()
    


def launch(wm, e):
    global PREP
    PREP.start()


            
# !SECTION! Main function

def main_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config",
                        nargs="?",
                        type=str,
                        default=default_config_path,
                        help="Path to the configuration file")
    parser.add_argument("-a", "--all",
                        action="store_true",
                        help="Lists all the potential preparations")
    args = parser.parse_args()
    conf = EtabliHandler(args.config)
    if args.all:
        print_potential_preparations(conf)
    else:
        if "prepare" in conf:
            global PREP
            PREP = PrepareDaemon(conf)
            WM.on(Event.WORKSPACE_FOCUS, launch)
            WM.on(Event.WORKSPACE_RENAME, launch)
            WM.main()
        else:
            print("not doing anything: no prepare configuration in the configuration file")

        
