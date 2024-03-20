#####
#NOTES: PETER BUSCHE
    # 1) Deleted all comments/documentation from previous author. 
        # Reason: Previous comments/documentation are preserved in boilerplate code. If we update and funcionalities, 
                #  we don't want leftover comments to potentially confuse us. Also, starting here but subject to change,
                # we know that all commented out code is the old code that I updated that was throwing errors. Thereofore,
                # we can quickly see what changed without having to use a comparison tool to the old code. For now, we can put 
                # comments up here.

    # 2) repr() vs str()? 
        # I would prefer is everything was str() 
        # if we update all repr() to str() will this cause errors later?

    # 3) All changes that involve the use of super()
        # I am not sure if this provides the correct functionality. I am trusting ChatGPT with this change.
        # Examples:
            # super(CustomDataTable, self).__init__() 
            # super(Genealogy, self).__init__(data, log, header)
            # super(CustTableGrid, self).__init__(parent, pos=pos, size=size)




# ERRORS:
    # 1) line 154: call to KinGroups
        # when we fix KinGroups and allow import statement this should be resolved

    # 2) line 211: call to pyp_newclasses
        # when we fix pyp_newclasses and allow import statement this should be resolved
####



import wx.grid
from wx.grid import *
import os
from relate import KinGroups
import pyp_newclasses, pyp_metrics


class CustomDataTable(wx.grid.GridTableBase):
#class CustomDataTable(wxPyGridTableBase):
    def __init__(self, data, log, header=1):
        super(CustomDataTable, self).__init__()
        # wxPyGridTableBase.__init__(self)
        # self.log = log
        if header:
            self.data = data[1:]
            self.colLabels = data[0]
        else:
            self.data = data
            self.colLabels = [''] * self.GetNumberCols()
            for i in range(self.GetNumberCols()):self.colLabels[i]=repr(i+1)

    def __iter__(self):
        return iter(self.data)
    
    def Sort(self, column):
        "Sort table by column. Convert strings to numbers, if possible, for sorting."
        tmp = []
        for s in self.data:
            if type(s[column]) == str:
                if s[column].isdigit(): tmp.append((int(s[column]), s))
                else: tmp.append((s[column], s))
            else: tmp.append((s[column], s))
        tmp.sort()
        self.data[:] = [x[1] for x in tmp]

    def GetNumberRows(self):
        return len(self.data)

    def GetNumberCols(self):
        return len(self.data[0])

    def IsEmptyCell(self, row, col):
        return not self.data[row][col] == ''

    def GetValue(self, row, col):
        try:
            return str(self.data[row][col])
        except IndexError:
            return ''

    def GetLine(self, row):
        try:
            return self.data[row]
        except IndexError:
            return ''

    def SetValue(self, row, col, value):
        try:
            self.data[row][col] = str(value)
        except IndexError:
            self.data.append([''] * self.GetNumberCols())
            self.SetValue(row, col, value)

            if self.GetView():
                self.GetView().ProcessTableMessage(wx.grid.GridTableMessage(self, wx.grid.GRIDTABLE_NOTIFY_ROWS_APPENDED, 1))

            # msg = wxGridTableMessage(self,                             # The table
            #                          wxGRIDTABLE_NOTIFY_ROWS_APPENDED, # what we did to it
            #                          1)                                # how many
            # self.GetView().ProcessTableMessage(msg)

    def GetColLabelValue(self, col):
        return self.colLabels[col]
    
