import os
from stat import S_ISSOCK

# inspired by https://stackoverflow.com/questions/22521440/how-to-obtain-a-list-of-running-emacs-servers-from-a-shell

serverdir = os.path.join(os.environ.get('XDG_RUNTIME_DIR'), 'emacs/')
servers = [s for s in os.listdir(serverdir)
           if S_ISSOCK(os.stat(os.path.join(serverdir, s)).st_mode)]
print(servers)



# lsof +d $XDG_RUNTIME_DIR/emacs
# if [[ -a "$XDG_RUNTIME_DIR/emacs/*" ]]; then echo "blaa"; else echo "wawa"; fi



# !TODO! write waybar daemon that is a given color if there are unsaved buffer in the level's emacs-server
# useful link: https://emacs.stackexchange.com/questions/28665/print-unquoted-output-to-stdout-from-emacsclient
