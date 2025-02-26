# Time-stamp: <2025-02-26 10:33:11>

from etabli import *

commands = {
    "firefox" : [NewWorkspaceIfNotExists("firefox"), SHexec("firefox")],
    "test" : [NewWorkspaceIfNotExists("test"), SHexec("kitty")],
#    "comms" : [NewWorkspaceIfNotExists("comms"), [(SHexec("thunderbird")
}

# !TODO! find a way to start "standard" launchers from the CLI 
