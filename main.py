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

# Parameter flags and variables
gui_enable = False

# Read command line arguments
argc = len(sys.argv)
print(f"{argc} arguments read.", file=sys.stderr)

# Parse command line arguments
for v in range(len(sys.argv)):
    if "--g" in sys.argv[v]:
        gui_enable = True
    elif "--i" in sys.argv[v]:
        if len(sys.argv) <= v:
            print("--i flag requires a valid filename.", file=sys.stderr)
        else:
            input_filename = sys.argv[v + 1]
            if os.path.isfile(input_filename):
                input_file = open(input_filename)
            else:
                print(f"{input_filename} could not be found and was not opened.", file=sys.stderr)

    elif "--h" in sys.argv[v]:
        print_usage()
    elif "--hf" in sys.argv[v]:
        print_details()
    elif "--c" in sys.argv[v]:
        if len(sys.argv) <= v:
            print("--c flag requires a valid calculation option.", file=sys.stderr)
        else:
            select_calc_option(sys.argv[v + 1])

if gui_enable:
    print(f"GUI flag enabled, starting GUI...", file=sys.stderr)