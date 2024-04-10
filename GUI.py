import tkinter as tk
from tkinter import filedialog, ttk
from tkhtmlview import HTMLLabel
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
        self.editor_panel = EditorPanel(self.notebook)
        self.notebook.add(self.editor_panel, text="Editor")

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
        self.data = None  # To store CSV data

        # Create widgets
        self.create_widgets()

    def create_widgets(self):

        # Display CSV data (using a treeview widget for tabular data)
        self.tree = ttk.Treeview(self)
        self.tree["columns"] = ("#1", "#2", "#3", "#4", "#5")  # Adjust as per your CSV columns
        self.tree.heading("#0", text="Index")
        self.tree.heading("#1", text="Column 1")
        self.tree.heading("#2", text="Column 2")
        self.tree.heading("#3", text="Column 3")
        self.tree.heading("#4", text="Column 4")
        self.tree.heading("#5", text="Column 5")
        self.tree.pack(expand=True, fill="both")

        # Error text box
        self.error_text = tk.Text(self, height=10, width=50)
        self.error_text.pack(side="right", fill="y")

        # Select columns and expected values
        self.column_selection = tk.Listbox(self, height=5, selectmode="multiple")
        self.column_selection.pack()
        self.expected_values_entry = tk.Entry(self)
        self.expected_values_entry.pack()

    def load_csv(self):
        # Load CSV file
        filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if filename:
            self.data = pd.read_csv(filename)
            self.display_data()

    def display_data(self):
        # Clear existing data in the treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Insert CSV data into the treeview
        for idx, row in self.data.iterrows():
            self.tree.insert("", tk.END, text=str(idx), values=tuple(row))

if __name__ == "__main__":
    GUI.run()