class Genealogy(CustomDataTable):
    def __init__(self, data, log, header=1):
        super(Genealogy, self).__init__(data, log, header)
        # CustomDataTable.__init__(self, data, log, header)
        self.fieldDef = {}
        
    def makeDict(self):
        
        self.dict ={}
        for i in self.data:
            self.dict[i[self.fieldDef['ego']]]={'dad':i[self.fieldDef['father']],'mom':i[self.fieldDef['mother']], 'sex':i[self.fieldDef['sex']], 'row':self.data.index(i)}
            
    def CheckUniqueID(self):
        "Checks that all Ego ID codes are unique."
        temp=[]
        errorlog=[]
        for i in range(len(self.data)):
            if temp.count(self.data[i][self.fieldDef['ego']]) != 0:
                errorlog.append('ego ID '+self.data[i][self.fieldDef['ego']]+' is not unique.\nSee rows '+repr(temp.index(self.data[i][self.fieldDef['ego']])+1)+' and '+repr(i+1)+'\n\n')                
            temp.append(self.data[i][self.fieldDef['ego']])
        return errorlog
        
    def CheckSex(self, errorsOnly):
        "Checks for female fathers and male mothers.  Also checks for some other stuff."
        self.makeDict()
        errorlog=[]
        warninglog = []
        sexCodes = [self.fieldDef['male'], self.fieldDef['female']]
        livingCodes = [self.fieldDef['alive'], self.fieldDef['dead'], '3'] # Kindemcom living code 3 = unknown
        for i in range(len(self.data)):
            if self.data[i][self.fieldDef['sex']] not in sexCodes:
                errorlog.append('ego ' + self.data[i][self.fieldDef['ego']] + ' sex code not defined.  See row ' + repr(i+1)+'\n\n')
            if not self.fieldDef['allAlive']:
                if self.data[i][self.fieldDef['living']] not in livingCodes:
                    errorlog.append('ego ' + self.data[i][self.fieldDef['ego']] + ' living code not defined.  See row ' + repr(i+1)+'\n\n')
            if self.data[i][self.fieldDef['father']] in self.dict:
                if self.dict[self.data[i][self.fieldDef['father']]]['sex']==self.fieldDef['female']:
                    errorlog.append('ego '+self.data[i][self.fieldDef['father']]+' is a female father.\nSee rows '+repr(self.dict[self.data[i][self.fieldDef['father']]]['row']+1)+' & '+repr(i+1)+'\n\n')
            elif self.data[i][self.fieldDef['father']] != self.fieldDef['missing'] and not errorsOnly: warninglog.append("Father " + self.data[i][self.fieldDef['father']] + ' does not appear as an ego in the data file.  See row '+repr(i+1) + '\n\n')
            if self.data[i][self.fieldDef['mother']] in self.dict:
                if self.dict[self.data[i][self.fieldDef['mother']]]['sex']==self.fieldDef['male']:
                    errorlog.append('ego '+self.data[i][self.fieldDef['mother']]+' is a male mother.\nSee rows '+repr(self.dict[self.data[i][self.fieldDef['mother']]]['row']+1)+' & '+repr(i+1)+'\n\n')
            elif self.data[i][self.fieldDef['mother']] != self.fieldDef['missing'] and not errorsOnly: warninglog.append("Mother " + self.data[i][self.fieldDef['mother']] + ' does not appear as an ego in the data file.  See row '+repr(i+1) + '\n\n')
        return [errorlog, warninglog]

    def CheckIncest(self, app):
        "Checks for sibling incest and parent-offspring incest. Issues warnings only"
        warninglog = []
        functionList = [['mates'], ['parents'], ['full siblings'], ['halfsiblings'], ['offspring']]
        fL = ['', '', '', 'parent', '', 'sibling', '', 'halfsibling', '', 'offspring']
        kin = KinGroups(app.frame.notebook.Panel('Editor').table.data, app)
        kin.fieldDef = app.frame.notebook.Panel('Editor').GetFieldDef()
        matrix = kin.kinCount(0, functionList)
        for i in range(len(matrix)):
            if matrix[i][1] == 0: continue
            for j in matrix[i][2].split(','):
                for k in range(3,10,2):
                    if matrix[i][k] == 0: continue
                    if j in matrix[i][k+1].split(','):
                        warninglog += 'ego ID '+matrix[i][0]+' has an incestuous mating with their ' + fL[k] +  ' ID ' + j + '.  See row ' + repr(i) + '\n\n'
        return warninglog
        
    def PopulationStats(self):
        "Basic population statistics"
        stats = {}
        stats['keyOrder'] = ['No. of living', 'No. of living males', 'No. of living females', 'Sex ratio']
        living, males, females = 0, 0, 0
        for i in self.data:
            if i[self.fieldDef['living']] == self.fieldDef['alive'] or self.fieldDef['allAlive']:
                living += 1
                if i[self.fieldDef['sex']] == self.fieldDef['male']: males += 1            
                if i[self.fieldDef['sex']] == self.fieldDef['female']: females += 1
        stats['No. of living'] = repr(living)
        stats['No. of living males'] = repr(males)
        stats['No. of living females'] = repr(females)
        if females != 0: stats['Sex ratio'] = '%3d:100' % round(float(males)*100/females)
        return stats
    
