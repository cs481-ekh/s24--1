import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import tkinter as tk
from tkinter import *
from tkinter import filedialog, ttk, messagebox
from tkhtmlview import HTMLLabel
import pandas as pd
from pandastable import Table, TableModel # Excellent Documentation: https://pandastable.readthedocs.io/en/latest/pandastable.html
from DataManager import DataManager

data_manager = None
width = 600
height = 400

class GUI:
    @classmethod
    def run(cls):
        root = tk.Tk()
        app = cls(root)
        root.mainloop()

    def __init__(self, root):
        self.root = root
        self.root.title("DataManager GUI")

        # Sizing
        self.root.minsize(width, height)

        # Create Menu Bar
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        # File Menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Open File", command=self.load_csv)
        self.file_menu.add_command(label="Save", command=self.save_file)
        self.file_menu.add_command(label="Save As", command=self.save_as_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.quit)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        # Edit Menu
        self.edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        # Add Edit menu options here
        self.menu_bar.add_cascade(label="Edit", menu=self.edit_menu)

        # Export Menu
        self.export_menu = tk.Menu(self.menu_bar, tearoff=0)
        # Add Export menu options here
        self.menu_bar.add_cascade(label="Export", menu=self.export_menu)

        self.CreateNotebook()

    # Builds global tabs
    def CreateNotebook(self):
        # Notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both")

        # Startup Tab - Help
        self.help_frame = tk.Frame(self.notebook)
        self.notebook.add(self.help_frame, text="Help")
        self.add_help_content()

    def TabSetup(self):
        "Set up notebook tabs."
        self.ClearTabs()
        self.CreateNotebook()
        self.editor_panel = EditorPanel(self.notebook, self)
        self.notebook.insert(0, self.editor_panel, text="Editor")
        self.notebook.insert(1, RelatednessPanel(self.notebook, self), text="Relatedness")
        self.notebook.insert(2, FoundersPanel(self.notebook), text="Founders")
        self.notebook.insert(3, LineagePanel(self.notebook, self), text="Lineages")
        self.notebook.insert(4, KinGroupPanel(self.notebook), text="Kin Counter")
        self.notebook.insert(5, KinPanel(self.notebook), text="Kin")
        self.notebook.insert(6, GroupPanel(self.notebook), text="Groups")
        self.notebook.insert(7, PlotPanel(self.notebook), text="Plot")
        self.notebook.insert(8, PCAPanel(self.notebook), text="PCA")
        self.notebook.select(0)
    
    def ClearTabs(self):
        self.notebook.destroy()

    def load_csv(self):
        filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if filename:
            global data_manager
            data_manager = DataManager(filename)
            print("CSV loaded successfully.")

            self.TabSetup()
    
    def save_file(self):
        # Add logic to save file
        print("Save is In Development")
    
    def save_as_file(self):
        # Add logic to save file as
        print("Save As is In Development")

    def create_dataframe(self):
        if self.data_manager:
            self.data_manager.createPandasDataFrame()
            print("DataFrame created successfully.")
        else:
            print("Please load a CSV file first.")

    def check_errors(self):
        if self.data_manager:
            errors = self.data_manager.checkForErrors()
            if not errors:
                print("No errors found.")
        else:
            print("Please create a DataFrame first.")
    
    # Called before any Calculation in all Tabs except Editor
    # Builds the backend DataFrame based on User Input
    def build_data_manager(self):
        global data_manager

        # Return if DataFrame Already Exists
        if not data_manager.df.empty:
            return
        
        # Gain access to Editor Panel
        editor = self.editor_panel

        # Build Parameters for DataManager DataFrame Creation
        columns = [editor.egoColumnValue.get(),\
                   editor.fatherColumnValue.get(),\
                   editor.motherColumnValue.get(),\
                   editor.sexColumnValue.get(),\
                   editor.livingColumnValue.get()]
        values = [editor.maleValue.get(),\
                  editor.femaleValue.get(),\
                  editor.aliveValue.get(),\
                  editor.deadValue.get(),\
                  editor.missingValue.get()]
        headerCheckbox = editor.removeHeader.get()

        # Call createPandasDataFrame()        
        data_manager.createPandasDataFrame(columns, values, headerCheckbox)
        
    # Loads Help Content into Help Tab
    # Runs when Program Boots
    def add_help_content(self):
        help_pane = ttk.PanedWindow(self.help_frame, orient="horizontal")
        help_pane.pack(expand=True, fill="both")

        # Navigation Menu
        nav_menu_frame = tk.Frame(help_pane, width=150)
        nav_menu_frame.grid(row=0, column=0, sticky="ns")

        nav_menu_label = tk.Label(nav_menu_frame, text="Navigation Menu")
        nav_menu_label.grid(row=0, column=0)

        # Sample Navigation Items
        nav_items = ["Introduction", "Usage", "FAQs", "Contact Us"]
        for idx, item in enumerate(nav_items):
            tk.Button(nav_menu_frame, text=item).grid(row=idx+1, column=0, sticky="ew")

        # HTML Content
        html_frame = tk.Frame(help_pane)
        help_pane.add(html_frame)

        # Read HTML content from file
        with open("Assets/HelpPanel/index.html", "r") as f:
            html_content = f.read()

        # Insert HTML content into HTMLLabel widget
        help_label = HTMLLabel(html_frame, html=html_content)
        help_label.grid(row=0, column=0, sticky="nsew")

