#!/usr/bin/env python


import argparse
from pathlib import Path
from etabli import *


def process_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config",
                        nargs="?",
                        type=str,
                        default=default_config_path,
                        help="Path to the configuration file")
    parser.add_argument("-a", "--all",
                        action="store_true",
                        help="Displays all the entries on the current board")
    parser.add_argument("-l", "--level",
                        type=str,
                        help="The level whose board you want to interact with")
    parser.add_argument("-n", "--name",
                        type=str,
                        help="The name of the variable to interact with")
    parser.add_argument("-v", "--value",
                        type=str,
                        help="The value to give to the variable")
    parser.add_argument("-e", "--erase",
                        action="store_true",
                        help="The given variable will be erased")
    parser.add_argument("-q", "--query",
                        action="store_true",
                        help="The given variable will be returned")                        
    return parser.parse_args()


def main_cli():
    args = process_arguments()
    conf = EtabliHandler(args.config)
    b = Board(conf["board_path"])

    
    if args.all:
        print(b)
    else:
        # some post processing of the arguments
        if not args.level:
            args.level = conf.split_workspace_name(current_workspace_name())[0]
        elif args.query and args.erase:
            raise Exception("can't both query and erase a variable")
        elif args.query and args.value:
            raise Exception("can't both query and set a variable")
        elif args.erase and args.value:
            raise Exception("can't both set and erase a variable")

        # main switch
        if args.erase:
            if args.level not in b.db:
                raise Exception("couldn't erase variable from absent level " + args.level)
            elif args.name not in b.db[args.level]:
                raise Exception("no variable with name " + args.name)
            else:
                del b.db[args.level][args.name]
                print(b)
                b.save()
        elif args.value:
            if not args.level:
                raise Exception("the level must be specified")
            elif not args.name:
                raise Exception("the name must be specified")
            b.stick_to_level(args.level, args.name, args.value)
            print(b)
            b.save()
        elif args.query:
            if not args.level:
                raise Exception("the level must be specified")
            elif not args.name:
                raise Exception("the name must be specified")
            print(b(args.level, args.name))
