import wx
from wx import *
import wx.html as html

appTitle = 'Descent'
__version__ = "2.0"

class MyFrame(wx.Frame):
    # Runs automatically, initializes application opbject
    def __init__(self, parent, title):
        super(MyFrame, self).__init__(parent, title=title, size=(600, 400))
        
        # Create a status bar
        self.CreateStatusBar()
        self.SetStatusText("Welcome to wxPython!")
        self.SetTitle(title + ' ' + __version__)

        # Menu ID numbers for Events
        self.ID_ABOUT   = 101
        self.ID_EXIT    = 102
        self.ID_OPEN    = 103
        self.ID_SAVE    = 104
        self.ID_SAVEAS  = 106
        self.ID_KINDEMCOM = 107
        self.ID_COPY = 108
        self.ID_PASTE = 109
        self.ID_EXPORT   = 110
        self.ID_EXPORTRMATRIX = 111
        self.ID_RELOAD = 112
        self.ID_EXPORTGMATRIX = 113
        self.ID_EXPORTKINDEMCOM = 114

        ####################
        ## Menu Bar Setup ##
        ####################

        # Set up file menu
        self.fileMenu = wx.Menu()
        self.fileMenu.Append(self.ID_OPEN, "&Open...\tCtrl-O", "Open a tab-delimited data file")
        self.fileMenu.Append(self.ID_SAVE, "&Save\tCtrl-S", "Save the current data file in tab-delimited format")
        self.fileMenu.Append(self.ID_SAVEAS, "Sa&ve as...", "Save the current data in a new file in tab-delimited format")
        self.fileMenu.Append(self.ID_KINDEMCOM, "&Import KINDEMCOM...", "Import KINDEMCOM Ego File")
        self.fileMenu.Append(self.ID_EXIT, "E&xit\tCtrl-Q", "Terminate the program")
        
        # Disable file menu items that require an open file
        self.fileMenu.Enable(self.ID_SAVE, False)
        self.fileMenu.Enable(self.ID_SAVEAS, False)
        

        # Set up edit menu
        self.editMenu = wx.Menu()
        self.editMenu.Append(self.ID_COPY, "&Copy\tCtrl-C", "Copy selection")
        
        # Disable edit menu items that require a selection
        self.editMenu.Enable(self.ID_COPY, False)
        

        # Set up export menu
        self.exportMenu = wx.Menu()
        self.exportMenu.Append(self.ID_EXPORT, "Export results...", "Export results to a tab-delimited file")
        self.exportMenu.Append(self.ID_EXPORTRMATRIX, "Export R-matrix...", "Export relatedness matrix to a tab-delimited file")
        self.exportMenu.Append(self.ID_EXPORTGMATRIX, "Export G-matrix...", "Export group relatedness matrix to a tab-delimited file")
        self.exportMenu.Append(self.ID_EXPORTKINDEMCOM, "Export KINDEMCOM...", "Export data file in KINDEMCOM format")
        
        # Disable export menu items that require an open file and results
        self.exportMenu.Enable(self.ID_EXPORT, False)
        self.exportMenu.Enable(self.ID_EXPORTRMATRIX, False)
        self.exportMenu.Enable(self.ID_EXPORTGMATRIX, False)
        self.exportMenu.Enable(self.ID_EXPORTKINDEMCOM, False)

        
        # Set up Sort menu        
        self.menuBar = wx.MenuBar()
        self.menuBar.Append(self.fileMenu, "&File")
        self.menuBar.Append(self.editMenu, "&Edit")
        self.menuBar.Append(self.exportMenu, "E&xport")
        self.SetMenuBar(self.menuBar)

        # Bind the menu item events to methods
        self.Bind(wx.EVT_MENU, self.OnOpen, id=self.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.onExit, id=self.ID_EXIT)
        

        # Create the notebook
        self.CreateNotebook() 
    
    ################
    # MENU METHODS #
    ################
    def onExit(self, event):
        self.Close(True)

    # Builds global tabs
    def CreateNotebook(self):
        # Create notebook for frame with help panel showing
        self.notebook = Notebook(self, wx.ID_ANY, wx.Point(0, 0), wx.Size(602, 400))
        wx.EVT_NOTEBOOK_PAGE_CHANGED(self, self.notebook.GetId(), self.OnPageChanged)
        self.notebook.AddPage(HelpPanel(self.notebook), "Help")

    # Currently Disconnected
    def ErrorDialog(self, warning, title='Error'):
        dlg = wx.MessageDialog(self, warning, title, wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
    
    # TODO
    # Currently Disconnected
    def OnAbout(self, event):
        splashImage = wx.Image('splash.bmp', wx.BITMAP_TYPE_BMP).ConvertToBitmap()        
        splash = wx.SplashScreen(splashImage, wx.SPLASH_CENTRE_ON_PARENT|wx.SPLASH_NO_TIMEOUT,
          6000, NULL, -1, wx.DefaultPosition, wx.DefaultSize, wx.SIMPLE_BORDER|wx.STAY_ON_TOP)
   
    # TODO
    # Currently Disconnected
    def OnOpen(self, event):
        dlg = wx.FileDialog(self, "Open a tab-delimited data file", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.OpenFile(path)
        dlg.Destroy()
    
    # TODO
    # Currently Disconnected        
    def OpenFile(self, path):
        self.path = path
        self.SetTitle(appTitle + ' ' + __version__ +' '+path)
        with open(path, 'r') as f:
            temp = f.readlines()
        data = []
        sepchar = self.DetermineSepChar(temp)
        for line in temp:
            line = line.strip().split(sepchar)
            data.append([item.strip() for item in line])
        # For now, just print the data to the console
        print(data)

    # TODO
    # Currently Disconnected        
    def DetermineSepChar(self, d):
        sepchars = ['\t', ',', ' ']
        counts = {s: [] for s in sepchars}
        for line in d[:10]:
            for sep in sepchars:
                counts[sep].append(line.count(sep))
        for sep, count_list in counts.items():
            if count_list[0] != 0 and count_list.count(count_list[0]) == len(count_list):
                return sep
        return None  # Default to None if no consistent separator is found
    
    # TODO
    # Currently Disconnected
    def PanelSetup(self, data=[]):
        "Set up notebook tabs."
        self.notebook.Destroy()  # Clear existing panels
        self.CreateNotebook()
        
        self.notebook.AddPage(EditorPanel(self.notebook, data), "Editor")
        # TODO: Add other panels as needed

        self.fileMenu.Enable(self.ID_SAVE, 1)
        self.fileMenu.Enable(self.ID_SAVEAS, 1)
        self.exportMenu.Enable(self.ID_EXPORTKINDEMCOM, 1)
    
    # TODO
    # Event Handler for Changing Tabs
    def OnPageChanged(self, event):
        oldpage = event.GetOldSelection()
        newpage = event.GetSelection()
        if oldpage != -1:
            self.notebook.GetPage(oldpage).OnDeactivate()
        self.notebook.GetPage(newpage).OnActivate()
        self.OpenFile(path)
        app.frame.notebook.Panel('Editor').ToggleHeader()
        app.frame.notebook.Panel('Editor').headerCheckBox.SetValue(1)
        app.frame.notebook.Panel('Editor').EgoColumn.SetSelection(0)
        app.frame.notebook.Panel('Editor').FatherColumn.SetSelection(1)
        app.frame.notebook.Panel('Editor').MotherColumn.SetSelection(2)
        app.frame.notebook.Panel('Editor').SexColumn.SetSelection(3)
        app.frame.notebook.Panel('Editor').LivingColumn.SetSelection(0)

# Notebook Object (Contains Tabs)
class Notebook(wx.Notebook):
    def __init__(self, parent, id, pos, size):
        super(Notebook, self).__init__(parent, id, pos, size)

    def Panel(self, name):
        # Convenient way to refer to tab panel windows by their names (assumes unique names)
        return self.PanelDict()[name]

    def PanelDict(self):
        d = {}  
        for i in range(self.GetPageCount()):
            d[self.GetPageText(i)] = self.GetPage(i)
        return d

    def Destroy(self):
        self.DeleteAllPages()
        super(Notebook, self).Destroy()

# Panel Object (Individual Tab Contents)
class Panel(wx.Panel):
    def __init__(self, parent):
        super(Panel, self).__init__(parent)


    def Clear(self):
        # Clear the panel
        pass

    def OnActivate(self):
        # Stuff to do when panel is selected
        pass

    def OnPanelOpen(self):
        pass

    def OnDeactivate(self):
        # Stuff to do when panel is deselected
        pass

    def OnPanelClose(self):
        pass

    def EnableMenus(self):
        pass

    def Export(self):
        pass

    def ErrorCheck(self):
        pass

    def SetStats(self, stats, title):
        pass

    def Copy(self):
        pass

    def CopyGridCells(self):
        pass

##########
# Panels #
##########

# Help Panel (Startup)
class HelpPanel(Panel):
    def __init__(self, parent):
        super(HelpPanel, self).__init__(parent)
        self.html = html.HtmlWindow(self, -1, pos=(125, 1), size=(470, 373), style=wx.NO_FULL_REPAINT_ON_RESIZE)
        self.html.LoadPage('help/index.html')
        self.choices = ['Splash', 'Introduction', 'Input file format', 'KINDEMCOM files', 'Error checking', 'Relatedness', 'Founders', 'Lineages', 'Counting kin', 'Kin', 'Groups', 'Plotting', 'PCA', 'Sorting', 'License', 'Change log', 'Bugs', 'Contact info', 'Acknowledgements']
        self.helpControl = wx.ListBox(self, 130, pos=(1, 1), size=(123, 373), choices=self.choices, style=wx.LB_NEEDED_SB)
        self.helpControl.Bind(wx.EVT_LISTBOX, self.OnHelpSelect)

    def OnHelpSelect(self, event):
        helpSection = self.choices[event.GetSelection()]
        self.html.LoadPage('help/index.html#' + helpSection)

    def EnableMenus(self):
        try:
            super(HelpPanel, self).EnableMenus()
        except:
            pass

# Builds App and Window
class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None, appTitle)
        frame.Show(True)
        return True

def BuildApp():
    app = MyApp(0) # MyApp(1) redirects errors to program window

    # Sustains Window
    app.MainLoop()
