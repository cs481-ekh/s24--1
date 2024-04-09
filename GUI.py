import tkinter as tk
from tkinter import filedialog, ttk
from DataManager import DataManager

class GUI:
    @classmethod
    def run(cls):
        root = tk.Tk()
        app = cls(root)
        root.mainloop()

    def __init__(self, root):
        self.root = root
        self.root.title("DataManager GUI")
        self.data_manager = None

        # Sizing
        self.root.minsize(600, 400)

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

        # Notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both")


        #region ========= Tabs =========

        # Editor
        self.editor_frame = tk.Frame(self.notebook)
        self.notebook.add(self.editor_frame, text="Editor")

        # Relatedness
        self.relatedness_frame = tk.Frame(self.notebook)
        self.notebook.add(self.relatedness_frame, text="Relatedness")

        # Founders
        self.founder_frame = tk.Frame(self.notebook)
        self.notebook.add(self.founder_frame, text="Founders")

        # Lineages
        self.lineages_frame = tk.Frame(self.notebook)
        self.notebook.add(self.lineages_frame, text="Lineages")

        # Kin Counter
        self.kin_counter_frame = tk.Frame(self.notebook)
        self.notebook.add(self.kin_counter_frame, text="Kin Counter")

        # Kin
        self.kin_frame = tk.Frame(self.notebook)
        self.notebook.add(self.kin_frame, text="Kin")

        # Groups
        self.groups_frame = tk.Frame(self.notebook)
        self.notebook.add(self.groups_frame, text="Groups")

        # Plot
        self.plot_frame = tk.Frame(self.notebook)
        self.notebook.add(self.plot_frame, text="Plot")

        # PCA
        self.pca_frame = tk.Frame(self.notebook)
        self.notebook.add(self.pca_frame, text="PCA")

        # Help
        self.help_frame = tk.Frame(self.notebook)
        self.notebook.add(self.help_frame, text="Help")
        self.add_help_content()

        # Hide all Tabs Except Help
        for i in range(len(self.notebook.tabs())):
            if self.notebook.tab(i, "text") != "Help":
                self.notebook.hide(i)

        #endregion

    def load_csv(self):
        filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if filename:
            self.data_manager = DataManager(filename)
            print("CSV loaded successfully.")

            # Shows all Tabs after successful load
            for i in range(len(self.notebook.tabs())):
                self.notebook.select(i)
            
            # Selects Editor Tab
            self.notebook.select(0)
    
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
    
    def add_help_content(self):
        # Add content to the Help tab
        label = tk.Label(self.help_frame, text="Welcome to DataManager GUI!\n\nTo get started, open a CSV file.")
        label.pack(expand=True, fill="both")

if __name__ == "__main__":
    GUI.run()