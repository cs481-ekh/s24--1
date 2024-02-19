# import tkinter as tk
# from tkinter import filedialog
# from tkinter import messagebox

# def open_file():
#     # This function will be called when "Open" is clicked
#     file_path = filedialog.askopenfilename()
#     if file_path:
#         # Here, you can add the code to handle the opening of the file
#         messagebox.showinfo("Information", f"You selected: {file_path}")
#         # Example: Open and read the file, load data, etc.

# # Starts Window
# window = tk.Tk()

# # Formats Window
# window.title('Descent')
# window.geometry('500x350')
# window.eval('tk::PlaceWindow . center')

# # Create a menu bar
# menu_bar = tk.Menu(window)

# # Create a "File" menu
# file_menu = tk.Menu(menu_bar, tearoff=0)
# file_menu.add_command(label="Open", command=open_file)
# file_menu.add_separator()
# file_menu.add_command(label="Exit", command=window.quit)
# menu_bar.add_cascade(label="File", menu=file_menu)

# # Create an "Edit" menu
# edit_menu = tk.Menu(menu_bar, tearoff=0)
# # Add items to the "Edit" menu if needed
# # edit_menu.add_command(label="...", command=...)
# menu_bar.add_cascade(label="Edit", menu=edit_menu)

# # Create an "Export" menu
# export_menu = tk.Menu(menu_bar, tearoff=0)
# # Add items to the "Export" menu if needed
# # export_menu.add_command(label="...", command=...)
# menu_bar.add_cascade(label="Export", menu=export_menu)

# # Set the menu bar on the window
# window.config(menu=menu_bar)

# # Keeps Window Open
# window.mainloop()






#============================================================================================================================================================================================




import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk

class WelcomeWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Descent Welcome')
        self.geometry('500x350')
        self.eval('tk::PlaceWindow . center')

        #create a menu bar
        menu_bar = tk.Menu(self)

        #create a file menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)

        #set the menu bar on the window
        self.config(menu=menu_bar)

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if file_path:
            self.destroy()  # Close the welcome window
            MainProgramWindow(file_path)  #open the main program window

class MainProgramWindow(tk.Tk):
    def __init__(self, file_path):
        super().__init__()
        self.title('Descent')
        self.geometry('800x600')
        self.eval('tk::PlaceWindow . center')
        

# Create and run the welcome window
welcome_window = WelcomeWindow()
welcome_window.mainloop()

