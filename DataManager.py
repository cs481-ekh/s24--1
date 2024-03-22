import pandas as pd

class DataManager:
    # Initializes DataManager using Input File
    def __init__(self, file):
        try:
            self.data = []
            self.dataFrame = None

            if file.endswith('.csv'): # CSV Only
                with open(file, 'r') as f:
                    temp = f.readlines()
                #sepchar = self.determineSepChar(temp)
                for line in temp:
                    #line = line.strip().split(sepchar)
                    line = line.strip().split(',') # CSV Specific
                    self.data.append([item.strip() for item in line])
            else:
                print("The DataManager only accepts CSV as a Valid File Format")
        except:
            print("There was a problem Initializing the DataManager")
    
    # Packs data into Pandas DataFrame Object
    # Requires Data and Alternate Column Order if applicable
    def createPandasDataFrame(self, data, columnOrder=['Ego', 'Father', 'Mother', 'Sex', 'Living']):
        num_columns = len(data[0])

        if columnOrder:
            column_names = columnOrder
        else:
            column_names = [f'Column{i+1}' for i in range(num_columns)]
        
        self.df = pd.DataFrame(data, columns=column_names)
    
        return self.df
    
    #region ========== MATH + PyPedal ==========

    #endregion

    #region ========== UTILS ==========

    # Sorts DataFrame by one column
    # Returns sorted version, but does not change the actual df
    def SortDataByCol(df, by='Ego'):
        sorted_df = df.sort_values(by=by)
        return sorted_df
    
    # Returns Number of Entries
    def GetNumberRows(self):
        return len(self.data)

    # Returns Number of Columns
    def GetNumberCols(self):
        return len(self.data[0])

    # Determines if cell is empty
    def IsEmptyCell(self, row, col):
        return not self.data[row][col] == ''

    # Returns value of single cell
    def GetValue(self, row, col):
        try:
            return str(self.data[row][col])
        except IndexError:
            return ''

    # Returns a full row
    def GetLine(self, row):
        try:
            return self.data[row]
        except IndexError:
            return ''
    
    # Returns complete dataset
    def getData(self):
        return self.data
    
    #endregion
    
    # TODO: Generic Export Method that takes in a type to determine what data to include
    def exportData(self, type):
        exportData = None
        match type:
            case "Relatedness":
                # exportData = Relatedness Export Data
                print("In Development")
            case "Kin":
                # exportData = Kin Export Data
                print("In Development")
            # ETC.
        
        #TODO: Export data using exportData
        pass