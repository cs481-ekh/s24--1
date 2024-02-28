# Main Python File
# (Should Start from CLI and run window.py if GUI is chosen)

import sys

# Parameter flags
gui_enable = False

# Read command line arguments
argc = len(sys.argv)
print(f"{argc} arguments read. Arguments:", file=sys.stderr)

for v in sys.argv:
    print(v, file=sys.stderr, end="")
print("", file=sys.stderr)

if gui_enable:
    print(f"GUI flag enabled, starting GUI...", file=sys.stderr)