class EditorPanel(tk.Frame):
    def __init__(self, parent, gui):
        super().__init__(parent)
        self.parent = parent
        self.gui = gui

        self.firstRow = None
        self.removeHeader = BooleanVar()

        # Create widgets
        self.create_panel_layout()

        # Fill Data Table with DataFrame
        global data_manager
        self.startingDataFrame = pd.DataFrame(data_manager.data)
        self.load_data_frame(self.startingDataFrame)

        # Fills Dropdown Menus with options
        self.load_selection_menu(self.startingDataFrame)

    # Builds Panel Layout for 3 sections; Data, Error, and Selection
    def create_panel_layout(self):
        self.upper = tk.Frame(self)
        self.upper.pack(side = 'top')
        self.data_pane = tk.Frame(self.upper, highlightbackground='Black', highlightthickness=2)
        self.data_pane.pack(side = "left")
        self.error_pane = tk.Frame(self.upper, highlightbackground='Black', highlightthickness=2, height=height, width=width * 0.3)
        self.error_pane.pack(side = "right")
        self.selection_pane = tk.Frame(self, highlightbackground='Black', highlightthickness=2, height=height * 0.3, width=width)
        self.selection_pane.pack(side = "bottom", fill=BOTH)

    # Loads dataframe into grid
    def load_data_frame(self, df):
        self.data_pane.pack(fill=BOTH,expand=1)
        self.table = pt = Table(self.data_pane, dataframe=df,
                                showtoolbar=False, showstatusbar=True)
        pt.show()

    def load_selection_menu(self, df):
        # Contains Header Checkbox
        containsHeading = Checkbutton(self.selection_pane, text="Row one contains column headings", variable=self.removeHeader, command=self.toggle_first_row_header)
        containsHeading.grid(row=0, column=0, columnspan=4)

        # Check for Incest Checkbox
        incest = Checkbutton(self.selection_pane, text="Incest")
        incest.grid(row=0, column=10)

        # Ego Dropdown Menu
        ttk.Label(self.selection_pane, text = "Ego :", 
          font = ("Times New Roman", 10)).grid(row=1, 
          column=0) 
        self.egoColumnValue = tk.StringVar()
        self.egoDropdown = ttk.Combobox(self.selection_pane, width = 10, textvariable = self.egoColumnValue)
        self.egoDropdown['values'] = df.columns.tolist()
        self.egoDropdown.grid(row=1, column=1)

        # Father Dropdown Menu
        ttk.Label(self.selection_pane, text = "Father:", 
          font = ("Times New Roman", 10)).grid(row=1, 
          column=2) 
        self.fatherColumnValue = tk.StringVar()
        self.fatherDropdown = ttk.Combobox(self.selection_pane, width = 10, textvariable = self.fatherColumnValue)
        self.fatherDropdown['values'] = df.columns.tolist()
        self.fatherDropdown.grid(row=1, column=3)

        # Mother Dropdown Menu
        ttk.Label(self.selection_pane, text = "Mother:", 
          font = ("Times New Roman", 10)).grid(row=2, 
          column=2) 
        self.motherColumnValue = tk.StringVar()
        self.motherDropdown = ttk.Combobox(self.selection_pane, width = 10, textvariable = self.motherColumnValue)
        self.motherDropdown['values'] = df.columns.tolist()
        self.motherDropdown.grid(row=2, column=3)

        # Sex Dropdown Menu
        ttk.Label(self.selection_pane, text = "Sex:", 
          font = ("Times New Roman", 10)).grid(row=2, 
          column=0) 
        self.sexColumnValue = tk.StringVar()
        self.sexDropdown = ttk.Combobox(self.selection_pane, width = 10, textvariable = self.sexColumnValue)
        self.sexDropdown['values'] = df.columns.tolist()
        self.sexDropdown.grid(row=2, column=1)

        # Living Dropdown Menu
        ttk.Label(self.selection_pane, text = "Living:", 
          font = ("Times New Roman", 10)).grid(row=1, 
          column=4) 
        self.livingColumnValue = tk.StringVar()
        self.livingDropdown = ttk.Combobox(self.selection_pane, width = 10, textvariable = self.livingColumnValue)
        self.livingDropdown['values'] = df.columns.tolist()
        self.livingDropdown.grid(row=1, column=5)

        # Male Entry Box
        ttk.Label(self.selection_pane, text = "Male:", 
          font = ("Times New Roman", 10)).grid(row=1, 
          column=6) 
        self.maleValue = tk.Entry(self.selection_pane,
                        width = 8)
        self.maleValue.grid(row=1, column=7)
        self.maleValue.insert(0, "Male") # Default Value

        # Female Entry Box
        ttk.Label(self.selection_pane, text = "Female:", 
          font = ("Times New Roman", 10)).grid(row=2, 
          column=6) 
        self.femaleValue = tk.Entry(self.selection_pane,
                        width = 8)
        self.femaleValue.grid(row=2, column=7)
        self.femaleValue.insert(0, "Female") # Default Value

        # Alive Textbox
        ttk.Label(self.selection_pane, text = "Alive:", 
          font = ("Times New Roman", 10)).grid(row=1, 
          column=8) 
        self.aliveValue = tk.Entry(self.selection_pane,
                        width = 8)
        self.aliveValue.grid(row=1, column=9)
        self.aliveValue.insert(0, "Alive") # Default Value

        # Dead Textbox
        ttk.Label(self.selection_pane, text = "Dead:", 
          font = ("Times New Roman", 10)).grid(row=2, 
          column=8) 
        self.deadValue = tk.Entry(self.selection_pane,
                        width = 8)
        self.deadValue.grid(row=2, column=9)
        self.deadValue.insert(0, "Dead") # Default Value

        # Missing Textbox
        ttk.Label(self.selection_pane, text = "Missing:", 
          font = ("Times New Roman", 10)).grid(row=2, 
          column=10) 
        self.missingValue = tk.Entry(self.selection_pane,
                        width = 8)
        self.missingValue.grid(row=1, column=10)
        self.missingValue.insert(0, "999") # Default Value

        # Check Error Button
        checkErrorButton = tk.Button(self.selection_pane, 
                                text = "Check Errors",  
                                command = self.load_errors)
        checkErrorButton.grid(row=0, column=6, columnspan=3)

    # TODO: Causes Error because the Datamanager Dataframe does not yet exist
    # TODO: Ensure errors allow for incest checking
    # Displays all errors from DataManager
    def load_errors(self):
        v = Scrollbar(self.error_pane, orient='vertical')
        v.pack(side='right', fill='y')

        text = Text(self.error_pane, yscrollcommand=v.set)

        for e in errors:
            text.insert(END, e + "\n\n")

        text.pack()
        pass

    # Gets called with Checkbox (First row contains Header)
    # Updates pandastable dataframe; deletes/adds first row, updates column names
    def toggle_first_row_header(self):
        if self.removeHeader.get(): # Is Checked
            self.table.setSelectedRow(0)
            self.firstRow = self.table.getSelectedRowData()

            # Update Column Names
            self.table.model.df.columns = self.firstRow.values[0]

            self.table.deleteRow()
        else: # Not Checked
            self.table.model.df = self.startingDataFrame

            # Reset Columns to Numbers
            column_names = []
            for x in range(len(self.table.model.df.columns)):
                column_names.append(x)
            self.table.model.df.columns = column_names

        self.table.redrawVisible()
        self.table.statusbar.update()
        
        # Update Dropdown Values
        self.egoDropdown['values'] = self.table.model.df.columns.tolist()
        self.fatherDropdown['values'] = self.table.model.df.columns.tolist()
        self.motherDropdown['values'] = self.table.model.df.columns.tolist()
        self.sexDropdown['values'] = self.table.model.df.columns.tolist()
        self.livingDropdown['values'] = self.table.model.df.columns.tolist()

