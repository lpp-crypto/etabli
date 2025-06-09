#!/usr/bin/env python

from etabliLib import *

import os
from stat import S_ISSOCK


EDITOR = ["sh", Path.home() / "new-emacs/scripts/editor"]

EDITOR_SESSIONS = {}

class EmacsServer:
    def __init__(self, daemon_name=None, additional_args=[]):
        self.daemon_name = daemon_name
        self.additional_args = additional_args
        self.pid = None

    def __call__(self, dummy):
        if self.daemon_name == None:
            daemon_name = current_level_name()
        else:
            daemon_name = self.daemon_name
        if daemon_name not in EDITOR_SESSIONS:
            cmd = EDITOR + self.additional_args
            cmd += ["--daemon={}".format(daemon_name)] 
            try:
                p = Popen(cmd)
                self.pid = p.pid
                return self.daemon_name
            except:
                print("couldn't start EMACS server {}".format(self.daemon_name))
        else:
            print("Server {} is already running".format(self.daemon_name))
                

def list_servers():
    # inspired by https://stackoverflow.com/questions/22521440/how-to-obtain-a-list-of-running-emacs-servers-from-a-shell
    serverdir = os.path.join(os.environ.get('XDG_RUNTIME_DIR'), 'emacs/')
    servers = [s for s in os.listdir(serverdir)
               if S_ISSOCK(os.stat(os.path.join(serverdir, s)).st_mode)]
    print(servers)



# lsof +d $XDG_RUNTIME_DIR/emacs
# if [[ -a "$XDG_RUNTIME_DIR/emacs/*" ]]; then echo "blaa"; else echo "wawa"; fi



# !TODO! write waybar daemon that is a given color if there are unsaved buffer in the level's emacs-server
# useful link: https://emacs.stackexchange.com/questions/28665/print-unquoted-output-to-stdout-from-emacsclient
