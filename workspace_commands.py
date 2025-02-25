# Time-stamp: <2025-02-23 17:20:19>

from workspaces import *

commands = {
    "firefox" : [NewWorkspaceIfNotExists("firefox"), SHexec("firefox")],
    "test" : [NewWorkspaceIfNotExists("test"), SHexec("kitty")],
#    "comms" : [NewWorkspaceIfNotExists("comms"), [(SHexec("thunderbird")
}

# !TODO! find a way to start "standard" launchers from the CLI 