class RelatednessPanel(tk.Frame):
    def __init__(self, parent, gui):
        super().__init__(parent)
        self.parent = parent
        self.gui = gui

        self.create_panel_layout()
    
    # Sizes the Frame and adds a button
    def create_panel_layout(self):
        self.pane = tk.Frame(self, highlightbackground='Black', highlightthickness=2)
        self.pane.pack(fill=BOTH, expand=True)

        # Create Button
        self.calculate_button = Button(self.pane, text="Calculate Relatedness Stats", command=self.display_relatedness_data)
        self.calculate_button.pack(side="bottom")

    # Displays Relatedness Data in a Pandastable
    def display_relatedness_data(self):
        # User Feedback: Alter Cursor because function takes a while
        self.gui.root.config(cursor="watch")
        self.gui.root.update()

        self.gui.build_data_manager()
        # Delete Button
        self.calculate_button.pack_forget()
        # Create Pandastable
        global data_manager
        self.pane.pack(fill=BOTH,expand=1)
        self.table = pt = Table(self.pane, dataframe=data_manager.getRelatednessStats(),
                                showtoolbar=False, showstatusbar=True)
        pt.show()
        
        pt.redrawVisible()

        # Return Cursor to normal
        self.gui.root.config(cursor="")

class FoundersPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.temp = tk.Frame(self, highlightbackground='Black', highlightthickness=2)
        self.temp.pack(side = "bottom")

        label = Label(self.temp, text="In Development")
        label.pack()

