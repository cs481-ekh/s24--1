import tkinter as tk
from tkinter import ttk

import wx
from wx import *

appTitle = 'Descent 2.0'

class MyFrame(wx.Frame):
    # Runs automatically, initializes application opbject
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, wx.Point(-1,-1), wx.Size(608,465), style = wx.MINIMIZE_BOX|wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX & ~ wx.RESIZE_BORDER)
        
        self.CreateStatusBar()
        self.SetStatusText("")
        self.SetTitle(title)

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
        self.fileMenu.Enable(self.ID_SAVE, 0)
        self.fileMenu.Enable(self.ID_SAVEAS, 0)
        

        # Set up edit menu
        self.editMenu = wx.Menu()
        self.editMenu.Append(self.ID_COPY, "&Copy\tCtrl-C", "Copy selection")
        # self.editMenu.Append(self.ID_PASTE, "&Paste\tCtrl-V", "Paste") # Disabled 'paste' because too much hassle to implement
        
        # Disable edit menu items that require a selection
        self.editMenu.Enable(self.ID_COPY, 0)
        

        # Set up export menu
        self.exportMenu = wx.Menu()
        self.exportMenu.Append(self.ID_EXPORT, "Export results...", "Export results to a tab-delimited file")
        self.exportMenu.Append(self.ID_EXPORTRMATRIX, "Export R-matrix...", "Export relatedness matrix to a tab-delimited file")
        self.exportMenu.Append(self.ID_EXPORTGMATRIX, "Export G-matrix...", "Export group relatedness matrix to a tab-delimited file")
        self.exportMenu.Append(self.ID_EXPORTKINDEMCOM, "Export KINDEMCOM...", "Export data file in KINDEMCOM format")
        # Disable export menu items that require an open file and results
        self.exportMenu.Enable(self.ID_EXPORT, 0)
        self.exportMenu.Enable(self.ID_EXPORTRMATRIX, 0)
        self.exportMenu.Enable(self.ID_EXPORTGMATRIX, 0)
        self.exportMenu.Enable(self.ID_EXPORTKINDEMCOM, 0)

        
        # Set up Sort menu        
        self.menuBar = wx.MenuBar()
        self.menuBar.Append(self.fileMenu, "&File")
        self.menuBar.Append(self.editMenu, "&Edit")
        self.menuBar.Append(self.exportMenu, "E&xport")
        #self.menuBar.Append(self.plotMenu, "&Plot")
        #self.menuBar.Append(self.sortMenu, "S&ort")
        self.SetMenuBar(self.menuBar)

        # TODO: There is something wrong here. The Syntax is old and deprecated!
        # Something like this might work: self.Bind(wx.EVT_MENU, self.OnOpen, self.ID_OPEN)
        """ #wx.EVT_MENU(self, self.ID_ABOUT, self.OnAbout)
        wx.EVT_MENU(self, self.ID_OPEN, self.OnOpen)
        wx.EVT_MENU(self, self.ID_SAVE, self.OnSave)
        wx.EVT_MENU(self, self.ID_SAVEAS, self.OnSaveAs)
        wx.EVT_MENU(self, self.ID_KINDEMCOM, self.OnImport)
        wx.EVT_MENU(self, self.ID_EXPORT, self.OnExport)
        wx.EVT_MENU(self, self.ID_EXPORTRMATRIX, self.OnExportMatrix)
        wx.EVT_MENU(self, self.ID_EXPORTGMATRIX, self.OnExportMatrix)
        wx.EVT_MENU(self, self.ID_EXPORTKINDEMCOM, self.OnExportKINDEMCOM)
        wx.EVT_MENU(self, self.ID_COPY, self.OnCopy)
        wx.EVT_MENU(self, self.ID_EXIT, self.TimeToQuit)
        #wx.EVT_MENU(self, self.ID_SCATTER, self.SetPlot)
        #wx.EVT_MENU(self, self.ID_HIST, self.SetPlot)
        #wx.EVT_MENU(self, self.ID_BOX, self.SetPlot)
        #wx.EVT_MENU(self, self.ID_RELOAD, self.Reload) """
        
        self.CreateNotebook()        
    
    # Builds global tabs
    def CreateNotebook(self):
        # Create notebook for frame with help panel showing
        self.notebook=Notebook(self, -1, wx.Point(0,0), wx.Size(602,400))
        wx.EVT_NOTEBOOK_PAGE_CHANGED(self, self.notebook.GetId(), self.OnPageChanged)
        # self.notebook.AddPage(HelpPanel(self), "Help")

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
        dlg = wx.FileDialog(self)
        dlg.SetStyle(wx.OPEN)
        path=''
        if dlg.ShowModal() == wx.ID_OK: path = dlg.GetPath()
        dlg.Destroy()
        if path != '': self.OpenFile(path)
    
        # TODO
    
        # TODO
    
    # TODO
    # Currently Disconnected        
    def OpenFile(self, path):
        self.path = path
        self.SetTitle(appTitle + ' ' + __version__ +' '+path)
        f=open(path,'r')
        temp=f.readlines()
        f.close()
        data=[]
        sepchar = self.DetermineSepChar(temp)
        for i in range(len(temp)):
            t = temp[i].replace('\n','').split(sepchar) # get rid of the trailing \n, and then split delimited fields into list items
            t = [str(j.strip()) for j in t] # Get rid of leading and trailing spaces, convert to ascii string
            data.append(t)
        self.PanelSetup(data)

    # TODO
    # Currently Disconnected        
    def DetermineSepChar(self, d):
        "Determine the separation character of the data file."
        sepchars = ['\t', ',', ' ']; counts = {}
        for s in sepchars: counts[s] = []
        for i in range(min(10, len(d))):
            for j in sepchars: counts[j].append(d[i].count(j))
        for i in sepchars:
            c = counts[i]
            if c[0] != 0 and c.count(c[0]) == len(c): return i
    
    # TODO
    # Currently Disconnected
    def PanelSetup(self, data=[]):
        "Set up notebook tabs."
        self.ClearPanels()
        self.CreateNotebook()
        self.notebook.InsertPage(0, EditorPanel(self.notebook, data), "Editor")
        self.notebook.InsertPage(1, RelatednessPanel(self.notebook), "Relatedness")
        self.notebook.InsertPage(2, FoundersPanel(self.notebook), "Founders")
        self.notebook.InsertPage(3, LineagePanel(self.notebook), "Lineages")
        self.notebook.InsertPage(4, KinGroupPanel(self.notebook), "Kin counter")
        self.notebook.InsertPage(5, KinPanel(self.notebook), "Kin")
        self.notebook.InsertPage(6, GroupPanel(self.notebook), "Groups")
        #self.notebook.InsertPage(7, Matplotlib(self.notebook), "MatPlot")
        self.notebook.InsertPage(7, PlotPanel(self.notebook), "Plot")
        self.notebook.InsertPage(8, PCAPanel(self.notebook), "PCA")
        self.notebook.SetSelection(0)
        app.frame.notebook.Panel('Editor').SetTable()
        app.frame.notebook.Panel('Editor').header = 0 # Uncheck the headerline box
        app.frame.notebook.Panel('Editor').headerCheckBox.SetValue(0) # Uncheck the headerline box
        self.fileMenu.Enable(self.ID_SAVE, 1)
        self.fileMenu.Enable(self.ID_SAVEAS, 1)
        self.exportMenu.Enable(self.ID_EXPORTKINDEMCOM, 1)
    
    # TODO
    # Currently Disconnected
    def writeTable(self, path, table, header=1):
        f = open(path, 'w')
        if header: # write out the column headings
            for i in range(table.GetNumberCols()): 
                f.write(table.GetColLabelValue(i))
                if i == table.GetNumberCols()-1: f.write('\n')
                else: f.write('\t')            
        for i in range(table.GetNumberRows()): # write out the data
            for j in range(table.GetNumberCols()):
                v = table.GetValue(i,j)
                if type(v) == type(''): f.write(v)
                else: f.write(v)               
                if (j == table.GetNumberCols()-1) and (i != table.GetNumberRows()-1): f.write('\n')
                else: f.write('\t')
        f.close()
    
    # TODO
    # Currently Disconnected    
    def savePath(self):
        dlg = wx.FileDialog(self)
        dlg.SetStyle(wx.SAVE)
        path=''
        if dlg.ShowModal() == wx.ID_OK: path = dlg.GetPath()
        dlg.Destroy()
        return path

    # TODO
    # Currently Disconnected        
    def OnSave(self, event):
        self.writeTable(self.path, self.notebook.Panel('Editor').table, self.notebook.Panel('Editor').header)
    
    # TODO
    # Currently Disconnected
    def OnSaveAs(self, event):
        path = self.savePath()
        if path != '':
            self.path = path
            self.SetTitle(appTitle+': '+self.path)
            self.writeTable(self.path, self.notebook.Panel('Editor').table, self.notebook.Panel('Editor').header)
    
    # TODO
    # Currently Disconnected
    def OnImport(self, event):
        path = self.savePath()
        if path != '':
            self.path=path
            self.SetTitle(appTitle + ' ' + __version__ + ' '+self.path)
            f=open(self.path,'r')
            temp=f.readlines()
            f.close()
            data=[['Ego', 'Father', 'Mother', 'Living', 'Sex', 'Year of birth', 'Population', 'Village', 'Household', 'Birthplace', 'Deathplace', 'Cause of death', 'Year of death', 'Menses', 'Photo ID', 'Abduction', 'Year', 'Month of birth', 'Month of death']]
            for i in temp:
                record = []
                record.append(i[0:15].strip())
                record.append(i[16:31].strip())
                record.append(i[32:47].strip())
                record.append(i[48:49].strip())
                record.append(i[50:51].strip())
                record.append(i[52:56].strip())
                record.append(i[57:58].strip())
                record.append(i[59:62].strip())
                record.append(i[63:66].strip())
                record.append(i[67:70].strip())
                record.append(i[71:74].strip())
                record.append(i[75:77].strip())
                record.append(i[78:82].strip())
                record.append(i[83:86].strip())
                record.append(i[87:90].strip())
                record.append(i[91:94].strip())
                record.append(i[95:99].strip())
                record.append(i[100:101].strip())
                record.append(i[102:103].strip())                
                data.append(record)
            self.PanelSetup(data)
            self.notebook.Panel('Editor').header = 0 # Uncheck the headerline box
            self.notebook.Panel('Editor').headerCheckBox.SetValue(0) # Uncheck the headerline box
            #self.editorPanel.table=Genealogy(self.data, sys.stdout)
            #self.grid = CustTableGrid(self.editorPanel, self.editorPanel.table, loc=[-1,-1], size=[430,345])            
    
    # TODO
    # Currently Disconnected
    def OnExport(self, event):
        page = self.notebook.GetSelection()
        panel = self.notebook.Panel(self.notebook.GetPageText(page))
        panel.Export()
        #path = self.savePath()
        #if path != '':
            #self.writeTable(path, panel.table)

    # TODO
    # Currently Disconnected
    def OnExportKINDEMCOM(self, event):
        # Export data file in KINDEMCOM format.  Only required fields are exported.
        # All other KINDEMCOM fields are filled in with 'missing' codes.
        if not app.frame.notebook.Panel('Editor').ErrorCheck(): return
        path = self.savePath()
        if path != '':
            f = open(path, 'w')
            fieldDef = app.frame.notebook.Panel('Editor').GetFieldDef()
            table = app.frame.notebook.Panel('Editor').table
            tempTable = []
            tempEgo = []
            for i in range(table.GetNumberRows()):
                # Get required fields from data file
                ego = table.GetValue(i, fieldDef['ego'])
                father = table.GetValue(i, fieldDef['father'])
                mother = table.GetValue(i, fieldDef['mother'])
                sex = table.GetValue(i, fieldDef['sex'])
                if not fieldDef['allAlive']: living = table.GetValue(i, fieldDef['living'])
                else: living = fieldDef['alive']
                # Convert missing values to KINDEMCOM missing code '999'
                if father == fieldDef['missing']: father = '999'
                if mother == fieldDef['missing']: mother = '999'
                if living == fieldDef['missing']: living = '3'
                # Convert sex and living codes to KINDEMCOM codes
                if sex == fieldDef['male']: sex = '1'
                elif sex == fieldDef['female']: sex = '2'
                if living == fieldDef['alive']: living = '0'
                elif living == fieldDef['dead']: living = '1'
                tempTable.append([ego, father, mother, sex, living])
                tempEgo.append(ego)
                
            for i in tempTable[:]:
                # KINDEMCOM requires that all fathers and mothers also be listed as egos in the egodata file.
                # Descent adds the fathers and mothers, setting THEIR fathers and mothers to missing.
                if i[1] not in tempEgo:
                    tempTable.append([i[1], '999', '999', '1', '3'])
                    tempEgo.append(i[1])
                if i[2] not in tempEgo:
                    tempTable.append([i[2], '999', '999', '2', '3'])
                    tempEgo.append(i[2])    
            
            output = []        
            for i in tempTable:
                ego, father, mother, sex, living = i[0], i[1], i[2], i[3], i[4]                
                if living == '0': pod, cod, yod = '   0', '  0', '    0'
                else: pod, cod, yod = ' 999', ' 99', ' 9999'
                output.append (ego.ljust(16) + father.ljust(16) + mother.ljust(16) + living + ' ' + sex + ' 9999' + ' 0' + '   0' + '   0' + ' 999' + pod + cod + yod + '   0' + '   0' + '   0' + ' 9999' + ' X' + ' X\n')
            # Kindemcom egodata files must be sorted alphabetically by ego id
            output.sort()
            for i in output: f.write(i)
            f.close()        
    
    # TODO
    # Currently Disconnected
    def OnExportMatrix(self, event):
        menuID = event.GetId()
        if menuID == self.ID_EXPORTRMATRIX:
            Matrix = app.frame.notebook.Panel('Relatedness').R
            IDs = Matrix.dict.keys()
        elif menuID == self.ID_EXPORTGMATRIX:
            Matrix = app.frame.notebook.Panel('Groups').G.gMatrix
            IDs = Matrix.keys()
        path = self.savePath()
        if path != '':
            f=open(path, 'w')            
            IDs.sort()
            for i in IDs: # Write out column headings
                f.write('\t'); f.write(i)
            for i in IDs:
                f.write('\n'); f.write(i) # Write out row labels
                for j in IDs:
                    if j != i:
                        if menuID == self.ID_EXPORTRMATRIX: f.write('\t'); f.write(Matrix.rMatrix(i,j)) # write out ID x ID r-values
                        else: f.write('\t'); f.write(Matrix[i][j])
                    else: f.write('\t'); f.write('1') # write out r-value = 1 for matrix diagonal
        f.close()
    
    # TODO
    # Currently Disconnected
    def OnCopy(self, event):
        "Ask panel to copy whatever should be copied."
        page = self.notebook.GetPageText(self.notebook.GetSelection())
        panel = self.notebook.Panel(page)
        panel.Copy()
    
    # TODO
    # Currently Disconnected
    def SetPlot(self, event):
        "Set the plot type and tell plot panel to do what needs to be done"
        pass
    
    # TODO
    # Currently Disconnected
    def OnPageChanged(self, event):
        oldpage = event.GetOldSelection()
        newpage = event.GetSelection()
        # Tell newly opened panel that it is now open
        if oldpage != -1: self.notebook.GetPage(oldpage).OnDeactivate()
        self.notebook.GetPage(newpage).OnActivate()
    
    # TODO
    # Currently Disconnected
    def TimeToQuit(self, event):
        self.Close(True)
    
    # TODO
    # Currently Disconnected
    def ClearPanels(self):
        self.notebook.Destroy()
        del self.notebook

    # TODO
    # Currently Disconnected    
    def ProgressBar(self, size):
        if not hasattr(self, 'Bar'):
            self.Bar = wx.Gauge(self, -1, size, wx.Point(175, 150), wx.Size(250, 25))
            self.Bar.SetBezelFace(3)
            self.Bar.SetShadowWidth(3)
        else:
            if size%10==0: self.Bar.SetValue(size)
            elif size == -1:
                self.Bar.Destroy()
                del self.Bar
    
    # TODO
    # Currently Disconnected
    def Reload(self, event):
        # A debug function to reload and display HTML help file
        self.notebook.Panel('Help').html.LoadPage('help/index.html')

    # TODO
    # Currently Disconnected
    def timer(self, start, msg=''):
        if start == 1: self.startTime = time.clock()
        else: self.SetStatusText(msg + ': %5.1f seconds' % (time.clock() - self.startTime))
    
    # TODO
    # Currently Disconnected
    def Debug(self, path):
        self.OpenFile(path)
        app.frame.notebook.Panel('Editor').ToggleHeader()
        app.frame.notebook.Panel('Editor').headerCheckBox.SetValue(1)
        app.frame.notebook.Panel('Editor').EgoColumn.SetSelection(0)
        app.frame.notebook.Panel('Editor').FatherColumn.SetSelection(1)
        app.frame.notebook.Panel('Editor').MotherColumn.SetSelection(2)
        app.frame.notebook.Panel('Editor').SexColumn.SetSelection(3)
        app.frame.notebook.Panel('Editor').LivingColumn.SetSelection(0)

# Builds App and Window
class MyApp(wx.App):
    def OnInit(self):
        self.frame = MyFrame(None, -1, appTitle)
        self.frame.Show(True)
        self.SetTopWindow(self.frame)
        return True

def BuildApp():
    app = MyApp(0) # MyApp(1) redirects errors to program window

    # Simple Debugging from V1.0
    try:
        app.frame.Debug(sys.argv[1])
    except:
        pass

    # Sustains Window
    app.MainLoop()
