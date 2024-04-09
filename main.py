# Main Python File
# (Should Start from CLI and run window.py if GUI is chosen)

import sys
#from Descent import *
from DataManager import *
import os

def print_usage():
    return "Descent is a genealogical analysis program that takes in files \nin the format of .csv and presents genealogical output."
    return "Descent is a genealogical analysis program that takes in files \nin the format of .csv and presents genealogical output."

def print_details():
    return print_usage() + "\nTODO: The list of options for each flag would be listed here."
    return print_usage() + "\nTODO: The list of options for each flag would be listed here."

def select_calc_option(str):
    print(f"TODO: Calculation option {str} would be selected here.", file=sys.stdout)

def select_out_option(str):
    print(f"TODO: Output option {str} would be selected here.", file=sys.stdout)


# Parameter flags and variables
gui_enable = False
dataMan = None # DataManager Object

def cli_init(str_list):
    # Read command line arguments
    retVal = ""
    argc = len(str_list)
    print(f"{argc} arguments read.", file=sys.stderr)

    # Parse command line arguments
    for v in range(len(str_list)):
        if "--h" in str_list[v]:
            retVal = print_usage()
            break
        elif "--hf" in str_list[v]:
            retVal = print_details()
            break
        elif "--i" in str_list[v]:
            if v >= (len(str_list) + 1):
                retVal += "--i flag requires a valid filename." + "\n"
            else:
                input_filename = str_list[v + 1]
                print(os.getcwd())
                if os.path.isfile(input_filename):
                    global dataMan
                    dataMan = DataManager(input_filename)
                    dataMan.createPandasDataFrame(columns=['PersonID', 'FatherID', 'MotherID', 'Sex', 'Deceased'], \
                                                  values=['Male', 'Female', 'FALSE', 'TRUE', '9999'], \
                                                  removeHeader=True)

                    dataMan.checkForErrors()

                    # Example Uses
                    #print(dataMan.getFounders())
                    print(dataMan.getLineages())
                else:
                    retVal += f"{input_filename} could not be found and was not opened.\n"

        elif "--g" in str_list[v]:
            global gui_enable
            gui_enable = True
        elif "--c" in str_list[v]:
            if len(str_list) >= v:
                retVal += "--c flag requires a valid calculation option."
            else:
                select_calc_option(str_list[v + 1])
        elif "--o" in str_list[v]:
            if len(str_list) >= v:
                retVal += "--o flag requires a valid output option."
            else:
                select_out_option(str_list[v + 1])
    return retVal

print(cli_init(sys.argv))
if gui_enable:
    print(f"GUI flag enabled, starting GUI...", file=sys.stderr)
    #BuildApp()