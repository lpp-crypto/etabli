#!/usr/bin/env python


from .utils import *



# !SECTION! The =Workspace= class 

class Workspace:
    def __init__(self, name, level, focused):
        """
        Args:
            name: the name (a string) of the workspace
            level: the Level instance containing this workspace
            focused: a boolean that is true if this workspace is visible
        """
        self.name = name
        self.level = level
        self.focused = focused
        self.on_top = False

        
    def pango_formatted(self, theme):
        if self.focused:
            return theme["sp"]["FOCUSED"].format(self.name)
        elif self.on_top:
            return theme["ontop"][self.level.visibility].format(self.name)
        else:
            return theme["sp"][self.level.visibility].format(self.name)

        
    def __str__(self):
        return self.name


    
# !SECTION! The =Level= class 

class Level:
    def __init__(self, eta, name):
        self.spaces = {}
        self.etabli = eta
        self.name = name
        self.visibility = None
        self.sorted_indices = []

        
    def append(self, index, focused, visible):
        if focused:
            self.visibility = FOCUSED_LEVEL
            self.spaces[index] = Workspace(index, self, True)
        elif visible:
            self.visibility = VISIBLE_LEVEL_OTHER_OUTPUT
            self.spaces[index] = Workspace(index, self, True)
        else:
            self.spaces[index] = Workspace(index, self, False)
        # !IMPROVE! this is inefficient
        self.sorted_indices = []
        self.set_indices()

            
    def set_indices(self):
        for i in sorted(self.spaces.keys(), key=str.casefold):
            self.sorted_indices.append(i)

            
    def first(self):
        return self.sorted_indices[0]

    
    def last(self):
        return self.sorted_indices[-1]


    def index(self, name):
        return self.sorted_indices[name]


    def __iter__(self):
        for i in self.sorted_indices:
            yield i

            
    def __getitem__(self, index):
        if index == 0:
            return self.spaces["0"]
        else:
            return self.spaces[index]
    
    
    def __len__(self):
        return len(self.spaces)

                
    def pango_formatted(self, theme):
        # opening delimiter
        result = " " + theme["sbl"]["open"][self.visibility]
        # level name
        result += theme["lvl"][self.visibility].format(self.name)
        # workspaces names
        for index in sorted(self.spaces.keys(), key=str.casefold):
            result += " " + self.spaces[index].pango_formatted(theme)
        # closing delimiter
        
        result += theme["sbl"]["close"][self.visibility]
        return result



# !SECTION! The Board class


class Board:
    def __init__(self, path):
        self.path = Path(path).expanduser()
        try:
            with open(self.path, "rb") as f:
                self.db = pickle.load(f)
        except:
            self.db = {}
        

    def __str__(self):
        result = "{\n"
        for l in sorted(self.db):
            result += "   {:15s} : {},\n".format("'"+l+"'", self.db[l])
        result += "}"
        return result


    def __call__(self, level, name):
        if level in self.db:
            if name in self.db[level]:
                if name == "dir": # special case of directories: we
                                  # handle the expansion in python
                    return str(Path(self.db[level][name]).expanduser())
                return self.db[level][name]
        return ""
    
    
    def stick_to_level(self, level, key, string):
        if level not in self.db:
            self.db[level] = {key: string}
        else:
            self.db[level][key] = string


    def set_level_current_ws(self, level, ws):
        if "current" not in self.db:
            self.db["current"] = {level: ws}
        else:
            self.db["current"][level] = ws
        self.save()

            
    def get_level_current_ws(self, level):
        if "current" not in self.db:
            return None
        elif level not in self.db["current"]:
            return None
        else:
            return self.db["current"][level]
        
            
    def save(self):
        with open(self.path, "wb") as f:
            pickle.dump(self.db, f)

            
    def pango_formatted(self, level, theme):
        if level in self.db.keys():
            result = "   "
            dlm = "<span color='{}'>{}</span>".format(
                    theme["brd"]["dlm_color"],
                    theme["brd"]["dlm"]
                )
            for l in sorted(self.db[level]):
                result += dlm
                result += "<span color='{}' style='italic'>{}</span> ".format(
                    theme["brd"]["key_color"],
                    l
                )
                result += "<span color='{}'>{}</span>".format(
                    theme["brd"]["txt_color"],
                    self.db[level][l]
                )
            return result 
        else:
            return ""

        

    

    