class LineagePanel(tk.Frame):
    def __init__(self, parent, gui):
        super().__init__(parent)
        self.parent = parent
        self.gui = gui

        self.create_panel_layout()
    
    # Sizes the Frame and adds a button
    def create_panel_layout(self):
        self.pane = tk.Frame(self, highlightbackground='Black', highlightthickness=2)
        self.pane.pack(fill=BOTH, expand=True)

        # Create Button
        self.calculate_button = Button(self.pane, text="Calculate Lineages", command=self.display_lineage_data)
        self.calculate_button.pack(side="bottom")
    
    # Displays Relatedness Data in a Pandastable
    def display_lineage_data(self):
        # User Feedback: Alter Cursor because function takes a while
        self.gui.root.config(cursor="watch")
        self.gui.root.update()

        self.gui.build_data_manager()
        # Delete Button
        self.calculate_button.pack_forget()
        # Create Pandastable
        global data_manager
        self.pane.pack(fill=BOTH,expand=1)
        self.table = pt = Table(self.pane, dataframe=data_manager.getLineages(),
                                showtoolbar=False, showstatusbar=True)
        pt.show()
        
        pt.redrawVisible()

        # Return Cursor to normal
        self.gui.root.config(cursor="")

class KinGroupPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.temp = tk.Frame(self, highlightbackground='Black', highlightthickness=2)
        self.temp.pack(side = "bottom")

        label = Label(self.temp, text="In Development")
        label.pack()

class KinPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.temp = tk.Frame(self, highlightbackground='Black', highlightthickness=2)
        self.temp.pack(side = "bottom")

        label = Label(self.temp, text="In Development")
        label.pack()

class GroupPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.temp = tk.Frame(self, highlightbackground='Black', highlightthickness=2)
        self.temp.pack(side = "bottom")

        label = Label(self.temp, text="In Development")
        label.pack()

class PlotPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.temp = tk.Frame(self, highlightbackground='Black', highlightthickness=2)
        self.temp.pack(side = "bottom")

        label = Label(self.temp, text="In Development")
        label.pack()

class PCAPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.temp = tk.Frame(self, highlightbackground='Black', highlightthickness=2)
        self.temp.pack(side = "bottom")

        label = Label(self.temp, text="In Development")
        label.pack()

if __name__ == "__main__":
    GUI.run()
