# Main Python File
# (Should Start from CLI and run window.py if GUI is chosen)

import sys
import os

def print_usage():
    print(f"Descent is a genealogical analysis program that takes in files",file=sys.stdout)
    print(f"in the format of .csv and presents genealogical output.", file=sys.stdout)

def print_details():
    print(f"TODO: The list of options for each flag would be listed here.", file=sys.stdout)

def select_calc_option(str):
    print(f"TODO: Calculation option {str} would be selected here.", file=sys.stdout)

def select_out_option(str):
    print(f"TODO: Output option {str} would be selected here.", file=sys.stdout)

def cli_init(str_list):
    # Parameter flags and variables
    gui_enable = False

    # Read command line arguments
    argc = len(str_list)
    print(f"{argc} arguments read.", file=sys.stderr)

    # Parse command line arguments
    for v in range(len(str_list)):
        if "--g" in str_list[v]:
            gui_enable = True
        elif "--i" in str_list[v]:
            if len(str_list) >= v:
                print("--i flag requires a valid filename.", file=sys.stderr)
            else:
                input_filename = str_list[v + 1]
                if os.path.isfile(input_filename):
                    input_file = open(input_filename)
                else:
                    print(f"{input_filename} could not be found and was not opened.", file=sys.stderr)

        elif "--h" in str_list[v]:
            print_usage()
        elif "--hf" in str_list[v]:
            print_details()
        elif "--c" in str_list[v]:
            if len(str_list) >= v:
                print("--c flag requires a valid calculation option.", file=sys.stderr)
            else:
                select_calc_option(str_list[v + 1])
        elif "--o" in str_list[v]:
            if len(str_list) >= v:
                print("--o flag requires a valid output option.", file=sys.stderr)
            else:
                select_out_option(str_list[v + 1])

    if gui_enable:
        print(f"GUI flag enabled, starting GUI...", file=sys.stderr)

cli_init(sys.argv)