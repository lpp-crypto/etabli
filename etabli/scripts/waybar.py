#!/usr/bin/env python

import argparse
from etabli import *



class WaybarDaemon:
    def __init__(self, config, output):
        self.config = config
        self.output = output
        self.eta = Etabli(self.config, output)


    def __str__(self):
        self.eta.set_state()
        output = '"text" : "{}", "percentage": 0.0, "class" : "custom-etabli"'.format(
            self.eta.pango_formatted(),
        )
        return '{' + output + '}'


    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

DAEMON = None
        
def wrapped_printing(SWAY, e):
    """This function's only purpose is to have the correct interface
    for it to to be called when an event is triggered.

    """
    print(DAEMON, flush=True)


# !SECTION! Main function 



def main_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config",
                        nargs="?",
                        type=str,
                        default=default_config_path,
                        help="Path to the configuration file")
    parser.add_argument("-o", "--output",
                        help="Name of the output on which waybar is to be displayed")
    args = parser.parse_args()

    
    conf = EtabliHandler(args.config)
    if not args.output:
        args.output = None

    global DAEMON
    with WaybarDaemon(conf, args.output) as DAEMON:
        # re-printing is triggered by a change of workspace, and a change of workspace name.
        WM.on(Event.WORKSPACE_FOCUS, wrapped_printing)
        WM.on(Event.WORKSPACE_RENAME, wrapped_printing)
        # we print a first version of the current Etabli to get going
        print(DAEMON, flush=True)
        WM.main()
    