# !SECTION! The Etabli class itself

  
class Etabli:
    """Stores the content of all the workspaces associated to a given
    output and stores it in an easy to use data structure.

    """


    # !SUBSECTION! Initializations
    
    def __init__(self,
                 config,
                 output):
        """Intializes an Etabli instance;

        `wm` is the i3ipc connection to use
        `output` is either `None` or the name of a specific output.
        
        """
        self.wm = WM
        self.config = config
        if output == None:
            self.output = None
        elif output[0] != "-":
            self.output = output
            self.take = True
        else:
            self.output = output[1:]
            self.take = False
        self.current_level_name = None
        self.current_index_name = None


    def set_state(self):
        self.set_state_from_wm()
        self.board = Board(self.config["board_path"])
        if "current" in self.board.db:
            for lev in self.levels:
                current = self.board.get_level_current_ws(lev)
                if current != None and current in self.levels[lev].sorted_indices:
                    self.levels[lev][current].on_top = True
        
        
    def set_state_from_wm(self):
        """Parses the list of workspaces and stores it int he internal
        state of the object.

        If `self.output` is set to `None`, then the workspaces on all
        outputs will be displayed. Otherwise, only those intended to
        appear on the given workspace are taken into account.

        """
        self.levels = {}
        self.on_current_output = False
        for sp in self.wm.get_workspaces():
            # checking whether this workspace belong to this etabli
            if (self.output) == None:
                valid = True
            elif self.take and self.output in sp.output:
                valid = True
            elif (not self.take) and (self.output not in sp.output):
                valid = True
            else:
                valid = False
            # if it does, we add it to its level (and create the level if need be)
            if  valid:
                name = sp.name
                lev, index = self.config.split_workspace_name(name)
                if lev not in self.levels:
                    self.levels[lev] = Level(self, lev)
                self.levels[lev].append(index, sp.focused, sp.visible)
                if sp.focused:
                    self.on_current_output = True
                    self.current_level_name = lev
                    self.current_index_name = index
        # adjusting the visibility of all levels now that we gather
        # all data, and giving index to all levels and indices
        self.sorted_levels = []
        self.length = 0
        for lev in sorted(self.levels.keys(), key=str.casefold):
            self.sorted_levels.append(lev)
            self.length += len(self.levels[lev])
            if self.levels[lev].visibility == None:
                if self.on_current_output:
                    self.levels[lev].visibility = NOT_VISIBLE_CURRENT_OUTPUT
                else:
                    self.levels[lev].visibility = NOT_VISIBLE_OTHER_OUTPUT


    # !SUBSUBSECTION! Obtaining information about the Etabli

    
    def workspace_super_index(self, name, index):
        lev_cursor = 0
        result = 0
        while self.sorted_levels[lev_cursor] != name:
            result += len(self.levels[self.sorted_levels[lev_cursor]])
            lev_cursor += 1
        return result + self.levels[self.sorted_levels[lev_cursor]].sorted_indices.index(index)

    
    def workspace_from_super_index(self, super_index):
        if super_index < 0:
            super_index = self.length - super_index
        lev_cursor = 0
        index_cursor = 0
        i = 0
        while i < super_index:
            index_cursor += 1
            i += 1
            if index_cursor == len(self.levels[self.sorted_levels[lev_cursor]]):
                lev_cursor += 1
                index_cursor = 0
        result_name  = self.sorted_levels[lev_cursor]
        result_index = self.levels[result_name].index(index_cursor)
        return [result_name, result_index]


    def current_level(self):
        return self.levels[self.current_level_name]



    # !SUBSUBSECTION! Returning workspaces names for cycling
        

    def name_other_workspace_within_level(self, amount):
        current_level_sorted_indices = self.levels[self.current_level_name].sorted_indices
        pos = current_level_sorted_indices.index(self.current_index_name)
        index_name = current_level_sorted_indices[
            (pos + amount) % len(current_level_sorted_indices)
        ]
        return self.current_level_name, index_name


    def name_cycle_level(self, amount):
        pos = self.sorted_levels.index(self.current_level_name)
        level_name = self.sorted_levels[
            (pos + amount) % len(self.sorted_levels)
        ]
        prev_name = self.board.get_level_current_ws(level_name)
        if prev_name == None:
            prev_index = self.levels[level_name].first()
        elif prev_name not in self.levels[level_name].sorted_indices:
            prev_index = self.levels[level_name].first()
        else:
            prev_index = prev_name
        return level_name, prev_index

    
    def name_new_workspace_within_level(self):
        index = 0
        while str(index) in self.current_level().spaces:
            index += 1
        return self.current_level_name, str(index)
    
        
    def name_cycle_within_current_output(self, amount):
        target = self.workspace_super_index(
            self.current_level_name,
            self.current_index_name
        )
        target = (target + amount) % self.length
        return self.workspace_from_super_index(target)

    
    # !SUBSUBSECTION! Changing focused window
    
    def focus_workspace(self, name, index):
        self.wm.command("workspace {}".format(
            self.config.format_workspace_name(
            name,
            index
        )))
        self.board.set_level_current_ws(name, index)
        
    
    def cycle_within_current_level(self, amount):
        lev, index = self.name_other_workspace_within_level(amount)
        self.focus_workspace(lev, index)

    
    def cycle_level(self, amount):
        lev, index = self.name_cycle_level(amount)
        self.focus_workspace(lev, index)


    def new_workspace_within_level(self):
        lev, index = self.name_new_workspace_within_level()
        self.focus_workspace(lev, index)

        
    def cycle_within_current_output(self, amount):
        lev, index = self.name_cycle_within_current_output(amount)
        self.focus_workspace(lev, index)


    # !SUBSUBSECTION! Cycling while bringing a window along 
    
    def send_window_to(self, name, index):
        target_ws = self.config.format_workspace_name(name, index)
        cmd = "move container to workspace '{}'".format(target_ws)
        print(cmd)
        self.wm.command(cmd)
        self.focus_workspace(name, index)

    
    def cycle_within_current_level_with_window(self, amount):
        lev, index = self.name_other_workspace_within_level(amount)
        self.send_window_to(lev, index)


    def cycle_level_with_window(self, amount):
        lev, index = self.name_cycle_level(amount)
        self.send_window_to(lev, index)


    def new_workspace_within_level_with_window(self):
        lev, index = self.name_new_workspace_within_level()
        self.send_window_to(lev, index)


    def cycle_within_current_output_with_window(self, amount):
        lev, index = self.name_cycle_within_current_output(amount)
        self.send_window_to(lev, index)

        
    # !SUBSUBSECTION! Printing
    
        
    def pango_formatted(self):
        """Returns the pango formatted string needed by waybar to
        display the state of the Etabli.

        """
        result = ""
        for lev in sorted(self.levels.keys(), key=str.casefold):
            result += self.levels[lev].pango_formatted(self.config["theme"])
        result += self.board.pango_formatted(
            self.current_level_name,
            self.config["theme"]
        )
        return result 


    def list_workspaces(self):
        result = []
        for lev in sorted(self.levels.keys(), key=str.casefold):
            for ws in self.levels[lev]:
                result.append(self.config.format_workspace_name(lev, ws))
        return result
                

    def print_workspaces(self):
        for ws in self.list_workspaces():
            print(ws)
                

    # !SUBSECTION! "With" environment

    def __enter__(self):
        return self

    
    def __exit__(self, exc_type, exc_value, traceback):
        print(self.board.db)
        self.board.save()



