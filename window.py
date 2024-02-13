import tkinter as tk
from tkinter import ttk

# Function to Build Generic Tabs
def create_tab(tab_control, title):
    frame = ttk.Frame(tab_control)
    tab_control.add(frame, text=title)
    # label = ttk.Label(frame, text=f"This is the {title} tab")
    # label.pack(expand=True, fill="both")

# Starts Window
root = tk.Tk()

# Formats Window
root.title('Descent')
root.geometry('500x350')
root.eval('tk::PlaceWindow . center')

# Creates Notebook (Tabs)
tab_control = ttk.Notebook(root, padding=(10, 10))
tab_control.pack(expand=True, fill="both")


# Create tabs
create_tab(tab_control, "Editor")
create_tab(tab_control, "Relatedness")
create_tab(tab_control, "Founders")
create_tab(tab_control, "Lineages")
create_tab(tab_control, "Kin Counter")
create_tab(tab_control, "Kin")
create_tab(tab_control, "Groups")
create_tab(tab_control, "Plot")
create_tab(tab_control, "PCA")
create_tab(tab_control, "Help")


# Keeps Window Open
root.mainloop()