class GenealogyFLO:
    """
    A file-like object to interface Genealogy objects with PyPedal.
    This class also translates some stuff into PyPedal format.
    """       
    def __init__(self, table, app):
        self.table = table
        self.sepchar = '\t'
        self.idToNum = ConvertIDToNumber(self.table.fieldDef['missing'])
        self.LineNumber = - 1
        self.createParentTable()
        
        self.sexTranslate = {self.table.fieldDef['male']: 'm', self.table.fieldDef['female']: 'f', self.table.fieldDef['missing']: '-999'}
        self.aliveTranslate = {self.table.fieldDef['alive']: '1', self.table.fieldDef['dead']: '0', self.table.fieldDef['missing']: '-999'}
                
        
        self.PyPedalOptions = {}
        self.PyPedalOptions['pedformat'] = 'asdxnl' 
        self.PyPedalOptions['pedfile'] = app.frame.path
        self.PyPedalOptions['infile'] = self
        self.PyPedalOptions['pedname'] = os.path.basename(app.frame.path)
        self.PyPedalOptions['sepchar'] = '\t'
        self.PyPedalOptions['slow_reorder'] = 1
        self.PyPedalOptions['renumber'] = 1
        
        
        self.pedigree = pyp_newclasses.NewPedigree(self.PyPedalOptions)
        self.pedigree.load()
        
        
        self.pIndex = {}
        for a in self.pedigree.pedigree: self.pIndex[str(a.animalID)] = a
        
        
        self.oIndex = {}
        for a in self.pedigree.pedigree: self.oIndex[str(a.originalID)] = a
        
        
        self.dIndex = {}
        for a in self.pedigree.pedigree: self.dIndex[str(a.name)] = a
        
        
        self.rIndex = {}
        for i, a in enumerate(self.pedigree.pedigree): self.rIndex[str(a.name)] = i
            
    def createParentTable(self):
        egos = [i[self.table.fieldDef['ego']] for i in self.table]
        fat = self.table.fieldDef['father']; mat = self.table.fieldDef['mother']
        miss = self.table.fieldDef['missing']
        fathers = []; mothers = []
        for i in self.table:
            if i[fat] not in egos and i[fat] not in fathers and i[fat] != miss: fathers += [i[fat]]
            if i[mat] not in egos and i[mat] not in mothers and i[mat] != miss: mothers += [i[mat]]
        f = [ [i, '0', '0', 'm', i, '0'] for i in fathers ]
        m = [ [i, '0', '0', 'f', i, '0'] for i in mothers ]
        self.psuedoTable = f + m
    
    def readline(self):
        self.LineNumber += 1
        if self.LineNumber < self.table.GetNumberRows():
            
            ln = self.table.GetLine(self.LineNumber)
            if ln != '':
                
                ln2  = self.idToNum.Convert(ln[self.table.fieldDef['ego']])    + self.sepchar
                ln2 += self.idToNum.Convert(ln[self.table.fieldDef['father']]) + self.sepchar
                ln2 += self.idToNum.Convert(ln[self.table.fieldDef['mother']]) + self.sepchar
                ln2 += self.sexTranslate[ ln[self.table.fieldDef['sex']] ] + self.sepchar
                ln2 += ln[self.table.fieldDef['ego']] + self.sepchar
                if not self.table.fieldDef['allAlive']: ln2 += self.aliveTranslate[ ln[self.table.fieldDef['living']] ]
                else: ln2 += '1'
                return ln2
            else:
                return 0
        else:
            
            try:
                
                self.psuedoTable[self.LineNumber - self.table.GetNumberRows()][0] = self.idToNum.Convert(self.psuedoTable[self.LineNumber - self.table.GetNumberRows()][0])
                return self.sepchar.join(self.psuedoTable[self.LineNumber - self.table.GetNumberRows()])
            except:
                return 0    
    
    def close(self):
        pass

