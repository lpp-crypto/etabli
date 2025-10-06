#!/usr/bin/env python


import argparse
from etabli import *




def process_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config",
                        nargs="?",
                        type=str,
                        default=default_config_path,
                        help="Path to the configuration file")
    # cycling
    # -- workspaces
    parser.add_argument("-nw", "--next_workspace",
                        action="store_true",
                        help="Changes focus to the next workspace, crossing level boundaries")
    parser.add_argument("-pw", "--previous_workspace",
                        action="store_true",
                        help="Changes focus to the previous workspace, crossing level boundaries")
    parser.add_argument("-ni", "--next_workspace_in_level",
                        action="store_true",
                        help="Changes focus to the next workspace withing the level")
    parser.add_argument("-pi", "--previous_workspace_in_level",
                        action="store_true",
                        help="Changes focus to the next workspace withing the level")
    parser.add_argument("-new", "--new_workspace_in_level",
                        action="store_true",
                        help="Focuses a new workspace within the current level")
    # -- levels
    parser.add_argument("-nl", "--next_level",
                        action="store_true",
                        help="Changes focus to the next level")
    parser.add_argument("-pl", "--previous_level",
                        action="store_true",
                        help="Changes focus to the previous level")

    # cycling with a window
    parser.add_argument("-nwww", "--next_workspace_with_window",
                        action="store_true",
                        help="Changes focus to the next workspace, crossing level boundaries, and brings the current container along")
    parser.add_argument("-pwww", "--previous_workspace_with_window",
                        action="store_true",
                        help="Changes focus to the previous workspace, crossing level boundaries, and brings the current container along")
    parser.add_argument("-niww", "--next_workspace_in_level_with_window",
                        action="store_true",
                        help="Changes focus to the next workspace withing the level, and brings the current container along")
    parser.add_argument("-piww", "--previous_workspace_in_level_with_window",
                        action="store_true",
                        help="Changes focus to the next workspace withing the level, and brings the current container along")
    parser.add_argument("-newww", "--new_workspace_in_level_with_window",
                        action="store_true",
                        help="Focuses a new workspace within the current level, and brings the current container along")
    # -- levels
    parser.add_argument("-nlww", "--next_level_with_window",
                        action="store_true",
                        help="Changes focus to the next level, and brings the current container along")
    parser.add_argument("-plww", "--previous_level_with_window",
                        action="store_true",
                        help="Changes focus to the previous level, and brings the current container along")
    
    # providing info for other scripts
    parser.add_argument("-lw", "--list_workspaces",
                        action="store_true",
                        help="Lists all the current workspaces")
    parser.add_argument("-cw", "--current_workspace",
                        action="store_true",
                        help="Returns the current workspace")
    parser.add_argument("-ci", "--current_index",
                        action="store_true",
                        help="Returns the current index")
    parser.add_argument("-cl", "--current_level",
                        action="store_true",
                        help="Returns the current level")
    parser.add_argument("--name_next_workspace_in_level",
                        action="store_true",
                        help="Returns the full name of the next workspace within this level")
    parser.add_argument("--name_previous_workspace_in_level",
                        action="store_true",
                        help="Returns the full name of the next workspace within this level")
    parser.add_argument("--name_new_workspace_in_level",
                        action="store_true",
                        help="Returns the full name of a new workspace within this level")
    return parser.parse_args()





def main_cli():
    args = process_arguments()
    conf = EtabliHandler(args.config)
    eta = Etabli(conf, current_output())
    eta.set_state()

    # Cycling
    # -- between workspaces
    if args.next_workspace:
        eta.cycle_within_current_output(1)
    elif args.previous_workspace:
        eta.cycle_within_current_output(-1)
    elif args.next_workspace_in_level:
        eta.cycle_within_current_level(1)
    elif args.previous_workspace_in_level:
        eta.cycle_within_current_level(-1)
    elif args.new_workspace_in_level:
        eta.new_workspace_within_level()
    elif args.next_level:
        eta.cycle_level(1)
    elif args.previous_level:
        eta.cycle_level(-1)
    # -- between workspaces, while bringing along a window
    elif args.next_workspace_with_window:
        eta.cycle_within_current_output_with_window(1)
    elif args.previous_workspace_with_window:
        eta.cycle_within_current_output_with_window(-1)
    elif args.next_workspace_in_level_with_window:
        eta.cycle_within_current_level_with_window(1)
    elif args.previous_workspace_in_level_with_window:
        eta.cycle_within_current_level_with_window(-1)
    elif args.new_workspace_in_level_with_window:
        eta.new_workspace_within_level_with_window()
    elif args.next_level_with_window:
        eta.cycle_level_with_window(1)
    elif args.previous_level_with_window:
        eta.cycle_level_with_window(-1)

    # printing information
    elif args.list_workspaces:
        eta.print_workspaces()
        if "prepare" in conf:
            print(conf["hrule"])
            print_potential_preparations(conf)
    elif args.current_workspace:
        print(current_workspace_name())
    elif args.current_index:
        print(conf.split_workspace_name(current_workspace_name())[-1])
    elif args.current_level:
        print(eta.current_level().name)
    elif args.name_next_workspace_in_level:
        lev, index = eta.name_other_workspace_within_level(1)
        print(conf.format_workspace_name(lev, index))
    elif args.name_previous_workspace_in_level:
        lev, index = eta.name_other_workspace_within_level(-1)
        print(conf.format_workspace_name(lev, index))
    elif args.name_new_workspace_in_level:
        lev, index = eta.name_new_workspace_in_level()
        print(conf.format_workspace_name(lev, index))
    # elif argv[1] == "rename_current_workspace":
    #     print(rename_workspace_by_guessing())
    else:
        print("use `etabli -h` to list the various input options")
    
if __name__ == "__main__":
    main_cli()
