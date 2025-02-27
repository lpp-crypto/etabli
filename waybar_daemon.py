#!/usr/bin/env python

from etabli import *


# !TODO! use similar style for all the workspaces, use a different font for the level names

# colors:
ACTIVE_COLOR = "#C00000"
ACTIVE_LEVEL_COLOR = "#994444"
BRACKET_COLOR = "#222222"
REGULAR_COLOR = "#EEEEEE"


def pretty_level(lev, indices, current):
    if len(indices) == 1: # case of a single workspace level
        if current[0] == lev:
            return " <span weight='bold' color='{}'>{}</span> ".format(ACTIVE_COLOR, lev)
        else:
            return " <span weight='bold' color='{}'>{}</span> ".format(REGULAR_COLOR, lev)
    else:
        result = "<span color='{}'> [</span>".format(ACTIVE_COLOR if (lev == current[0]) else BRACKET_COLOR)
        result += "<span style='italic' color='{}'>{}</span>".format(
            ACTIVE_LEVEL_COLOR if (lev == current[0]) else REGULAR_COLOR,
            lev
        )
        for index in sorted(indices, key=str.casefold):
            result += "<span weight='bold' color='{}'> {} </span>".format(
                ACTIVE_LEVEL_COLOR if (lev == current[0] and index == current[1]) else REGULAR_COLOR,
                index
            )        
        result += "<span color='{}'>] </span>".format(ACTIVE_COLOR if (lev == current[0]) else BRACKET_COLOR)
        return result
        


    
class Etabli:
    def __init__(self, wm):
        self.wm = wm
        self.get_state_from_wm()

    def get_state_from_wm(self):
        self.levels = {}
        self.current = [None, None]
        for sp in self.wm.get_workspaces():
            name = sp.name
            lev, index = split_workspace_name(name)
            if lev in self.levels.keys():
                self.levels[lev].append(index)
            else:
                self.levels[lev] = [index]
            if sp.focused:
                self.current = [lev, index]
                

    def __str__(self):
        result = ""
        bracket_open  = "<span color='#111111'>[</span>"
        bracket_close = "<span color='#111111'>]</span>"
        index_separator = "<span color='#555555'>|</span>"
        for lev in sorted(self.levels.keys(), key=str.casefold):
            result += pretty_level(lev, self.levels[lev], self.current)
        return result
        #     if lev == self.current_level:
        #         pretty_lev = "<span color='#0000C0'>{}</span>".format(lev)
        #     else:
        #         pretty_lev = lev
        #     if len(self.levels[lev]) == 1:
        #         result += "{}{}{}".format(
        #             " <span weight='bold'>",
        #             pretty_lev,
        #             "</span> "
        #         )
        #     else:
        #         result += bracket_open + "<span weight='bold'>{}</span>  ".format(
        #             pretty_lev,
        #         )
        #         for index in sorted(self.levels[lev], key=str.casefold):
        #             if lev == self.current_level and index == self.current_index:
        #                 result += "<span color='#C00000' style='italic'>{}</span> ".format(index) + index_separator + " "
        #             else:
        #                 result += "{} ".format(index) + index_separator + " "
        #         result = result[:-(1+len(index_separator))] + bracket_close + " "
        # print("current: {}\n\n".format(self.current_level))
        # return result[:-1]

def waybar_input(SWAY, e):
    MAIN_ETABLI.get_state_from_wm()
    print( '{"text" : "' + str(MAIN_ETABLI) + '", "tooltip": false, "percentage": 0.0, "class" : "custom-etabli"}', flush=True)


if __name__ == "__main__":
    MAIN_ETABLI = Etabli(SWAY)
    SWAY.on(Event.WORKSPACE_FOCUS, waybar_input)
    SWAY.on(Event.WORKSPACE_RENAME, waybar_input)
    print( '{"text" : "' + str(MAIN_ETABLI) + '", "tooltip": false, "percentage": 0.0, "class" : "custom-etabli"}', flush=True)
    SWAY.main()

