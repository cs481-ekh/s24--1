#####
#NOTES: PETER BUSCHE
    # 1)Only changed certain functionalities, kept old code nearby if we need to compare
    # 2)Only got GUI working in a very limited fashion, we can add functionalities later
####





import os, sys
import warnings
import wx
import wx.html as html
import time#, random, pydot, re, tempfile

# import Numeric, MLab
import numpy as np
from numpy import cov, mean
from numpy.linalg import svd

from CustomDataTable import *
from Relate import *

from Assets.PyPedal import pyp_newclasses, pyp_metrics

# Global Variables
appTitle = 'Descent'
__version__ = "2.0"
app = None
path = None

class MyFrame(wx.Frame):
    # Runs automatically, initializes application opbject
    def __init__(self, parent, id, title):
        super(MyFrame, self).__init__(parent, title=title, size=(600, 400))

        # Create a status bar
        self.CreateStatusBar()
        self.SetStatusText("Welcome to Descent!")
        self.SetTitle(title + ' ' + __version__)

        # Menu ID numbers
        self.ID_ABOUT = 101
        self.ID_EXIT = 102
        self.ID_OPEN = 103
        self.ID_SAVE = 104
        self.ID_SAVEAS = 106
        self.ID_KINDEMCOM = 107
        self.ID_COPY = 108
        self.ID_PASTE = 109
        self.ID_EXPORT = 110
        self.ID_EXPORTRMATRIX = 111
        self.ID_RELOAD = 112
        self.ID_EXPORTGMATRIX = 113
        self.ID_EXPORTKINDEMCOM = 114

        #===FILE MENU===
        self.fileMenu = wx.Menu()
        self.fileMenu.Append(self.ID_OPEN, "&Open...\tCtrl-O", "Open a tab-delimited data file")
        self.fileMenu.Append(self.ID_SAVE, "&Save\tCtrl-S", "Save the current data file in tab-delimited format")
        self.fileMenu.Append(self.ID_SAVEAS, "Sa&ve as...", "Save the current data in a new file in tab-delimited format")
        self.fileMenu.Append(self.ID_KINDEMCOM, "&Import KINDEMCOM...", "Import KINDEMCOM Ego File")
        self.fileMenu.Append(self.ID_EXIT, "E&xit\tCtrl-Q", "Terminate the program")

        #open file menu
        # Disable file menu items that require an open file
        self.fileMenu.Enable(self.ID_SAVE, False)
        self.fileMenu.Enable(self.ID_SAVEAS, False)

        #===EDIT MENU===
        self.editMenu = wx.Menu()
        self.editMenu.Append(self.ID_COPY, "&Copy\tCtrl-C", "Copy selection")

        #===EXPORT MENU===
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

        #===MENU BAR===
        self.menuBar = wx.MenuBar()
        self.menuBar.Append(self.fileMenu, "&File")
        self.menuBar.Append(self.editMenu, "&Edit")
        self.menuBar.Append(self.exportMenu, "E&xport")
        self.SetMenuBar(self.menuBar)

        # Bind the menu item events to methods
        self.Bind(wx.EVT_MENU, self.OnOpen, id=self.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.OnSave, id=self.ID_SAVE)
        self.Bind(wx.EVT_MENU, self.OnSaveAs, id=self.ID_SAVEAS)
        self.Bind(wx.EVT_MENU, self.OnImport, id=self.ID_KINDEMCOM)
        self.Bind(wx.EVT_MENU, self.OnExport, id=self.ID_EXPORT)
        self.Bind(wx.EVT_MENU, self.OnExportMatrix, id=self.ID_EXPORTRMATRIX)
        self.Bind(wx.EVT_MENU, self.OnExportMatrix, id=self.ID_EXPORTGMATRIX)
        self.Bind(wx.EVT_MENU, self.OnExportKINDEMCOM, id=self.ID_EXPORTKINDEMCOM)
        self.Bind(wx.EVT_MENU, self.OnCopy, id=self.ID_COPY)
        self.Bind(wx.EVT_MENU, self.TimeToQuit, id=self.ID_EXIT)

        # Create the notebook
        self.CreateNotebook()

    # Builds global tabs
    def CreateNotebook(self):
        # Create notebook for frame with help panel showing
        self.notebook = Notebook(self, wx.ID_ANY, wx.Point(0, 0), wx.Size(602, 400))
        #wx.EVT_NOTEBOOK_PAGE_CHANGED(self, self.notebook.GetId(), self.OnPageChanged)
        self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.notebook.AddPage(HelpPanel(self.notebook), "Help")
    
    # done
    def ErrorDialog(self, warning, title='Error'):
        dlg = wx.MessageDialog(self, warning, title, wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    # maybe - remove this? It is never used
    def OnAbout(self, event):
        # splashImage = wx.Image('splash.bmp', wx.BITMAP_TYPE_BMP).ConvertToBitmap()
        # splash = wx.SplashScreen(splashImage, wx.SPLASH_CENTRE_ON_PARENT | wx.SPLASH_NO_TIMEOUT, 6000, None, -1, wx.DefaultPosition, wx.DefaultSize, wx.SIMPLE_BORDER | wx.STAY_ON_TOP)
        pass

    # done
    def OnOpen(self, event):
        dlg = wx.FileDialog(self, "Open a tab-delimited data file", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.OpenFile(path)
        dlg.Destroy()

    # done
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
        self.PanelSetup(data)

    # maybe - could make this more robust to deal with bad data?
    def DetermineSepChar(self, d):
        #=======================OLD===========================
        # "Determine the separation character of the data file."
        # sepchars = ['\t', ',', ' ']; counts = {}
        # for s in sepchars: counts[s] = []
        # for i in range(min(10, len(d))):
        #     for j in sepchars: counts[j].append(d[i].count(j))
        # for i in sepchars:
        #     c = counts[i]
        #     if c[0] != 0 and c.count(c[0]) == len(c): return i
        #======================================================

        sepchars = ['\t', ',', ' ']
        counts = {s: [] for s in sepchars}
        for line in d[:10]:
            for sep in sepchars:
                counts[sep].append(line.count(sep))
        for sep, count_list in counts.items():
            if count_list[0] != 0 and count_list.count(count_list[0]) == len(count_list):
                return sep
        return None  # Default to None if no consistent separator is found

    # maybe - issues with the .SetTable() and .header and .headerCheckbox
        # I am not sure if this is correct since interpreter cannot see these function calls until Editor Panel is created
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

        # app.frame.notebook.Panel('Editor').SetTable()
        # self.notebook.Panel('Editor').header = 0
        # self.notebook.Panel('Editor').headerCheckBox.SetValue(0)
        app.frame.notebook.GetPage(0).SetTable()
        self.notebook.GetPage(0).header = 0
        self.notebook.GetPage(0).headerCheckBox.SetValue(0)

        self.fileMenu.Enable(self.ID_SAVE, 1)
        self.fileMenu.Enable(self.ID_SAVEAS, 1)
        self.exportMenu.Enable(self.ID_EXPORTKINDEMCOM, 1)

    # maybe - same issues as PanelSetup()
    def writeTable(self, path, table, header=1):
        with open(path, 'w') as f:
            if header:  # write out the column headings
                for i in range(table.GetNumberCols()):
                    f.write(table.GetColLabelValue(i))
                    if i == table.GetNumberCols() - 1:
                        f.write('\n')
                    else:
                        f.write('\t')
            for i in range(table.GetNumberRows()):  # write out the data
                for j in range(table.GetNumberCols()):
                    v = table.GetValue(i, j)
                    f.write(str(v))
                    if j == table.GetNumberCols() - 1 and i != table.GetNumberRows() - 1:
                        f.write('\n')
                    else:
                        f.write('\t')

        # def writeTable(self, path, table, header=1):
        #     f = open(path, 'w')
        #     if header: # write out the column headings
        #         for i in range(table.GetNumberCols()): 
        #             f.write(table.GetColLabelValue(i))
        #             if i == table.GetNumberCols()-1: f.write('\n')
        #             else: f.write('\t')            
        #     for i in range(table.GetNumberRows()): # write out the data
        #         for j in range(table.GetNumberCols()):
        #             v = table.GetValue(i,j)
        #             if type(v) == type(''): f.write(v)
        #             else: f.write(repr(v))               
        #             if (j == table.GetNumberCols()-1) and (i != table.GetNumberRows()-1): f.write('\n')
        #             else: f.write('\t')
        #     f.close()

    # maybe - same issues as PanelSetup()
    def savePath(self):
        dlg = wx.FileDialog(self, style=wx.FD_SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            dlg.Destroy()
            return path
        dlg.Destroy()
        return ''


        # def savePath(self):
        #     dlg = wx.FileDialog(self)
        #     dlg.SetStyle(wx.SAVE)
        #     path=''
        #     if dlg.ShowModal() == wx.ID_OK: path = dlg.GetPath()
        #     dlg.Destroy()
        #     return path
        #     # pass

    # maybe - same issues as PanelSetup()
    def OnSave(self, event):
        editor_panel = self.notebook.GetPage(0)
        self.writeTable(self.path, editor_panel.table, editor_panel.header)

        # def OnSave(self, event):
        #     self.writeTable(self.path, self.notebook.Panel('Editor').table, self.notebook.Panel('Editor').header)
        #     # pass

    # maybe - same issues as PanelSetup()
    def OnSaveAs(self, event):
        path = self.savePath()
        if path != '':
            self.path = path
            self.SetTitle(appTitle + ' ' + __version__ + ' ' + self.path)
            editor_panel = self.notebook.GetPage(0)
            self.writeTable(self.path, editor_panel.table, editor_panel.header)

        # def OnSaveAs(self, event):
        #     path = self.savePath()
        #     if path != '':
        #         self.path = path
        #         self.SetTitle(appTitle+': '+self.path)
        #         self.writeTable(self.path, self.notebook.Panel('Editor').table, self.notebook.Panel('Editor').header)
        #     # pass

    # maybe - need to test to see if it works
    def OnImport(self, event):
        path = self.savePath()
        if path != '':
            self.path = path
            self.SetTitle(appTitle + ' ' + __version__ + ' ' + self.path)
            with open(self.path, 'r') as f:
                temp = f.readlines()
            data = [['Ego', 'Father', 'Mother', 'Living', 'Sex', 'Year of birth', 'Population', 'Village', 'Household', 'Birthplace', 'Deathplace', 'Cause of death', 'Year of death', 'Menses', 'Photo ID', 'Abduction', 'Year', 'Month of birth', 'Month of death']]
            for i in temp:
                record = [i[0:15].strip(), i[16:31].strip(), i[32:47].strip(), i[48:49].strip(), i[50:51].strip(), i[52:56].strip(), i[57:58].strip(), i[59:62].strip(), i[63:66].strip(), i[67:70].strip(), i[71:74].strip(), i[75:77].strip(), i[78:82].strip(), i[83:86].strip(), i[87:90].strip(), i[91:94].strip(), i[95:99].strip(), i[100:101].strip(), i[102:103].strip()]
                data.append(record)
            self.PanelSetup(data)
            editor_panel = self.notebook.GetPage(0)
            editor_panel.header = 0  # Uncheck the headerline box
            editor_panel.headerCheckBox.SetValue(0)  # Uncheck the headerline box


        # def OnImport(self, event):
            # path = self.savePath()
            # if path != '':
            #     self.path=path
            #     self.SetTitle(appTitle + ' ' + __version__ + ' '+self.path)
            #     f=open(self.path,'r')
            #     temp=f.readlines()
            #     f.close()
            #     data=[['Ego', 'Father', 'Mother', 'Living', 'Sex', 'Year of birth', 'Population', 'Village', 'Household', 'Birthplace', 'Deathplace', 'Cause of death', 'Year of death', 'Menses', 'Photo ID', 'Abduction', 'Year', 'Month of birth', 'Month of death']]
            #     for i in temp:
            #         record = []
            #         record.append(i[0:15].strip())
            #         record.append(i[16:31].strip())
            #         record.append(i[32:47].strip())
            #         record.append(i[48:49].strip())
            #         record.append(i[50:51].strip())
            #         record.append(i[52:56].strip())
            #         record.append(i[57:58].strip())
            #         record.append(i[59:62].strip())
            #         record.append(i[63:66].strip())
            #         record.append(i[67:70].strip())
            #         record.append(i[71:74].strip())
            #         record.append(i[75:77].strip())
            #         record.append(i[78:82].strip())
            #         record.append(i[83:86].strip())
            #         record.append(i[87:90].strip())
            #         record.append(i[91:94].strip())
            #         record.append(i[95:99].strip())
            #         record.append(i[100:101].strip())
            #         record.append(i[102:103].strip())                
            #         data.append(record)
            #     self.PanelSetup(data)
            #     self.notebook.Panel('Editor').header = 0 # Uncheck the headerline box
            #     self.notebook.Panel('Editor').headerCheckBox.SetValue(0) # Uncheck the headerline box
            #     #self.editorPanel.table=Genealogy(self.data, sys.stdout)
            #     #self.grid = CustTableGrid(self.editorPanel, self.editorPanel.table, loc=[-1,-1], size=[430,345])
            # pass

    # maybe - need to test
    def OnExport(self, event):
        page = self.notebook.GetSelection()
        panel = self.notebook.GetPage(page)
        panel.Export()

        # def OnExport(self, event):
        #     page = self.notebook.GetSelection()
        #     panel = self.notebook.Panel(self.notebook.GetPageText(page))
        #     panel.Export()
        #     #path = self.savePath()
        #     #if path != '':
        #         #self.writeTable(path, panel.table)
        #     # pass

    # maybe - need to test
    def OnExportKINDEMCOM(self, event):
        # Export data file in KINDEMCOM format.  Only required fields are exported.
        # All other KINDEMCOM fields are filled in with 'missing' codes.
        editor_panel = self.notebook.GetPage(0)
        if not editor_panel.ErrorCheck():
            return
        path = self.savePath()
        if path != '':
            with open(path, 'w') as f:
                fieldDef = editor_panel.GetFieldDef()
                table = editor_panel.table
                tempTable = []
                tempEgo = []
                for i in range(table.GetNumberRows()):
                    # Get required fields from data file
                    ego = table.GetValue(i, fieldDef['ego'])
                    father = table.GetValue(i, fieldDef['father'])
                    mother = table.GetValue(i, fieldDef['mother'])
                    sex = table.GetValue(i, fieldDef['sex'])
                    if not fieldDef['allAlive']:
                        living = table.GetValue(i, fieldDef['living'])
                    else:
                        living = fieldDef['alive']
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
                    ego, father, mother, sex, living = i
                    if living == '0':
                        pod, cod, yod = '   0', '  0', '    0'
                    else:
                        pod, cod, yod = ' 999', ' 99', ' 9999'
                    output.append(ego.ljust(16) + father.ljust(16) + mother.ljust(16) + living + ' ' + sex + ' 9999' + ' 0' + '   0' + '   0' + ' 999' + pod + cod + yod + '   0' + '   0' + '   0' + ' 9999' + ' X' + ' X\n')
                # Kindemcom egodata files must be sorted alphabetically by ego id
                output.sort()
                for line in output:
                    f.write(line)

        # def OnExportKINDEMCOM(self, event):
        #     # Export data file in KINDEMCOM format.  Only required fields are exported.
        #     # All other KINDEMCOM fields are filled in with 'missing' codes.
        #     if not app.frame.notebook.Panel('Editor').ErrorCheck(): return
        #     path = self.savePath()
        #     if path != '':
        #         f = open(path, 'w')
        #         fieldDef = app.frame.notebook.Panel('Editor').GetFieldDef()
        #         table = app.frame.notebook.Panel('Editor').table
        #         tempTable = []
        #         tempEgo = []
        #         for i in range(table.GetNumberRows()):
        #             # Get required fields from data file
        #             ego = table.GetValue(i, fieldDef['ego'])
        #             father = table.GetValue(i, fieldDef['father'])
        #             mother = table.GetValue(i, fieldDef['mother'])
        #             sex = table.GetValue(i, fieldDef['sex'])
        #             if not fieldDef['allAlive']: living = table.GetValue(i, fieldDef['living'])
        #             else: living = fieldDef['alive']
        #             # Convert missing values to KINDEMCOM missing code '999'
        #             if father == fieldDef['missing']: father = '999'
        #             if mother == fieldDef['missing']: mother = '999'
        #             if living == fieldDef['missing']: living = '3'
        #             # Convert sex and living codes to KINDEMCOM codes
        #             if sex == fieldDef['male']: sex = '1'
        #             elif sex == fieldDef['female']: sex = '2'
        #             if living == fieldDef['alive']: living = '0'
        #             elif living == fieldDef['dead']: living = '1'
        #             tempTable.append([ego, father, mother, sex, living])
        #             tempEgo.append(ego)
                    
        #         for i in tempTable[:]:
        #             # KINDEMCOM requires that all fathers and mothers also be listed as egos in the egodata file.
        #             # Descent adds the fathers and mothers, setting THEIR fathers and mothers to missing.
        #             if i[1] not in tempEgo:
        #                 tempTable.append([i[1], '999', '999', '1', '3'])
        #                 tempEgo.append(i[1])
        #             if i[2] not in tempEgo:
        #                 tempTable.append([i[2], '999', '999', '2', '3'])
        #                 tempEgo.append(i[2])    
                
        #         output = []        
        #         for i in tempTable:
        #             ego, father, mother, sex, living = i[0], i[1], i[2], i[3], i[4]                
        #             if living == '0': pod, cod, yod = '   0', '  0', '    0'
        #             else: pod, cod, yod = ' 999', ' 99', ' 9999'
        #             output.append (ego.ljust(16) + father.ljust(16) + mother.ljust(16) + living + ' ' + sex + ' 9999' + ' 0' + '   0' + '   0' + ' 999' + pod + cod + yod + '   0' + '   0' + '   0' + ' 9999' + ' X' + ' X\n')
        #         # Kindemcom egodata files must be sorted alphabetically by ego id
        #         output.sort()
        #         for i in output: f.write(i)
        #         f.close()  
            # pass

    # maybe - need to test
    def OnExportMatrix(self, event):
        menuID = event.GetId()
        if menuID == self.ID_EXPORTRMATRIX:
            relatedness_panel = self.notebook.GetPage(1)
            Matrix = relatedness_panel.R
            IDs = list(Matrix.dict.keys())
        elif menuID == self.ID_EXPORTGMATRIX:
            groups_panel = self.notebook.GetPage(6)
            Matrix = groups_panel.G.gMatrix
            IDs = list(Matrix.keys())
        path = self.savePath()
        if path != '':
            with open(path, 'w') as f:
                IDs.sort()
                f.write('\t' + '\t'.join(IDs))  # Write out column headings
                for i in IDs:
                    f.write('\n' + i)  # Write out row labels
                    for j in IDs:
                        if j != i:
                            if menuID == self.ID_EXPORTRMATRIX:
                                f.write('\t' + str(Matrix.rMatrix(i, j)))  # write out ID x ID r-values
                            else:
                                f.write('\t' + str(Matrix[i][j]))
                        else:
                            f.write('\t1')  # write out r-value = 1 for matrix diagonal

        # def OnExportMatrix(self, event):
        #     menuID = event.GetId()
        #     if menuID == self.ID_EXPORTRMATRIX:
        #         Matrix = app.frame.notebook.Panel('Relatedness').R
        #         IDs = list(Matrix.dict.keys())
        #     elif menuID == self.ID_EXPORTGMATRIX:
        #         Matrix = app.frame.notebook.Panel('Groups').G.gMatrix
        #         IDs = list(Matrix.keys())
        #     path = self.savePath()
        #     if path != '':
        #         f=open(path, 'w')            
        #         IDs.sort()
        #         for i in IDs: # Write out column headings
        #             f.write('\t'); f.write(i)
        #         for i in IDs:
        #             f.write('\n'); f.write(i) # Write out row labels
        #             for j in IDs:
        #                 if j != i:
        #                     if menuID == self.ID_EXPORTRMATRIX: f.write('\t'); f.write(repr(Matrix.rMatrix(i,j))) # write out ID x ID r-values
        #                     else: f.write('\t'); f.write(repr(Matrix[i][j]))
        #                 else: f.write('\t'); f.write('1') # write out r-value = 1 for matrix diagonal
        #     f.close()
        #     # pass

    # maybe - need to test
    def OnCopy(self, event):
        "Ask panel to copy whatever should be copied."
        page_index = self.notebook.GetSelection()
        panel = self.notebook.GetPage(page_index)
        panel.Copy()

        # def OnCopy(self, event):
        #     "Ask panel to copy whatever should be copied."
        #     page = self.notebook.GetPageText(self.notebook.GetSelection())
        #     panel = self.notebook.Panel(page)
        #     panel.Copy()
            # pass

    # done - had no functionality in original code
    def SetPlot(self, event):
        "Set the plot type and tell plot panel to do what needs to be done"
        pass

    # maybe- need to test
    def OnPageChanged(self, event):
        oldpage = event.GetOldSelection()
        newpage = event.GetSelection()
        if oldpage != -1:
            self.notebook.GetPage(oldpage).OnDeactivate()
        self.notebook.GetPage(newpage).OnActivate()
        # pass
    
    # done - no changes
    def TimeToQuit(self, event):
        self.Close(True)

    # done - no changes
    def ClearPanels(self):
        self.notebook.Destroy()
        del self.notebook

    # maybe - no changes, need to test
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

    #maybe - need to test
    def Reload(self, event):
        # A debug function to reload and display HTML help file
        for index in range(self.notebook.GetPageCount()):
            if self.notebook.GetPageText(index) == "Help":
                help_panel = self.notebook.GetPage(index)
                help_panel.html.LoadPage('help/index.html')
                break

        # def Reload(self, event):
        #     # A debug function to reload and display HTML help file
        #     self.notebook.Panel('Help').html.LoadPage('help/index.html')

    # done - no changes 
    def timer(self, start, msg=''):
        if start == 1: self.startTime = time.clock()
        else: self.SetStatusText(msg + ': %5.1f seconds' % (time.clock() - self.startTime))

    # maybe - need to test
    def Debug(self, path):
        self.OpenFile(path)
        editor_panel = self.notebook.GetPage(0)
        editor_panel.ToggleHeader()
        editor_panel.headerCheckBox.SetValue(1)
        editor_panel.EgoColumn.SetSelection(0)
        editor_panel.FatherColumn.SetSelection(1)
        editor_panel.MotherColumn.SetSelection(2)
        editor_panel.SexColumn.SetSelection(3)
        editor_panel.LivingColumn.SetSelection(0)


        # def Debug(self, path):
        #     # self.OpenFile(path)
        #     # app.frame.notebook.Panel('Editor').ToggleHeader()
        #     # app.frame.notebook.Panel('Editor').headerCheckBox.SetValue(1)
        #     # app.frame.notebook.Panel('Editor').EgoColumn.SetSelection(0)
        #     # app.frame.notebook.Panel('Editor').FatherColumn.SetSelection(1)
        #     # app.frame.notebook.Panel('Editor').MotherColumn.SetSelection(2)
        #     # app.frame.notebook.Panel('Editor').SexColumn.SetSelection(3)
        #     # app.frame.notebook.Panel('Editor').LivingColumn.SetSelection(0)  
        #     pass

#DONE
class Notebook(wx.Notebook):
    def __init__(self, parent, win, loc, size):
        wx.Notebook.__init__(self, parent, win, loc, size)

    def Panel(self, name):
        # Convenient way to refer to tab panel windows by their names (assumes unique names)
        return self.PanelDict()[name]

    def PanelDict(self):
        d = {}  # {Panel_name:Panel_window, ...}
        for i in range(self.GetPageCount()):
            d[self.GetPageText(i)] = self.GetPage(i)
        return d

    def Destroy(self):
        self.DeleteAllPages()
        # wx.Notebook.Destroy(self)
        super(Notebook, self).Destroy()

class Panel(wx.Panel):
    # maybe - small changes
    def __init__(self, win):
        wx.Panel.__init__(self, win, -1) 
        # self.app = app

    # maybe - no changes
    def Clear(self):
        if hasattr(self, 'grid'):
            self.grid.Destroy()
            del self.grid
        if hasattr(self, 'log'): self.log.Clear()

    # maybe - no changes
    def OnActivate(self):
        "Stuff to do when panel is selected"
        self.OnPanelOpen()
        self.EnableMenus()

    # maybe - no changes
    def OnPanelOpen(self):
        "Placeholder method.  This refers to opening a tab."
        pass

    # maybe - no changes
    def OnDeactivate(self):
        "Stuff to do when panel is deselected"
        self.OnPanelClose()

    # maybe - no changes
    def OnPanelClose(self):
        "Placeholder method.  This refers to closing a tab."
        pass

    # maybe - small changes
    def EnableMenus(self):
        global app
        if hasattr(self, 'grid'):
            app.frame.exportMenu.Enable(self.app.frame.ID_EXPORT, 1)
        else:
            app.frame.exportMenu.Enable(self.app.frame.ID_EXPORT, 0)

    # maybe - no changes
    def Export(self):
        "Default action is to export table; override if necessary."
        path = app.frame.savePath()
        if path != '': app.frame.writeTable(path, self.table) 

    # maybe - no changes
    def ErrorCheck(self):
        app.frame.SetStatusText('')
        app.frame.notebook.Panel('Editor').OnCheckErrorsClick(1, 1) # when calling from other panels, errors only
        if app.frame.notebook.Panel('Editor').errorFlag:            
            app.frame.ErrorDialog('Errors found in dataset.  Check errorlog in Editor tab.')
            return 0
        else: return 1

    # maybe - no changes
    def SetStats(self, stats, title):
        self.log.AppendText('\n\n' + title + ':\n')
        keys = stats['keyOrder']
        for i in keys: self.log.AppendText('\n' + i+': ' + stats[i])
        self.log.AppendText('\n\n')

    # maybe - no changes
    def Copy(self):
        self.CopyGridCells()

    # maybe - need to test
    def CopyGridCells(self):
        if not hasattr(self, 'grid') or not self.grid.IsSelection():
            return  # No grid or nothing is selected

        selected_rows = self.grid.GetSelectedRows()
        selected_cols = self.grid.GetSelectedCols()
        selection_block = self.grid.GetSelectionBlockTopLeft()

        if selected_rows:
            topLeft = (selected_rows[0], 0)
            bottomRight = (selected_rows[-1], self.grid.GetNumberCols() - 1)
        elif selected_cols:
            topLeft = (0, selected_cols[0])
            bottomRight = (self.grid.GetNumberRows() - 1, selected_cols[-1])
        elif selection_block:
            topLeft = selection_block[0]
            bottomRight = self.grid.GetSelectionBlockBottomRight()[0]
        else:
            return  # No valid selection

        text_lines = []
        for x in range(topLeft[0], bottomRight[0] + 1):
            line = []
            for y in range(topLeft[1], bottomRight[1] + 1):
                value = self.table.GetValue(x, y)
                line.append(value if isinstance(value, str) else repr(value))
            text_lines.append('\t'.join(line))

        text = '\n'.join(text_lines)

        do = wx.TextDataObject()
        do.SetText(text)
        wx.TheClipboard.Open()
        wx.TheClipboard.SetData(do)
        wx.TheClipboard.Close()

        # def CopyGridCells(self):
        #     # Copy selected block of grid cells.  Selected single cells are copied using some other, unknown routine.
        #     if not hasattr(self, 'grid'): return # No data to select from
        #     if not self.grid.IsSelection(): return # Nothing is selected
        #     if self.grid.GetSelectedRows() != []:
        #         # One or more entire rows is selected
        #         topLeft = [(self.grid.GetSelectedRows()[0], 0)]
        #         bottomRight = [(self.grid.GetSelectedRows()[-1], self.grid.GetNumberCols()-1)]
        #     elif self.grid.GetSelectedCols() != []:
        #         # One or more entire columns is selected
        #         topLeft = [(0, self.grid.GetSelectedCols()[0])]
        #         bottomRight = [(self.grid.GetNumberRows()-1, self.grid.GetSelectedCols()[-1])]
        #     else:
        #         # A selected block of cells that aren't a row or column
        #         topLeft = self.grid.GetSelectionBlockTopLeft()
        #         bottomRight = self.grid.GetSelectionBlockBottomRight()            
        #     # Convert selected table cells to tab-delimited, line-feed delimited text block
        #     text = ''
        #     for x in range(topLeft[0][0], bottomRight[0][0]+1): # For some reason, top left is returned as a list of a tuple
        #         for y in range(topLeft[0][1], bottomRight[0][1]+1):
        #             value = self.table.GetValue(x, y)
        #             # This is so strings don't have quotes
        #             if type(value) == type(''): text = text + self.table.GetValue(x, y) 
        #             else: text = text + repr(self.table.GetValue(x, y))
        #             if y != (bottomRight[0][1]):  text = text + '\t'
        #         if x != (bottomRight[0][0]): text = text + '\n'        
        #     do = wx.TextDataObject()
        #     do.SetText(text)
        #     wx.TheClipboard.Open()
        #     wx.TheClipboard.SetData(do)
        #     wx.TheClipboard.Close()

class EditorPanel(Panel):
    def __init__(self, win, data, header=0):

        # NEW
        Panel.__init__(self, win)
        self.data = data
        self.header = header
        self.errorFlag = 1
        # Initialize other attributes and controls for the Editor panel
        self.log = wx.TextCtrl(self, -1, "", pos=(440, 0), size=(153, 290), style=wx.TE_MULTILINE | wx.TE_RICH | wx.TE_READONLY)
        self.errorButton = wx.Button(self, -1, "Error check", pos=(440, 294))
        self.errorButton.Bind(wx.EVT_BUTTON, self.OnCheckErrorsClick)
        self.IncestCheckBox = wx.CheckBox(self, -1, "Incest", pos=(535, 296), size=(190, 20), style=wx.NO_BORDER)
        self.headerCheckBox = wx.CheckBox(self, -1, "Row one contains column headings", pos=(3, 305), size=(190, 20), style=wx.NO_BORDER)
        self.headerCheckBox.Bind(wx.EVT_CHECKBOX, self.EvtHeaderCheckBox)

        self.SetTable()

        # OLD
        wx.StaticText(self, -1, "Ego:", wx.Point(3, 329), wx.Size(25, 20))
        self.EgoColumn = wx.Choice(self, 20, (30, 327), wx.Size(75,20), choices = self.table.colLabels)        
        wx.StaticText(self, -1, "Father:", wx.Point(110, 329), wx.Size(30, 20))
        self.FatherColumn = wx.Choice(self, 25, (150, 327), wx.Size(75,20), choices = self.table.colLabels)        
        wx.StaticText(self, -1, "Sex:", wx.Point(3, 354), wx.Size(25, 20))
        self.SexColumn = wx.Choice(self, 30, (30, 352), wx.Size(75,20), choices = self.table.colLabels)        
        wx.StaticText(self, -1, "Mother:", wx.Point(110, 354), wx.Size(34, 20))
        self.MotherColumn = wx.Choice(self, 35, (150, 352), wx.Size(75,20), choices = self.table.colLabels)
        wx.StaticText(self, -1, "Living:", wx.Point(231, 329), wx.Size(30, 20))
        self.LivingColumn = wx.Choice(self, 36, (265, 327), wx.Size(75, 20), choices = self.table.colLabels)

        # NEW
        # wx.StaticText(self, -1, "Ego:", pos=(3, 329))
        # self.EgoColumn = wx.Choice(self, -1, pos=(30, 327), size=(75, 20), choices=self.data.colLabels)
        # wx.StaticText(self, -1, "Father:", pos=(110, 329))
        # self.FatherColumn = wx.Choice(self, -1, pos=(150, 327), size=(75, 20), choices=self.data.colLabels)
        # wx.StaticText(self, -1, "Sex:", pos=(3, 354))
        # self.SexColumn = wx.Choice(self, -1, pos=(30, 352), size=(75, 20), choices=self.data.colLabels)
        # wx.StaticText(self, -1, "Mother:", pos=(110, 354))
        # self.MotherColumn = wx.Choice(self, -1, pos=(150, 352), size=(75, 20), choices=self.data.colLabels)
        # wx.StaticText(self, -1, "Living:", pos=(231, 329))
        # self.LivingColumn = wx.Choice(self, -1, pos=(265, 327), size=(75, 20), choices=self.data.colLabels)


        self.SetColumnChoices()

        # OLD
        wx.StaticText(self, -1, "Male:", wx.Point(350, 329), wx.Size(30, 20))
        self.male = wx.TextCtrl(self, 40, "m", wx.Point(390, 327), size=(50, -1))
        wx.StaticText(self, -1, "Female:", wx.Point(350, 354), wx.Size(34, 20))
        self.female = wx.TextCtrl(self, 45, "f", wx.Point(390, 352), size=(50, -1))
        wx.StaticText(self, -1, "Alive:", wx.Point(444, 329), wx.Size(30, 20))
        self.alive = wx.TextCtrl(self, 55, "1", wx.Point(475, 327), wx.Size(50, 20))
        wx.StaticText(self, -1, "Dead:", wx.Point(444, 354), wx.Size(30, 20))
        self.dead = wx.TextCtrl(self, 60, "0", wx.Point(475, 352), wx.Size(50, 20))
        wx.StaticText(self, -1, "Missing", wx.Point(545, 351), wx.Size(50, 20))
        self.missing = wx.TextCtrl(self, 50, "999", wx.Point(540, 327), size=(50, -1))

        # NEW
        # wx.StaticText(self, -1, "Male:", pos=(350, 329))
        # self.male = wx.TextCtrl(self, -1, "m", pos=(390, 327), size=(50, -1))
        # wx.StaticText(self, -1, "Female:", pos=(350, 354))
        # self.female = wx.TextCtrl(self, -1, "f", pos=(390, 352), size=(50, -1))
        # wx.StaticText(self, -1, "Alive:", pos=(444, 329))
        # self.alive = wx.TextCtrl(self, -1, "1", pos=(475, 327), size=(50, 20))
        # wx.StaticText(self, -1, "Dead:", pos=(444, 354))
        # self.dead = wx.TextCtrl(self, -1, "0", pos=(475, 352), size=(50, 20))
        # wx.StaticText(self, -1, "Missing", pos=(545, 351))
        # self.missing = wx.TextCtrl(self, -1, "999", pos=(540, 327), size=(50, -1))

        # NEW
        self.male.Bind(wx.EVT_TEXT, self.EvtTextChange)
        self.female.Bind(wx.EVT_TEXT, self.EvtTextChange)
        self.alive.Bind(wx.EVT_TEXT, self.EvtTextChange)
        self.dead.Bind(wx.EVT_TEXT, self.EvtTextChange)
        self.missing.Bind(wx.EVT_TEXT, self.EvtTextChange)
        # pass

    def EnableMenus(self):
        "Disable Export menu in Editor tab because it is not needed here."
        app.frame.exportMenu.Enable(app.frame.ID_EXPORT, 0)
        # pass

    def SetTable(self):
        self.Clear()
        self.table = Genealogy(self.data, sys.stdout, self.header)
        self.grid = CustTableGrid(self, self.table, pos=(0, 0), size=(430, 304))
        if hasattr(self, 'EgoColumn'):
            self.SetColumnChoices()
        # pass

    def SetColumnList(self): # Delete??
        columnList = []
        for i in range(self.table.GetNumberCols()): columnList.append(self.table.GetColLabelValue(i))
        return columnList
        # pass

    def EvtHeaderCheckBox(self, event):
        self.ToggleHeader()
        # pass

    def ToggleHeader(self):
        self.header = not self.header
        self.SetTable()
        # pass

    def SetColumnChoices(self):
        "Set Column Choices"
        self.EgoColumn.Clear()
        for i in self.table.colLabels: self.EgoColumn.Append(i)
        self.FatherColumn.Clear()
        for i in self.table.colLabels: self.FatherColumn.Append(i)
        self.MotherColumn.Clear()
        for i in self.table.colLabels: self.MotherColumn.Append(i)
        self.SexColumn.Clear()
        for i in self.table.colLabels: self.SexColumn.Append(i)
        self.LivingColumn.Clear()
        self.LivingColumn.Append('All living')
        for i in self.table.colLabels: self.LivingColumn.Append(i)
        # Moved group column stuff to group panel
        #self.GroupColumn.Clear()
        #for i in self.table.colLabels: self.GroupColumn.Append(i)
        # pass

    def EvtTextChange(self, event): 
        self.grid.dirty = True
        # pass

    def GetFieldDef(self):
        # This queries the user settings for the locations of the ego, father, mother, and sex fields
        # as well as the codes for male, female, and missing
        fieldDef = {}
        fieldDef['male'] = str(self.male.GetValue())
        fieldDef['female'] = str(self.female.GetValue())
        fieldDef['missing'] = str(self.missing.GetValue())
        fieldDef['alive'] = str(self.alive.GetValue())
        fieldDef['dead'] = str(self.dead.GetValue())
        fieldDef['ego'] = self.EgoColumn.GetSelection()
        fieldDef['father'] = self.FatherColumn.GetSelection()
        fieldDef['mother'] = self.MotherColumn.GetSelection()
        fieldDef['sex'] = self.SexColumn.GetSelection()
        fieldDef['living'] = self.LivingColumn.GetSelection() - 1 # Need to subtract 1 because 'All living' has been prepended
        fieldDef['allAlive'] = (self.LivingColumn.GetStringSelection() == 'All living')
        #fieldDef['group'] = self.GroupColumn.GetSelection()  # Moved group column stuff to group panel
        if fieldDef['male'] == '' or fieldDef['female'] == '' or fieldDef['missing'] == '':
            self.errorFlag = 1
        if fieldDef['ego'] == -1 or fieldDef['father'] == -1 or fieldDef['mother'] == -1 or fieldDef['sex'] == -1:
            self.errorFlag = 1        
        if not fieldDef['allAlive']:
            if fieldDef['alive'] == '' or fieldDef['dead'] == '' or fieldDef['living'] == -1:
                self.errorFlag = 1
        return fieldDef
        # pass

    def PyPedalSetUp(self):
        "Create PyPedal pedigree."
        self.pedigree = GenealogyFLO(self.table, app)
        # pass

    def OnCheckErrorsClick(self, event, errorsOnly = 0):
        "Checks for errors in the genealogy file."
        wx.BeginBusyCursor()
        app.frame.timer(1)
        self.log.Clear()
        f = self.GetFieldDef()
        if f['male'] == '' or f['female'] == '' or f['ego'] == -1 or f['father'] == -1 or f['mother'] == -1 or f['sex'] == -1 or f['living'] == -2:
            # If these errors are found, don't bother looking for other errors.
            self.log.AppendText('Errors:\n')
            self.errorFlag = 1
            self.log.AppendText('\nOne or more required columns or values has not been specified below.')
            wx.EndBusyCursor()
            return
        self.table.fieldDef = f
                
        tempErrorlog=self.table.CheckUniqueID()
        temp = self.table.CheckSex(errorsOnly)
        incest = []
        if self.IncestCheckBox.GetValue() and not errorsOnly: incest = self.table.CheckIncest(app)
        tempErrorlog.extend(temp[0])
        if tempErrorlog != []:
            self.log.AppendText('Errors:\n\n')
            for i in tempErrorlog: self.log.AppendText(i)
            self.errorFlag = 1
        else:
            self.errorFlag = 0
            self.log.AppendText('No errors found.')
        self.log.AppendText('\n')
        
        if not errorsOnly and not self.errorFlag:
            self.SetStats(self.table.PopulationStats(), 'Population stats')
        
        if not errorsOnly:
            self.log.AppendText('Warnings:\n\n')
            if temp[1] != []:
                for i in temp[1]: self.log.AppendText(i)
            elif incest != []:
                for i in incest: self.log.AppendText(i)
            else: self.log.AppendText('No warnings.')
                        
        if not self.errorFlag and errorsOnly and self.grid.dirty:
            self.grid.dirty = False
            self.PyPedalSetUp()
        self.log.ShowPosition(1)
        app.frame.timer(0, 'Error checking')
        wx.EndBusyCursor()
        # pass

class RelatednessPanel(Panel):
    def __init__(self, win):
        Panel.__init__(self, win)
        # self.relateButton = wx.Button(self, 21, "Compute Relatedness Stats", wx.Point(225,350))
        # self.log = wx.TextCtrl(self, -1, "", pos=(440,0), size=(153, 340), style=wx.TE_MULTILINE|wx.TE_RICH|wx.TE_READONLY)
        # wx.EVT_BUTTON(self, 21, self.OnComputeFgALL)
        # self.stats = {'keyOrder':['Average [nonzero] coefficient of relationship', '\nAverage [nonzero] coefficient of inbreeding']}
        pass


    def EnableMenus(self):
        # Panel.EnableMenus(self)
        # #super(RelatednessPanel, self).EnableMenus()
        # if hasattr(self, 'grid'): app.frame.exportMenu.Enable(app.frame.ID_EXPORTRMATRIX, 1)
        pass
        
    def OnComputeFgALL(self, event):
        # if self.ErrorCheck():
        #     wx.BeginBusyCursor()    
        #     self.Clear()
        #     app.frame.timer(1)
        #     self.R=rMatrix(app.frame.notebook.Panel('Editor').table.data, app)
        #     self.R.fieldDef = app.frame.notebook.Panel('Editor').GetFieldDef()
        #     self.R.relatedness()
        #     self.table = CustomDataTable(self.R.FgALL(), sys.stdout)            
        #     app.frame.timer(0, 'Relatedness')
        #     self.table.Sort(0)
        #     self.grid = CustTableGrid(self, self.table, loc=[0, 0], size=[430,340])
        #     self.grid.EnableEditing(False) # Disable editing of results
        #     self.EnableMenus() # Enable relevant menus for this panel now that we have results
        #     self.stats['\nAverage [nonzero] coefficient of inbreeding'] = repr(self.R.f_avg)
        #     self.stats['Average [nonzero] coefficient of relationship'] = repr(self.R.r_avg)
        #     self.SetStats(self.stats, 'Relatedness & Inbreeding')
        #     wx.EndBusyCursor()
        pass

class FoundersPanel(Panel):
    def __init__(self, win):
        Panel.__init__(self, win)
        # self.lineageButton = wx.Button(self, 70, "Find population founders", wx.Point(225,350))
        # wx.EVT_BUTTON(self, 70, self.OnFindFounders)
        # self.countCheckBox = wx.CheckBox(self, -1, "List ID's", wx.Point(425, 351), wx.Size(60, 20), wx.NO_BORDER)
        # self.log = wx.TextCtrl(self, -1, "", pos=(440,0), size=(153, 340), style=wx.TE_MULTILINE|wx.TE_RICH|wx.TE_READONLY)
        # self.stats = {'keyOrder':['Number of founders', '\nMaximum number of descendants', '\nMaximum number of living descendants', '\nAverage number of descendants', '\nAverage number of living descendants']}
        pass

    def OnFindFounders(self, event):
        # if self.ErrorCheck():
        #     wx.BeginBusyCursor()
        #     self.Clear()
        #     app.frame.timer(1)
        #     R=rMatrix(app.frame.notebook.Panel('Editor').table.data, app)
        #     R.fieldDef = app.frame.notebook.Panel('Editor').GetFieldDef()
        #     self.table = CustomDataTable(R.findFounders((not self.countCheckBox.IsChecked())), sys.stdout)
        #     self.table.Sort(0)
        #     self.grid = CustTableGrid(self, self.table, loc=[0, 0], size=[430,340])
        #     self.grid.SetColSize(1, 100)
        #     self.grid.SetColSize(2, 120)
        #     #self.grid.SetColSize(3, 130)
        #     #self.grid.SetColSize(4, 140)
        #     app.frame.timer(0, 'Founders')
        #     self.grid.EnableEditing(False) # Disable editing of results
        #     self.EnableMenus() # Enable relevant menus for this panel now that we have results
        #     if not self.countCheckBox.IsChecked():
        #         descendants = [i[1] for i in self.table]
        #         living = [i[2] for i in self.table]
        #         self.stats['Number of founders'] = repr(len(descendants))
        #         self.stats['\nMaximum number of descendants'] = repr(max(descendants))
        #         self.stats['\nMaximum number of living descendants'] = repr(max(living))
        #         self.stats['\nAverage number of descendants'] = repr(float(sum(descendants)/len(descendants)))
        #         self.stats['\nAverage number of living descendants'] = repr(float(sum(living)/len(living)))
        #         self.SetStats(self.stats, 'Summary founder stats')
        #     wx.EndBusyCursor()
        pass

class LineagePanel(Panel):
    def __init__(self, win):
        Panel.__init__(self, win)
        # self.lineageButton = wx.Button(self, 60, "Compute Lineages", wx.Point(245,350))
        # wx.EVT_BUTTON(self, 60, self.OnComputeLineages)
        # self.log = wx.TextCtrl(self, -1, "", pos=(440,0), size=(153, 340), style=wx.TE_MULTILINE|wx.TE_RICH|wx.TE_READONLY)
        pass

    def OnComputeLineages(self, event):
        # if self.ErrorCheck():
        #     wx.BeginBusyCursor()
        #     self.Clear()
        #     app.frame.timer(1)
        #     L=Lineages(app.frame.notebook.Panel('Editor').table.data, app)
        #     self.table = CustomDataTable(L.computeLineages(), sys.stdout)
        #     self.table.Sort(0)
        #     self.grid = CustTableGrid(self, self.table, loc=[0, 0], size=[430,340])
        #     self.grid.SetColSize(2, 100)
        #     self.grid.SetColSize(4, 100)
        #     app.frame.timer(0, 'Lineages')
        #     self.grid.EnableEditing(False) # Disable editing of results
        #     self.EnableMenus() # Enable relevant menus for this panel now that we have results
        #     self.SetStats(L.patStats, 'Patrilineage stats')
        #     self.SetStats(L.matStats, 'Matrilineage stats')
        #     wx.EndBusyCursor()
        pass

class KinPanel(Panel):
    def __init__(self, win):
        Panel.__init__(self, win)
        # self.EgoChoice = wx.Choice(self, -1, (10, 5), wx.Size(120, 10), choices = [])
        # self.EgoLabel = wx.StaticText(self, -1, "Ego", wx.Point(10, 27), wx.Size(50, 15))
        # self.KinButton = wx.Button(self, 220, "Compute Kin", wx.Point(10, 45))
        # wx.EVT_BUTTON(self, 220, self.OnComputeKin)
        # # Check box to omit non-kin from being displayed
        # self.kinOnlyCheckBox = wx.CheckBox(self, -1, "Omit non-kin", wx.Point(10, 70), wx.Size(90, 20), wx.NO_BORDER)        
        # self.kinOnlyCheckBox.SetValue(True)
        # # Check box to generate pedigree chart
        # self.pedigreeCheckBox = wx.CheckBox(self, -1, "Kinship diagram", wx.Point(10, 90), wx.Size(110, 20), wx.NO_BORDER)        
        # self.PathChoice = wx.Choice(self, -1, (10, 115), wx.Size(110, 20), choices = ['All', '1', '2', '3', '4'])
        # self.PathChoice.SetSelection(2)
        # self.PathLabel = wx.StaticText(self, -1, "Max genealogical distance", wx.Point(10, 140), wx.Size(128, 20))
        pass

class KinGroupPanel(Panel):
    def __init__(self, win):
        Panel.__init__(self, win)
        # self.kinGroupButton = wx.Button(self, 410, "Count kin-group members", wx.Point(407,350))
        # wx.EVT_BUTTON(self, 410, self.countKin)
        # #self.countCheckBox = wx.CheckBox(self, 420, "List ID's", wx.Point(525, 351), wx.Size(60, 20), wx.NO_BORDER)
        # #wx.EVT_CHECKBOX(self, 420, self.EvtCountCheckBox)
        # self.count = 1
        # self.choice=[]
        # self.kinGroups=['', 'fathers', 'mothers', 'parents', 'sons', 'daughters', 'offspring', 'full brothers', 'full sisters', 'full siblings', 'grandparents','grandchildren','halfbrothers','halfsisters', 'halfsiblings', 'full cousins', 'mates', 'stepsons', 'stepdaughters', 'stepchildren', 'stepbrothers', 'stepsisters', 'stepsiblings']
        # for i in range(3):
        #     for j in range(2):
        #         temp=[]
        #         for k in range(4):
        #             temp.append(wx.Choice(self, 40+i*8+j*4+k, (370+j*130, 5+(i*120)+(k*25)), choices = self.kinGroups))
        #         self.choice.append(temp)
        pass


    def EvtCountCheckBox(self, event):
        # self.count = not self.count
        pass
    
    def countKin(self, event):
        # self.functionsList=[]
        # for i in range(6):
        #     if self.choice[i][0].GetSelection() < 1: continue
        #     temp=[]
        #     for j in range(4):
        #         if self.choice[i][j].GetSelection() > 0: temp.append(self.choice[i][j].GetStringSelection())
        #         else:break
        #     self.functionsList.append(temp)
        
        # if self.ErrorCheck():
        #     wx.BeginBusyCursor()
        #     self.Clear()
        #     app.frame.timer(1)
        #     self.KinGroups=KinGroups(app.frame.notebook.Panel('Editor').table.data, app)
        #     self.KinGroups.fieldDef = app.frame.notebook.Panel('Editor').GetFieldDef()
        #     self.table = CustomDataTable(self.KinGroups.kinCount(self.count, self.functionsList), sys.stdout)
        #     self.table.Sort(0)
        #     self.grid = CustTableGrid(self, self.table, loc=[-1,-1], size=[365,341])
        #     self.grid.SetColLabelAlignment(wx.ALIGN_LEFT, wx.ALIGN_CENTRE)
        #     app.frame.timer(0, 'Kin count')
        #     self.grid.EnableEditing(False) # Disable editing of results
        #     self.EnableMenus() # Enable relevant menus for this panel now that we have results
        #     wx.EndBusyCursor()
        pass

class GroupPanel(Panel):
    def __init__(self, win):
        Panel.__init__(self, win)
        # self.GroupChoice = wx.Choice(self, -1, (10, 25), wx.Size(120, 20), [])
        # self.GroupLabel = wx.StaticText(self, -1, "Group column", wx.Point(10, 50), wx.Size(75, 20))
        # self.groupButton = wx.Button(self, 70, "Compute group relatedness stats", wx.Point(10, 75))
        # wx.EVT_BUTTON(self, 70, self.OnComputeGroupStats)
        pass

    def OnPanelOpen(self):
        # selection = self.GroupChoice.GetSelection()
        # text = self.GroupChoice.GetString(selection)
        # self.GroupChoice.Clear()
        # # need to reset GroupChoice in case stuff has been changed, but try to set it back where it was if possible
        # self.GroupChoice.Append('Patrilineage')
        # self.GroupChoice.Append('Matrilineage')
        # for i in app.frame.notebook.Panel('Editor').table.colLabels: self.GroupChoice.Append(i)
        # if text == self.GroupChoice.GetString(selection): self.GroupChoice.SetSelection(selection)
        pass


    def EnableMenus(self):
        # Panel.EnableMenus(self)
        # if hasattr(self, 'grid'): app.frame.exportMenu.Enable(app.frame.ID_EXPORTGMATRIX, 1)
        pass


    def OnComputeGroupStats(self, event):
        # groupColumn = self.GroupChoice.GetSelection()
        # if not hasattr(app.frame.notebook.Panel('Relatedness'), 'R'):
        #     app.frame.ErrorDialog('R-values must first be computed in Relatedness tab.')
        # elif groupColumn == -1:
        #     app.frame.ErrorDialog('First select the group column from the popup menu.')
        # elif self.ErrorCheck():
        #     wx.BeginBusyCursor()
        #     self.Clear()
        #     app.frame.timer(1)
        #     self.G = Groups(app.frame.notebook.Panel('Relatedness').R.rMatrix, app.frame.notebook.Panel('Editor').table.data, groupColumn, app)
        #     self.G.relatedness()
        #     self.table = CustomDataTable(self.G.stats(), sys.stdout)
        #     self.table.Sort(0)
        #     self.grid = CustTableGrid(self, self.table, loc=[195, 0], size=[400, 373])
        #     self.grid.SetColSize(2, 120)
        #     app.frame.timer(0, 'Groups')
        #     self.grid.EnableEditing(False) # Disable editing of results
        #     self.EnableMenus() # Enable relevant menus for this panel now that we have results
        #     wx.EndBusyCursor()
        pass

class PlotPanelBase(Panel):
    def __init__(self, win):
        Panel.__init__(self, win)
        # #self.Plot = PlotCanvas(self, -1, wx.Point(0,35), wx.Size(475,340))
        # self.Color = ChoiceMenu(self, 130, wx.Point(480, 9), wx.Size(114, 20), [])
        # self.colorPanel = scrolled.ScrolledPanel(self, -1, wx.Point(480,35), wx.Size(114,339), style = wx.SUNKEN_BORDER)
        # self.labelBox = wx.CheckBox(self, -1, "Labels", wx.Point(420, 0o5))
        # self.jitterBox = wx.CheckBox(self, -1, "Jitter", wx.Point(420, 20))
        # self.colors = ['BLUE', 'RED', 'AQUAMARINE', 'BLUE VIOLET', 'BROWN', 'CADET BLUE', 'CORAL', 'CORNFLOWER BLUE', 'CYAN', 'DARK GREY', 'DARK GREEN', 'DARK OLIVE GREEN', 'DARK ORCHID', 'DARK SLATE BLUE', 'DARK SLATE GREY DARK TURQUOISE', 'DIM GREY', 'FIREBRICK', 'FOREST GREEN', 'GOLD', 'GOLDENROD', 'GREY', 'GREEN', 'GREEN YELLOW', 'INDIAN RED', 'KHAKI', 'LIGHT BLUE', 'LIGHT GREY', 'LIGHT STEEL BLUE', 'LIME GREEN', 'MAGENTA', 'MAROON', 'MEDIUM AQUAMARINE', 'MEDIUM BLUE', 'MEDIUM FOREST GREEN', 'MEDIUM GOLDENROD', 'MEDIUM ORCHID', 'MEDIUM SEA GREEN', 'MEDIUM SLATE BLUE', 'MEDIUM SPRING GREEN', 'MEDIUM TURQUOISE', 'MEDIUM VIOLET RED', 'MIDNIGHT BLUE', 'NAVY', 'ORANGE', 'ORANGE RED', 'ORCHID', 'PALE GREEN', 'PINK', 'PLUM', 'PURPLE', 'SALMON', 'SEA GREEN', 'SIENNA', 'SKY BLUE', 'SLATE BLUE', 'SPRING GREEN', 'STEEL BLUE', 'TAN', 'THISTLE', 'TURQUOISE', 'VIOLET', 'VIOLET RED', 'WHEAT', 'YELLOW', 'YELLOW GREEN']
        # self.colorIndex = 0
        pass
            
    def OnPanelOpen(self):
        # """Reset color menu in case column labels have changed, but try and set things back to the way
        # they were if possible."""
        # selection = self.Color.GetSelection()
        # text = self.Color.GetString(selection)
        # self.Color.Clear()
        # newChoices = ['Colorize by: None', 'Patrilineage', 'Matrilineage']
        # for i in app.frame.notebook.Panel('Editor').table.colLabels: newChoices.append(i)
        # self.Color.Reset(newChoices)
        # if text != '' and text == self.Color.GetString(selection): self.Color.SetSelection(selection)
        pass

    def EnableMenus(self):
        # app.frame.exportMenu.Enable(app.frame.ID_EXPORT, 1)
        pass

    def Copy(self):
        # "Override grid copy in order to copy plot bitmap."
        # bmpdo = wx.BitmapDataObject(self.Plot._Buffer)
        # wx.TheClipboard.Open()
        # wx.TheClipboard.SetData(bmpdo)
        # wx.TheClipboard.Close()
        pass

    def Export(self):
        # self.Plot.SaveFile()
        pass

    def Indices(self):
        # "Figures out which egos belong to which groups, and assigns each group a random color."
        # groupColumn = self.Color.GetSelection()
        # if groupColumn > 2:
        #     # Fields in original file
        #     fieldDef = app.frame.notebook.Panel('Editor').GetFieldDef()
        #     egoColumn = fieldDef['ego']
        #     if groupColumn > 2: groupColumn -= 3
        #     table = app.frame.notebook.Panel('Editor').table            
        # elif groupColumn > 0:
        #     # Patrilineage or Matrilineage
        #     L = app.frame.notebook.Panel('Lineages')
        #     if not hasattr(L, 'table'): L.OnComputeLineages(0)
        #     if groupColumn == 2: groupColumn = 4
        #     table = L.table
        #     egoColumn = 0
        # else:
        #     # No group
        #     groupColumn = -1
        #     fieldDef = app.frame.notebook.Panel('Editor').GetFieldDef()
        #     egoColumn = fieldDef['ego']
        #     table = app.frame.notebook.Panel('Editor').table
        # table.Sort(egoColumn) # Make sure egos are in sort order
        # data = table.data
        # self.IDS = [i[egoColumn] for i in data]
        # # Create a dictionary of egos' group ID's
        # self.egoDict = {} 
        # for i in data:
        #     if groupColumn == -1: self.egoDict[i[egoColumn]] = 'All'
        #     elif i[groupColumn] == '': self.egoDict[i[egoColumn]] = fieldDef['missing']
        #     else: self.egoDict[i[egoColumn]] = str(i[groupColumn])
        # # Create list of group IDs registered to ID list
        # # If colorize == None, then create one group ('All')
        # if groupColumn == -1:
        #     self.groupIDS = len(self.IDS) * ['All']
        #     self.groupDict = {'All':self.IDS}
        #     self.colorDict = {'All':'black'} # color for group 'All' = black
        #     self.clearColorPanel()
        #     return
        # else:
        #     self.groupIDS = [self.egoDict[i] for i in self.IDS]
        # # Create a dictionary of groups of egos
        # self.groupDict = {}
        # for i in data:
        #     groupID = i[groupColumn]
        #     if groupID == '': groupID = fieldDef['missing']
        #     if groupID not in self.groupDict: self.groupDict[groupID] = [i[egoColumn]]
        #     else: self.groupDict[groupID] += [i[egoColumn]]
        # self.colorDict = {}
        # #random.seed(0)
        # for i in self.groupDict: self.colorDict[i] = self.RandomColor() #( random.randint(0,255), random.randint(0,255), random.randint(0,255) )
        # self.createColorPanel() # set up legend        
        pass

    def RandomColor(self):
        # "Returns a random wx color, without replacement."
        # self.colorIndex += 1
        # return self.colors[self.colorIndex % len(self.colors)]
        pass

    def ScatterPlot(self, data, ColumnNames, mask = 0, labels=''):
        # "Scatterplot of x,y data."
        # if type(data) == type([]):
        #     xydata = Numeric.array(data[0:2])
        #     xydata = Numeric.swapaxes(xydata, 0, 1)
        # else: xydata = data
        # xydata = compress(equal(mask, 1), xydata, 0)
        # if self.jitterBox.IsChecked(): dataJ = self.jitter(xydata, 0.01)
        # else: dataJ = xydata
        # self.Indices() # Color groups
        # groups = list(self.groupDict.keys()); groups.sort()
        # markers = []
        # gids = array(self.groupIDS, PyObject) # Need to use PyObject type for character strings
        # if labels == '': rids = array(self.IDS, PyObject)
        # else: rids = array(labels, PyObject)
        # # Strip out elements for which there are missing data
        # # mask is an array where 0 = missing data, 1 = nonmissing data
        # gids = compress(equal(mask, 1), gids, 0)
        # rids = compress(equal(mask, 1), rids, 0)
        # for i in groups:
        #     groupPlotData = compress(equal(gids, i), dataJ, 0)
        #     groupIDS = compress(equal(gids, i), rids, 0)
        #     markers += [wxPyPlot.PolyMarker(groupPlotData, colour = self.colorDict[i])] #wx.Colour(red=self.colorDict[i][0], green=self.colorDict[i][1], blue=self.colorDict[i][2]) )]
        #     if self.labelBox.IsChecked(): markers += [wxPyPlot.PolyLabel(groupPlotData, groupIDS)]
        # graphics = wxPyPlot.PlotGraphics(markers, '', ColumnNames[0], ColumnNames[1])
        # self.Plot.SetEnableZoom(True)
        # self.Plot.SetXSpec('auto')
        # self.Plot.Draw(graphics)
        # # Compute and display regression coefficient
        # try:
        #     reg = MLab.corrcoef(xydata)[0][1]
        #     if reg < 0: r = repr(round(reg, 2))[0:5]
        #     else: r = repr(round(reg, 2))[0:4]
        # except:
        #     r = 'na'
        # if hasattr(self, 'r'): self.r.SetLabel('r = ' + r) # Hack!!!
        pass
        
    def Barplot(self, data, barlabel, mask):
        # "Barplot of data in categories."
        # self.Indices()
        # groups = list(self.groupDict.keys()); groups.sort()
        # gids = array(self.groupIDS, PyObject) # Need to use PyObject type for character strings
        # rids = array(self.IDS, PyObject)
        # # Strip out elements for which there are missing data
        # # mask is an array where 0 = missing data, 1 = nonmissing data
        # data = compress(equal(mask, 1), data, 0)
        # gids = compress(equal(mask, 1), gids, 0)
        # rids = compress(equal(mask, 1), rids, 0)
        # means = []; columnLabels = []; columnColors = []
        # for i in groups:
        #     groupPlotData = compress(equal(gids, i), data, 0)
        #     groupIDS = compress(equal(gids, i), rids, 0)
        #     means += [Numeric.average(groupPlotData)]
        #     columnLabels += [str(i)]
        #     columnColors += [self.colorDict[str(i)]]
        # points = [ [(i,0), (i, m)] for i, m in enumerate(means)]
        # lines = [wxPyPlot.PolyLine(p, colour = columnColors[i], legend=columnLabels[i], width=35) for i, p in enumerate(points)]
        # graphics = wxPyPlot.PlotGraphics(lines, '', xLabel=self.Color.GetStringSelection(), yLabel='Mean '+barlabel)
        # self.Plot.SetEnableZoom(False)
        # #self.Plot.SetEnableLegend(True)
        # self.Plot.SetXSpec('none')
        # self.Plot.Draw(graphics, xAxis = (-len(lines)/10, len(lines)+len(lines)/10))
        # self.r.SetLabel(' ')
        pass
    
    def Histogram(self, data, xLabel='Histogram', yLabel='Count', mask=0, bins=10):
        # "Plot a histogram of data."
        # #print 'len(data), len(mask), data, mask', len(data), len(mask), data, mask
        # data = compress(equal(mask, 1), data, 0) # Get rid of missing values
        # ymin, ymax = min(data), max(data)
        # dy = float(ymax-ymin)/(bins-1)
        # bins = [ymin + dy*i for i in range(bins)]
        # y = Numeric.array(data)
        # n = Numeric.searchsorted(sort(y), bins)
        # n = MLab.diff(MLab.concatenate([n, [len(y)]]))        
        # points = [ [(b,0), (b, n[i])] for i, b in enumerate(bins)]
        # lines = [wxPyPlot.PolyLine(p, width=35) for p in points]
        # graphics = wxPyPlot.PlotGraphics(lines, '', xLabel, yLabel)
        # self.Plot.SetEnableZoom(False)
        # self.Plot.SetXSpec('auto')
        # self.Plot.Draw(graphics, xAxis = (ymin-dy,ymax+dy))
        # self.r.SetLabel(' ')
        pass
        
    def jitter(self, data, percent):
        # "perturb +- %"
        # n = data.shape[0]
        # dim = data.shape[1]
        # mi = MLab.min(data)
        # ma = MLab.max(data)
        # st = percent*2*(ma-mi)
        # dataJ = data.copy()
        # for i in range(n):
        #     for j in range(dim):
        #         dataJ[i][j] += st[j]*(random.random()-0.5)
        # return dataJ
        pass
        
    def createColorPanel(self):
        # "The legend of colors for groups."
        # self.clearColorPanel()
        # fgs = wx.FlexGridSizer(cols=2, vgap=4, hgap=4) # Sizer to hold color buttons and labels
        # colors = list(self.colorDict.keys()); colors.sort()
        # for i in colors:
        #     color = self.colorDict[i]
        #     b = wx.Button(self.colorPanel, -1, '', size=wx.Size(15,15))
        #     b.SetBackgroundColour(self.colorDict[i]) #(red=color[0], green=color[1], blue=color[2]))
        #     label = wx.StaticText(self.colorPanel, -1, i)
        #     self.colorPanelObjects += [b]
        #     self.colorPanelObjects += [label]
        #     fgs.Add(b, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        #     fgs.Add(label, flag=wx.EXPAND|wx.RIGHT, border=25)
        # self.colorPanel.SetSizer(fgs)
        # self.colorPanel.SetAutoLayout(1)
        # self.colorPanel.SetupScrolling(scroll_x=False)
        pass

    def clearColorPanel(self):
        # if hasattr(self, 'colorPanelObjects'): # First delete previous panel objects if they exist
        #     for i in self.colorPanelObjects: i.Destroy()
        # self.colorPanelObjects = []
        pass

class PlotPanel(PlotPanelBase):
    def __init__(self, win):
        PlotPanelBase.__init__(self, win)
        # self.Plot = wxPyPlot.PlotCanvas(self, -1, wx.Point(0,35), wx.Size(475,340))
        # self.XLabel = wx.StaticText(self, -1, "X: ", wx.Point(5, 12), wx.Size(15, 20))
        # self.XChoice = ChoiceMenu(self, -1, wx.Point(20, 10), wx.Size(80, 20), [])
        # self.YLabel = wx.StaticText(self, -1, "Y: ", wx.Point(110, 12), wx.Size(15, 20))
        # self.YChoice = ChoiceMenu(self, -1, wx.Point(125, 10), wx.Size(80, 20), [])
        # #self.ZLabel = wx.StaticText(self, -1, "Z: ", wx.Point(215, 12), wx.Size(15, 20))
        # #self.ZChoice = ChoiceMenu(self, -1, wx.Point(230, 10), wx.Size(80, 20), [])
        # self.plotButton = wx.Button(self, 80, "Plot", wx.Point(250, 9))
        # wx.EVT_BUTTON(self, 80, self.OnPlot)
        # self.r = wx.StaticText(self, -1, "", wx.Point(340, 13), wx.Size(15, 20))
        pass
        
    def EnableMenus(self):
        # "Enable Plot menu."
        # pass #app.frame.menuBar.EnableTop(3, 1)
        pass

    def OnPanelOpen(self):
        # PlotPanelBase.OnPanelOpen(self)
        # # find all variables that can be plotted
        # wx.BeginBusyCursor()
        
        # if not hasattr(self, 'editorVariables'):
        #     # Get variables from the main data.  Because this is slow, only do it if it hasn't already been done.
        #     if self.ErrorCheck():
        #         self.editorVariables = {} # {Variable:[table, column], ...}
        #         columnNum = app.frame.notebook.Panel('Editor').table.GetNumberCols()
        #         rowNum = app.frame.notebook.Panel('Editor').table.GetNumberRows()
        #         fieldDef = app.frame.notebook.Panel('Editor').GetFieldDef()
        #         ignoreFields = [fieldDef['ego'], fieldDef['father'], fieldDef['mother']]
        #         for i in range(columnNum):
        #             if i in ignoreFields: continue
        #             allNumbers = True
        #             for j in range(rowNum):
        #                 try:
        #                     float(app.frame.notebook.Panel('Editor').table.data[j][i])
        #                 except:
        #                     # let blank cells count as missing numeric value
        #                     chr = app.frame.notebook.Panel('Editor').table.data[j][i].strip()
        #                     if chr != '' and chr != fieldDef['missing']:
        #                         allNumbers =  False
        #                         break                   
        #             if allNumbers:
        #                 variableName = app.frame.notebook.Panel('Editor').table.GetColLabelValue(i)
        #                 self.editorVariables[variableName] = [app.frame.notebook.Panel('Editor').table, i]
        #     else:
        #         wx.EndBusyCursor()
        #         return
        
        # self.variables = self.editorVariables.copy()
        
        # if hasattr(app.frame.notebook.Panel('Relatedness'), 'grid'):
        #     self.variables['FgALL'] = [app.frame.notebook.Panel('Relatedness').table, 1]
        #     self.variables['FgCON'] = [app.frame.notebook.Panel('Relatedness').table, 2]
        #     self.variables['No. relatives'] = [app.frame.notebook.Panel('Relatedness').table, 3]
        #     self.variables['Inbreeding'] = [app.frame.notebook.Panel('Relatedness').table, 4]
        # if hasattr(app.frame.notebook.Panel('Lineages'), 'grid'):
        #     self.variables['Patrilineage size'] = [app.frame.notebook.Panel('Lineages').table, 3]
        #     self.variables['Matrilineage size'] = [app.frame.notebook.Panel('Lineages').table, 6]
        # if hasattr(app.frame.notebook.Panel('Kin counter'), 'grid'):
        #     columnNum = app.frame.notebook.Panel('Kin counter').table.GetNumberCols()
        #     for i in range(1, columnNum):
        #         variableName = app.frame.notebook.Panel('Kin counter').table.GetColLabelValue(i)
        #         if variableName.count('Count'): self.variables[variableName] = [app.frame.notebook.Panel('Kin counter').table, i]
        # v=[""]; v += list(self.variables.keys()); v.sort()
        # selections = self.XChoice.GetStringSelection(), self.YChoice.GetStringSelection() #, self.ZChoice.GetStringSelection()
        # self.XChoice.Reset(v); self.YChoice.Reset(v) #; self.ZChoice.Reset(v)
        # # Try and set selections to what was selected before
        # self.XChoice.SetStringSelection(selections[0])
        # self.YChoice.SetStringSelection(selections[1])
        # #self.ZChoice.SetStringSelection(selections[2])
        # wx.EndBusyCursor()
        pass
        
    def OnPlot(self, event):
        # n = app.frame.notebook.Panel('Editor').table.GetNumberRows()
        # selections = []; Data = []; ColumnNames = []; mask = [1 for i in range(n)]
        # selections += [self.XChoice.GetStringSelection()]
        # selections += [self.YChoice.GetStringSelection()]
        # #selections += [self.ZChoice.GetStringSelection()]
        # fieldDef = app.frame.notebook.Panel('Editor').GetFieldDef()
        # self.colorIndex = 0
        # for v in selections:
        #     if v != '':
        #         handle = self.variables[v]
        #         # Sort on ego column
        #         if handle[0] == app.frame.notebook.Panel('Editor').table: handle[0].Sort(fieldDef['ego']) 
        #         else: handle[0].Sort(0) # in all other tables, ego is column 0 
        #         variable = []; ColumnNames += [v]
        #         for i in range(n):
        #             if handle[0].data[i][handle[1]] == fieldDef['missing']:
        #                 mask[i] = 0
        #                 variable += [-999]
        #                 continue
        #             try:
        #                 variable += [ float(handle[0].data[i][handle[1]]) ]
        #             except: # strip out non-numeric 'missing' values
        #                 mask[i] = 0
        #                 variable += [-999]
        #                 continue
        #         Data.append(variable)
        
        # # Function dispatch for plot type selection in menu
        # if len(Data) == 1 and self.Color.GetSelection() == 0: self.Histogram(Data[0], xLabel = ColumnNames[0], mask=mask)
        # elif len(Data) == 1 and self.Color.GetSelection() != 0: self.Barplot(Data[0], barlabel = ColumnNames[0], mask = mask)
        # elif len(Data) > 1: self.ScatterPlot(Data, ColumnNames, mask)
        pass


    def OnPlotOLD(self, event):
        # n = app.frame.notebook.Panel('Editor').table.GetNumberRows()
        # x = self.XChoice.GetStringSelection()
        # y = self.YChoice.GetStringSelection()
        # fieldDef = app.frame.notebook.Panel('Editor').GetFieldDef()
        # if x == '' or y == '': return
        # x2 = self.variables[x]; y2 = self.variables[y]
        # # Sort on ego column
        # if x2[0] == app.frame.notebook.Panel('Editor').table: x2[0].Sort(fieldDef['ego']) 
        # else: x2[0].Sort(0) # in all other tables, ego is column 0 
        # if y2[0] == app.frame.notebook.Panel('Editor').table: y2[0].Sort(fieldDef['ego'])
        # else: y2[0].Sort(0) # in all other tables, ego is column 0 
        # array = []; mask = []
        # for i in range(n):
        #     if x2[0].data[i][x2[1]] == fieldDef['missing'] or y2[0].data[i][y2[1]] == fieldDef['missing']:
        #         mask += [0]
        #         continue
        #     try:
        #         #array += [ [ float(x2[0].data[i][x2[1]]), float(y2[0].data[i][y2[1]]) ] ]
        #         array += [ float(x2[0].data[i][x2[1]]) ]
        #         mask += [1]
        #     except: # strip out non-numeric 'missing' values
        #         mask += [0]
        #         continue
        # #a = Numeric.array(array)
        # try:
        #     reg = MLab.corrcoef(a)[0][1]
        #     if reg < 0: r = repr(round(reg, 2))[0:5]
        #     else: r = repr(round(reg, 2))[0:4]
        # except:
        #     r = 'na'
        # self.r.SetLabel('r = ' + r)
        # #self.ScatterPlot(a, x, y, mask)
        # self.Histogram(array)
        pass

class Matplotlib(PlotPanelBase):
    # "Using matplotlib as the plotting library."
    def __init__(self, win):
        PlotPanelBase.__init__(self, win)
        # self.XLabel = wx.StaticText(self, -1, "X: ", wx.Point(5, 12), wx.Size(15, 20))
        # self.XChoice = ChoiceMenu(self, -1, wx.Point(20, 10), wx.Size(80, 20), [])
        # self.YLabel = wx.StaticText(self, -1, "Y: ", wx.Point(110, 12), wx.Size(15, 20))
        # self.YChoice = ChoiceMenu(self, -1, wx.Point(125, 10), wx.Size(80, 20), [])
        # self.ZLabel = wx.StaticText(self, -1, "Z: ", wx.Point(215, 12), wx.Size(15, 20))
        # self.ZChoice = ChoiceMenu(self, -1, wx.Point(230, 10), wx.Size(80, 20), [])
        # self.plotButton = wx.Button(self, 80, "Plot", wx.Point(330, 9))
        # wx.EVT_BUTTON(self, 80, self.OnPlot)
        # #self.r = wx.StaticText(self, -1, "", wx.Point(430, 13), wx.Size(15, 20))
        # self.createPlot()
        pass

    def OnPanelOpen(self):
        # PlotPanelBase.OnPanelOpen(self)
        # # find all variables that can be plotted
        # wx.BeginBusyCursor()
        
        # if not hasattr(self, 'editorVariables'):
        #     # Get variables from the main data.  Because this is slow, only do it if it hasn't already been done.
        #     if self.ErrorCheck():
        #         self.editorVariables = {} # {Variable:[table, column], ...}
        #         columnNum = app.frame.notebook.Panel('Editor').table.GetNumberCols()
        #         rowNum = app.frame.notebook.Panel('Editor').table.GetNumberRows()
        #         fieldDef = app.frame.notebook.Panel('Editor').GetFieldDef()
        #         ignoreFields = [fieldDef['ego'], fieldDef['father'], fieldDef['mother']]
        #         for i in range(columnNum):
        #             if i in ignoreFields: continue
        #             allNumbers = True
        #             for j in range(rowNum):
        #                 try:
        #                     int(app.frame.notebook.Panel('Editor').table.data[j][i])
        #                 except:
        #                     # let blank cells count as missing numeric value
        #                     if app.frame.notebook.Panel('Editor').table.data[j][i].strip() != '':
        #                         allNumbers =  False
        #                         break
        #             if allNumbers:
        #                 variableName = app.frame.notebook.Panel('Editor').table.GetColLabelValue(i)
        #                 self.editorVariables[variableName] = [app.frame.notebook.Panel('Editor').table, i]
        #     else:
        #         wx.EndBusyCursor()
        #         return
        
        # self.variables = self.editorVariables.copy()
        
        # if hasattr(app.frame.notebook.Panel('Relatedness'), 'grid'):
        #     self.variables['FgALL'] = [app.frame.notebook.Panel('Relatedness').table, 1]
        #     self.variables['FgCON'] = [app.frame.notebook.Panel('Relatedness').table, 2]
        #     self.variables['No. relatives'] = [app.frame.notebook.Panel('Relatedness').table, 3]
        #     self.variables['Inbreeding'] = [app.frame.notebook.Panel('Relatedness').table, 4]
        #     #self.variables['PP-FgALL'] = [app.frame.notebook.Panel('Relatedness').table, 5]
        #     #self.variables['PP-FgCON'] = [app.frame.notebook.Panel('Relatedness').table, 6]
        # if hasattr(app.frame.notebook.Panel('Lineages'), 'grid'):
        #     self.variables['Patrilineage size'] = [app.frame.notebook.Panel('Lineages').table, 3]
        #     self.variables['Matrilineage size'] = [app.frame.notebook.Panel('Lineages').table, 6]
        # if hasattr(app.frame.notebook.Panel('Kin counter'), 'grid'):
        #     columnNum = app.frame.notebook.Panel('Kin counter').table.GetNumberCols()
        #     for i in range(1, columnNum):
        #         variableName = app.frame.notebook.Panel('Kin counter').table.GetColLabelValue(i)
        #         if variableName.count('Count'): self.variables[variableName] = [app.frame.notebook.Panel('Kin counter').table, i]
        # v=[""]; v += list(self.variables.keys()); v.sort()
        # selections = self.XChoice.GetStringSelection(), self.YChoice.GetStringSelection(), self.ZChoice.GetStringSelection()
        # self.XChoice.Reset(v); self.YChoice.Reset(v); self.ZChoice.Reset(v)
        # # Try and set selections to what was selected before
        # self.XChoice.SetStringSelection(selections[0])
        # self.YChoice.SetStringSelection(selections[1])
        # self.ZChoice.SetStringSelection(selections[2])
        # wx.EndBusyCursor()
        pass
            
    def OnPanelClose(self):
        # "Disable Plot menu."
        # app.frame.menuBar.EnableTop(3, 0)
        pass
        
    def EnableMenus(self):
        # "Enable Plot menu."
        # app.frame.menuBar.EnableTop(3, 1)
        pass
            
    def Copy(self):
        # "Override grid copy in order to copy plot bitmap."
        # bmpdo = wx.BitmapDataObject(self.Plot._Buffer)
        # wx.TheClipboard.Open()
        # wx.TheClipboard.SetData(bmpdo)
        # wx.TheClipboard.Close()
        pass
        
    def Export(self):
        # self.Plot.SaveFile()
        pass
        
    def jitter(self, data, percent):
        # "perturb +- %"
        # n  = len(data)
        # mi = min(data)
        # ma = max(data)
        # st = percent*2*(ma-mi)
        # dataJ = data[:]
        # for i in range(n): dataJ[i] += st*(random.random()-0.5)
        # return dataJ
        pass
    
    def createPlot(self):
        # "Setup up a matplotlib plot that is ready to plot data"
        # ## A workaround to get matplotlib to play nice with my other controls
        # self.mplPanel = wx.Panel(self, -1, pos=wx.Point(0,35), size=wx.Size(475,340))
        # ######## matplotlib code ##############
        # self.mplPanel.fig = Figure()
        # self.canvas = FigureCanvasWx(self.mplPanel, -1, self.mplPanel.fig)
        # self.canvas.SetClientRect(wx.Rect(0,35,475,340))        
        # #self.p = self.mplPanel.fig.add_subplot(111)
        # # Add an axes at left, bottom, width, height
        # self.p = self.mplPanel.fig.add_axes([0.15,0.15,0.75,0.75])
        # ######## End of matplotlib code ###########
        pass

    def OnPlot(self, event):
        # n = app.frame.notebook.Panel('Editor').table.GetNumberRows()
        # selections = []; Data = []; ColumnNames = []
        # selections += [self.XChoice.GetStringSelection()]
        # selections += [self.YChoice.GetStringSelection()]
        # selections += [self.ZChoice.GetStringSelection()]
        # fieldDef = app.frame.notebook.Panel('Editor').GetFieldDef()
        # for v in selections:
        #     if v != '':
        #         handle = self.variables[v]
        #         # Sort on ego column
        #         if handle[0] == app.frame.notebook.Panel('Editor').table: handle[0].Sort(fieldDef['ego']) 
        #         else: handle[0].Sort(0) # in all other tables, ego is column 0 
        #         variable = []; ColumnNames += [v]
        #         for i in range(n):
        #             try:
        #                 variable += [ float(handle[0].data[i][handle[1]]) ]
        #             except: # strip out non-numeric 'missing' values
        #                 continue
        #         Data.append(variable)
        
        # self.p.clear() # matplotlib code to clear plot figure
        # # Function dispatch for plot type selection in menu
        # if app.frame.plotMenu.IsChecked(app.frame.ID_SCATTER): self.ScatterPlot(Data, ColumnNames)
        # if app.frame.plotMenu.IsChecked(app.frame.ID_HIST): self.Histogram(Data, ColumnNames)
        # if app.frame.plotMenu.IsChecked(app.frame.ID_BOX):            
        #     array = Numeric.array(Data)
        #     array = Numeric.swapaxes(array, (0, 1))
        #     self.BoxPlot(array, ColumnNames)
        pass
        
    def ScatterPlot(self, Data, ColumnNames):
        # if len(Data) < 2: return
        # s = 20
        # X = Data[0]
        # Y = Data[1]
        # m, b = polyfit(X, Y, 1)
        # x = [min(X), max(X)]
        # y = [m*x[0]+b, m*x[1]+b]
        # if len(Data) == 3:
        #     Z = Data[2]
        #     minZ = min(Z)
        #     d = max(Z) - minZ
        #     if d!= 0: s = [100*(float(i-minZ)/d)+20 for i in Z]
        # if self.jitterBox.IsChecked():
        #     X = self.jitter(X, 0.01)
        #     Y = self.jitter(Y, 0.01)
        # self.p.scatter(X, Y, s, alpha=0.75)
        # self.p.plot(x, y, '-k', linewidth=2)
        # self.p.set_xlabel(ColumnNames[0], size="small")
        # self.p.set_ylabel(ColumnNames[1], size="small")
        # self.canvas.draw()
        pass
        
    def Histogram(self, Data, ColumnNames):
        # if len(Data) < 1: return  
        # self.p.hist(Data[0])
        # self.p.set_xlabel(ColumnNames[0], size="small")
        # self.canvas.draw()
        pass
        
    def BoxPlot(self, Data, ColumnNames):        
        # return # Weird bug in boxplot...
        # if len(Data) < 1: return
        # self.p.boxplot(Data, notch=1)
        # self.canvas.draw()
        pass

class PCAPanel(PlotPanelBase):
    def __init__(self, win):
        PlotPanelBase.__init__(self, win)
        # self.Plot = wxPyPlot.PlotCanvas(self, -1, wx.Point(0,35), wx.Size(475,340))
        # self.Plot2D = wx.Button(self, 90, "2D Plot", wx.Point(190, 9))
        # wx.EVT_BUTTON(self, 90, self.On2D)
        # self.Plot3D = wx.Button(self, 100, "3D Plot", wx.Point(270, 9))
        # wx.EVT_BUTTON(self, 100, self.On3D)
        # self.Choice = wx.Choice(self, 120, (1, 9), wx.Size(105, 20), ['PCA', 'MDS (Torgerson)'])
        # self.Choice.SetSelection(0) # initialize to PCA
        # wx.EVT_CHOICE(self, 120, self.OnChoice)
        # self.ScreeButton = wx.Button(self, 130, "Scree plot", wx.Point(110, 9))
        # wx.EVT_BUTTON(self, 130, self.Scree)
        # #self.stereoBox = wx.CheckBox(self, 105, "Stereo", wx.Point(355, 13))
        pass
    
    def OnChoice(self, event):
        # selection = self.Choice.GetStringSelection()
        # if selection == 'PCA':
        #     self.ScreeButton = wx.Button(self, 130, "Scree plot", wx.Point(110, 9))
        #     wx.EVT_BUTTON(self, 130, self.Scree)            
        # elif hasattr(self, 'ScreeButton'):
        #     self.ScreeButton.Destroy()
        #     del(self.ScreeButton)
        pass
    
    def functionDispatch(self, dim):
        # if not self.ErrorCheck(): return 0
        # if not hasattr(app.frame.notebook.Panel('Relatedness'), 'R'):
        #     app.frame.ErrorDialog('R-values must first be computed in Relatedness tab.')
        #     return 0
        # else: self.rArray = app.frame.notebook.Panel('Relatedness').R
        # selection = self.Choice.GetStringSelection()
        # app.frame.timer(1)
        # if selection == 'MDS (Torgerson)':
        #     self.rArray.MDS(dim)
        #     self.PlotData = self.rArray.mds.X
        #     stressString = ' (Initial avg. stress: ' + repr(round(self.rArray.stress1)) + '; final avg. stress: ' + repr(round(self.rArray.stress2)) + ') '
        #     app.frame.timer(0, 'Torgerson MDS' + stressString)
        # elif selection == 'PCA':
        #     self.rArray.PCA()
        #     self.PlotData = self.rArray.PCAPlot(dim)
        #     app.frame.timer(0, 'PCA')
        # return 1
        pass
    
    def Scree(self, event):
        # # Scree plot
        # wx.BeginBusyCursor()
        # if not hasattr(app.frame.notebook.Panel('Relatedness'), 'R'):
        #     app.frame.ErrorDialog('R-values must first be computed in Relatedness tab.')
        #     wx.EndBusyCursor()
        #     return
        # else: self.rArray = app.frame.notebook.Panel('Relatedness').R
        # self.rArray.PCA()
        # scree = []; labels = []
        # for i in range(10): scree += [[i, self.rArray.evals[i]]]
        # for i in range(10): labels += [repr(self.rArray.evals[i])]
        # scree = Numeric.array(scree)
        # markers = wxPyPlot.PolyMarker(scree)
        # labels = wxPyPlot.PolyLabel(scree, labels)
        # graphics = wxPyPlot.PlotGraphics([markers, labels], 'Scree Plot', 'Eigenvalue', '')
        # self.Plot.SetEnableZoom(True)
        # self.Plot.Draw(graphics)
        # wx.EndBusyCursor()
        pass
            
    def PreFlight(self):        
        # self.colorIndex = 0
        # self.ColourDatabase = wx.ColourDatabase()
        # n = max(Numeric.shape(self.PlotData))
        # self.mask = []; self.labels = []
        # for row in range(n):
        #     name = self.rArray.PyPedalPedigree.pedigree.pedigree[row].name
        #     if name in list(self.rArray.dict.keys()):
        #         self.mask += [1]
        #         self.labels += [name]
        #     else: self.mask += [0]
        # data = compress(equal(self.mask, 1), self.PlotData, 0)
        # mask = max(Numeric.shape(data))*[1]
        # return (data, mask)
        pass
    
    def On2D(self, event):
        # wx.BeginBusyCursor()
        # if not self.functionDispatch(2):
        #     wx.EndBusyCursor()
        #     return
        # # Here was have to get only data with ID's who are egos # This is a hack; Scatterplot needs a mask list, so here it is.
        # data, mask = self.PreFlight()
        # self.ScatterPlot(data, ['1','2'], mask, labels = self.labels)
        # wx.EndBusyCursor()
        pass
        
    def On3D(self, event):
        # wx.BeginBusyCursor()
        # if not self.functionDispatch(3):
        #     wx.EndBusyCursor()
        #     return
        # data, mask = self.PreFlight()
        # if self.jitterBox.IsChecked(): dataJ = self.jitter(data, 0.02)
        # else: dataJ = data
        # self.Indices()
        # if len(list(self.colorDict.keys())) == 1: self.colorDict[list(self.colorDict.keys())[0]] = 'RED'
        # #import visual
        # if not hasattr(self, 'scene') or self.scene.visible == 0:
        #     self.scene = visual.display(title='Kinship space', width=600, height=400, center=(0,0,0), background=(0,0,0))
        #     self.scene.select()
        #     self.scene.exit = 0
        #     #if self.stereoBox.IsChecked(): self.scene.stereo = 'redblue'
        #     #else: self.scene.stereo = 'nostereo'
        # else:
        #     for i in self.scene.objects: i.visible = 0
        # self.sceneObjects = [] # Seems like you have to have a python ref to scene objects in order to free their memory        
        # n = max(Numeric.shape(data)) #len(self.rArray.IDS)
        # c = float(255)
        # for i in range(n):
        #     (name,x,y,z) = (self.labels[i], dataJ[i, 0], dataJ[i, 1], dataJ[i, 2])
        #     if self.labelBox.IsChecked(): self.sceneObjects += [visual.label(pos=(x,y,z),text=name,height=14,box=0,opacity=0,color=(0,1,1))]
        #     b = visual.box(pos=(x,y,z), length=.02, height=.02, width=.02)
        #     #b = visual.sphere(pos=(x,y,z), radius=.02)
        #     color =  self.colorDict[ self.egoDict[self.labels[i]] ]
        #     colorObject = self.ColourDatabase.Find(color)
        #     b.color = (colorObject.Red()/c, colorObject.Green()/c, colorObject.Blue()/c)
        #     self.sceneObjects += [b]
        # wx.EndBusyCursor()
        pass
        
    def ScatterPlotOLD(self, data):
        # "Scatterplot of x,y data."
        # if self.jitterBox.IsChecked(): dataJ = self.jitter(data, 0.01)
        # else: dataJ = data
        # markers = wxPyPlot.PolyMarker(data)
        # graphics = wxPyPlot.PlotGraphics([markers], '', '1', '2')
        # self.Plot.SetEnableZoom(True)
        # self.Plot.SetXSpec('auto')
        # self.Plot.Draw(graphics)
        pass 
    
    def OnColor(self, event):
        # pass
        # #selection = self.Color.GetStringSelection()   
        pass

class HelpPanel(Panel):
    def __init__(self, parent):
        super(HelpPanel, self).__init__(parent)
        self.html = html.HtmlWindow(self, -1, pos=(125, 1), size=(470, 373), style=wx.NO_FULL_REPAINT_ON_RESIZE)
        self.html.LoadPage('Assets/HelpPanel/index.html')
        self.choices = ['Splash', 'Introduction', 'Input file format', 'KINDEMCOM files', 'Error checking', 'Relatedness', 'Founders', 'Lineages', 'Counting kin', 'Kin', 'Groups', 'Plotting', 'PCA', 'Sorting', 'License', 'Change log', 'Bugs', 'Contact info', 'Acknowledgements']
        self.helpControl = wx.ListBox(self, 130, pos=(1, 1), size=(123, 373), choices=self.choices, style=wx.LB_NEEDED_SB)
        self.helpControl.Bind(wx.EVT_LISTBOX, self.OnHelpSelect)

        #=============================OLD======================================    
        # def __init__(self, win):
        #     Panel.__init__(self, win)
        #     self.html = wxHtmlWindow(self, -1, (125, 1), (470, 373), style=wx.NO_FULL_REPAINT_ON_RESIZE)  #wx.HW_SCROLLBAR_AUTO)
        #     self.html.LoadPage('help/index.html')
        #     self.choices = ['Splash', 'Introduction', 'Input file format', 'KINDEMCOM files', 'Error checking', 'Relatedness', 'Founders', 'Lineages', 'Counting kin', 'Kin', 'Groups', 'Plotting', 'PCA', 'Sorting', 'License', 'Change log', 'Bugs', 'Contact info', 'Acknowledgements']
        #     self.helpControl = wx.ListBox(self, 130, (1,1), (123,373), self.choices, style=wx.LB_NEEDED_SB, validator=wx.DefaultValidator)
        #     wx.EVT_LISTBOX(self, 130, self.OnHelpSelect)
        #======================================================================

    def OnHelpSelect(self, event):
        helpSection = self.choices[event.GetSelection()]
        self.html.LoadPage('Assets/HelpPanel/index.html#' + helpSection)

    def EnableMenus(self):
        try:
            super(HelpPanel, self).EnableMenus()
            # Panel.EnableMenus(self)
        except:
            pass

class ChoiceMenu(wx.Choice):
    def __init__(self, parent, wid, loc, size, choices):
        wx.Choice.__init__(self, parent, wid, loc, size, choices)

    def Reset(self, newChoices):
        # # Reset choices, but try and set things back to the way they were if possible
        # text = self.GetStringSelection()
        # self.Clear()
        # for i in newChoices: self.Append(i)
        # if text in newChoices: self.SetStringSelection(text)
        # else: self.SetSelection(0)
        pass

# Builds App and Window
class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None, -1, appTitle)
        frame.Show(True)
        self.SetTopWindow(self.frame)
        return True

def BuildApp():
    app = MyApp(0) # MyApp(1) redirects errors to program window

    # Sustains Window
    app.MainLoop()
