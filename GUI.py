import tkinter as tk
from tkinter import *
from tkinter import filedialog, ttk, messagebox
from tkhtmlview import HTMLLabel
import pandas as pd
from pandastable import Table, TableModel
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
        self.notebook.insert(0, EditorPanel(self.notebook), text="Editor")
        self.notebook.insert(1, RelatednessPanel(self.notebook), text="Relatedness")
        self.notebook.insert(2, FoundersPanel(self.notebook), text="Founders")
        self.notebook.insert(3, LineagePanel(self.notebook), text="Lineages")
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
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.boolFirstRow = BooleanVar()

        # Create widgets
        self.create_panel_layout()

        # Fill Data Table with DataFrame
        global data_manager
        tempDF = pd.DataFrame(data_manager.data)
        self.load_data_frame(tempDF)

        # Fills Dropdown Menus with options
        self.load_selection_menu(tempDF)

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

    # Displays Dropdown Menus, Check Boxes, Text Entries, and Check Errors Button
    def load_selection_menu(self, df):
        # Contains Header Checkbox
        containsHeading = Checkbutton(self.selection_pane, text="Row one contains column headings", variable=self.boolFirstRow, command=self.toggle_first_row_header)
        containsHeading.grid(row=0, column=0, columnspan=4)

        # Check for Incest Checkbox
        incest = Checkbutton(self.selection_pane, text="Incest")
        incest.grid(row=0, column=10)

        # Ego Dropdown Menu
        ttk.Label(self.selection_pane, text = "Ego :", 
          font = ("Times New Roman", 10)).grid(row=1, 
          column=0) 
        n = tk.StringVar() 
        egoDropdown = ttk.Combobox(self.selection_pane, width = 10, textvariable = n)
        egoDropdown['values'] = df.columns.tolist()
        egoDropdown.grid(row=1, column=1)

        # Father Dropdown Menu
        ttk.Label(self.selection_pane, text = "Father:", 
          font = ("Times New Roman", 10)).grid(row=1, 
          column=2) 
        n = tk.StringVar() 
        fatherDropdown = ttk.Combobox(self.selection_pane, width = 10, textvariable = n)
        fatherDropdown['values'] = df.columns.tolist()
        fatherDropdown.grid(row=1, column=3)

        # Mother Dropdown Menu
        ttk.Label(self.selection_pane, text = "Mother:", 
          font = ("Times New Roman", 10)).grid(row=2, 
          column=2) 
        n = tk.StringVar() 
        motherDropdown = ttk.Combobox(self.selection_pane, width = 10, textvariable = n)
        motherDropdown['values'] = df.columns.tolist()
        motherDropdown.grid(row=2, column=3)

        # Sex Dropdown Menu
        ttk.Label(self.selection_pane, text = "Sex:", 
          font = ("Times New Roman", 10)).grid(row=2, 
          column=0) 
        n = tk.StringVar() 
        sexDropdown = ttk.Combobox(self.selection_pane, width = 10, textvariable = n)
        sexDropdown['values'] = df.columns.tolist()
        sexDropdown.grid(row=2, column=1)

        # Living Dropdown Menu
        ttk.Label(self.selection_pane, text = "Living:", 
          font = ("Times New Roman", 10)).grid(row=1, 
          column=4) 
        n = tk.StringVar() 
        livingDropdown = ttk.Combobox(self.selection_pane, width = 10, textvariable = n)
        livingDropdown['values'] = df.columns.tolist()
        livingDropdown.grid(row=1, column=5)

        # Male Textbox
        ttk.Label(self.selection_pane, text = "Male:", 
          font = ("Times New Roman", 10)).grid(row=1, 
          column=6) 
        maleValue = tk.Text(self.selection_pane, 
                        height = 1, 
                        width = 5)
        maleValue.grid(row=1, column=7)

        # Female Textbox
        ttk.Label(self.selection_pane, text = "Female:", 
          font = ("Times New Roman", 10)).grid(row=2, 
          column=6) 
        femaleValue = tk.Text(self.selection_pane, 
                        height = 1, 
                        width = 5)
        femaleValue.grid(row=2, column=7)

        # Alive Textbox
        ttk.Label(self.selection_pane, text = "Alive:", 
          font = ("Times New Roman", 10)).grid(row=1, 
          column=8) 
        aliveValue = tk.Text(self.selection_pane, 
                        height = 1, 
                        width = 5)
        aliveValue.grid(row=1, column=9)

        # Dead Textbox
        ttk.Label(self.selection_pane, text = "Dead:", 
          font = ("Times New Roman", 10)).grid(row=2, 
          column=8) 
        deadValue = tk.Text(self.selection_pane, 
                        height = 1, 
                        width = 5)
        deadValue.grid(row=2, column=9)

        # Missing Textbox
        ttk.Label(self.selection_pane, text = "Missing:", 
          font = ("Times New Roman", 10)).grid(row=2, 
          column=10) 
        deadValue = tk.Text(self.selection_pane, 
                        height = 1, 
                        width = 5)
        deadValue.grid(row=1, column=10)

        # Check Error Button
        checkErrorButton = tk.Button(self.selection_pane, 
                                text = "Check Errors",  
                                command = self.load_errors)
        checkErrorButton.grid(row=0, column=6, columnspan=3)

    def load_errors(self):
        v = Scrollbar(self.error_pane, orient='vertical')
        v.pack(side='right', fill='y')

        text = Text(self.error_pane, yscrollcommand=v.set)

        global data_manager
        errors = data_manager.checkForErrors()

        for e in errors:
            text.insert(END, e + "\n\n")

        text.pack()
        pass

    def toggle_first_row_header(self):
        
        if self.boolFirstRow.get(): # Is Checked
            pass
        else: # Not Checked
            pass
        pass

class RelatednessPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.temp = tk.Frame(self, highlightbackground='Black', highlightthickness=2)
        self.temp.pack()

        label = Label(self.temp, text="In Development")
        label.pack()

class FoundersPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.temp = tk.Frame(self, highlightbackground='Black', highlightthickness=2)
        self.temp.pack(side = "bottom")

        label = Label(self.temp, text="In Development")
        label.pack()

class LineagePanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.temp = tk.Frame(self, highlightbackground='Black', highlightthickness=2)
        self.temp.pack(side = "bottom")

        label = Label(self.temp, text="In Development")
        label.pack()

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
