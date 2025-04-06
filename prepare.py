#!/usr/bin/env python

from etabliLib import *
from etabliConfig import launch_table

def maybe_prepare(SWAY, e):
    if is_current_workspace_empty(SWAY):
        curr = current_workspace_name()
        for k in launch_table.keys():
            if k in curr:
                launch_chain(launch_table[k])
                print(launch_table[k])
                break
    else:
        pass



# !TODO! add functions that read the content of ~/org/meuporg to open project with all the windows needed

    
if __name__ == "__main__":        
    SWAY.on(Event.WORKSPACE_FOCUS, maybe_prepare)
    SWAY.on(Event.WORKSPACE_RENAME, maybe_prepare)
    SWAY.main()