class ConvertIDToNumber:
        """
        Map an arbitrary user ID code to a string representation of a numeric ID code.
        All ID's are mapped, even if they are already numeric.
        """
        def __init__(self, missing):
            
            self.OriginalToPyPedal = {missing: '0'}
            
            self.PyPedalToOriginal = {'0':missing}
            self.counter = 0
        
        def Convert(self, ID):
            "Assumes ID is a string; returns a string representation of a numeric ID"
            if ID in self.OriginalToPyPedal: return self.OriginalToPyPedal[ID]
            self.counter += 1; c = str(self.counter)
            self.OriginalToPyPedal[ID] = c
            self.PyPedalToOriginal[c] = ID
            return c
        
class CustTableGrid(wx.grid.Grid):
    def __init__(self, parent, table, pos, size):
        super(CustTableGrid, self).__init__(parent, pos=pos, size=size)
        self.SetTable(table, takeOwnership=True)
        self.dirty = True
        self.SetDefaultCellOverflow(False)

        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self.OnLeftDClick)
        self.Bind(wx.grid.EVT_GRID_LABEL_LEFT_DCLICK, self.OnLabelLeftDClick)
        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.OnCellLeftClick)
        self.Bind(wx.grid.EVT_GRID_CELL_CHANGED, self.OnGridCellChange)

    def OnLeftDClick(self, evt):
        "Edit on a double-click."
        if self.CanEnableCellControl():
            self.EnableCellEditControl()

    def OnLabelLeftDClick(self, evt):
        "Sort by this column on double-click."
        self.GetTable().Sort(evt.GetCol())
        self.ForceRefresh()

    def OnCellLeftClick(self, evt):
        cellContents = self.GetCellValue(evt.GetRow(), evt.GetCol())
        self.GetParent().GetParent().SetStatusText(cellContents)
        evt.Skip()

    def OnGridCellChange(self, evt):
        self.dirty = True



    # class CustTableGrid(wxGrid):
    #     def __init__(self, parent, table, loc, size):
    #         wxGrid.__init__(self, parent, -1, wx.Point(loc[0],loc[1]),wx.Size(size[0],size[1]))
    #         self.parent = parent
    #         self.SetTable(table, 1)
    #         self.dirty = True
    #         #self.SetRowLabelSize(0)
    #         #self.SetMargins(0,0)
    #         #self.AutoSizeColumns(false)
    #         self.SetDefaultCellOverflow(False)
    #         EVT_GRID_CELL_LEFT_DCLICK(self, self.OnLeftDClick)
    #         EVT_GRID_LABEL_LEFT_DCLICK(self, self.OnLabelLeftDClick)
    #         EVT_GRID_CELL_LEFT_CLICK(self, self.OnCellLeftClick)
    #         EVT_GRID_CELL_CHANGE(self, self.OnGridCellChange)

    #     def OnLeftDClick(self, evt):
    #         "Edit on a double-click."
    #         if self.CanEnableCellControl(): self.EnableCellEditControl()
                
    #     def OnLabelLeftDClick(self, evt):
    #         "Sort by this column on double-click."
    #         self.GetTable().Sort(evt.GetCol())
    #         self.ForceRefresh()
            
    #     def OnCellLeftClick(self, evt):
    #         cellContents = self.GetCellValue(evt.GetRow(), evt.GetCol())
    #         self.parent.app.frame.SetStatusText(cellContents)
    #         evt.Skip()
            
    #     def OnGridCellChange(self, evt):
    #         self.dirty = True