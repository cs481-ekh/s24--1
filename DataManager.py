import pandas as pd
import numpy as np
# Excellent Documntation for Pandas
# https://pandas.pydata.org/docs/reference/frame.html


class DataManager:
    # Initializes DataManager using Input File Name (../Example.csv)
    def __init__(self, filename):
        try:
            self.data = []
            self.df = None
            self.rm = None

            if filename.endswith('.csv'): # CSV Only
                with open(filename, 'r') as f:
                    temp = f.readlines()
                for line in temp:
                    line = line.strip().split(',') # CSV Specific
                    self.data.append([item.strip() for item in line])
            else:
                print("The DataManager only accepts CSV as a Valid File Format")
        except:
            print("There was a problem Initializing the DataManager")
    
    # Packs data into Pandas DataFrame Object
    # Requires Data and Alternate Column Order if applicable
    def createPandasDataFrame(self, columnOrder=['Ego', 'Father', 'Mother', 'Sex', 'Living']):
        if self.data is None:
            print("You can't create the DataFrame: Data is None")
            return

        num_columns = len(self.data[0])

        # Removes first row if it is header
        if not self.data[0][0].isnumeric():
            del self.data[0]

        if columnOrder:
            column_names = columnOrder
        else:
            column_names = [f'Column{i+1}' for i in range(num_columns)]
        
        self.df = pd.DataFrame(self.data, columns=column_names)
        self.df['Ego'] = self.df['Ego'].astype(int)
    
        return self.df
    
    #region ========== MATH + PyPedal ==========

    # Returns a DataFrame of size N x N
    # Calculates the relatedness of each individual to each individual
    # TODO: Currently No Math Done (Change Random() to actual function)
    def calculateRMatrix(self):
        try:
            num_individuals = len(self.df)
            r_matrix = pd.DataFrame(index=self.df['Ego'], columns=self.df['Ego'])

            for i in range(num_individuals):
                for j in range(num_individuals):
                    # Calculate relatedness between individuals i and j
                    relatedness = self.calculateRelatedness(i, j, set())
                    r_matrix.iloc[i, j] = relatedness

            return r_matrix
        except Exception as e:
            print("Error calculating RMatrix:", e)
            return None
    
    # Recursively Determines two individual's relatedness
    # Takes in Ego i and Ego j of self.df
    # Takes in blank set: visited, to not repeat people
    def calculateRelatedness(self, i, j, visited):
        # Check if individuals i and j are the same individual
        if i == j:
            return 1  # Full relatedness to oneself
        
        # Check if the relatedness between i and j has already been calculated
        if (i, j) in visited or (j, i) in visited:
            return 0  # Avoid infinite recursion
        
        # Add the current pair to the set of visited pairs
        visited.add((i, j))
        
        # Check if individuals i and j share a parent
        if self.isParent(i, j) or self.isParent(j, i):
            return 0.5  # Relatedness to a parent
        
        # Check if individuals i and j share a sibling
        if self.isSibling(i, j):
            return 0.25  # Relatedness to a sibling
        
        # Check if individuals i and j are distantly related through common ancestors
        for parent_i in [self.df.iloc[i]['Father'], self.df.iloc[i]['Mother']]:
            if pd.notnull(parent_i):
                for parent_j in [self.df.iloc[j]['Father'], self.df.iloc[j]['Mother']]:
                    if pd.notnull(parent_j):
                        relatedness = self.calculateRelatedness(parent_i, parent_j, visited)
                        if relatedness > 0:
                            # Found a common ancestor
                            return relatedness * 0.5  # Relatedness is halved for each generation

        # Individuals i and j are not related
        return 0
    
    def isParent(self, i, j):
        # Check if individual i is a parent of individual j
        return self.df.iloc[j]['Father'] == i or self.df.iloc[j]['Mother'] == i
    
    def isSibling(self, i, j):
        # Check if individuals i and j share at least one parent
        return self.df.iloc[i]['Father'] == self.df.iloc[j]['Father'] or \
               self.df.iloc[i]['Mother'] == self.df.iloc[j]['Mother']


    #endregion

    #region ========== Pandas Utils ==========

    # Sorts DataFrame by one column
    # Returns sorted version, but does not change the actual df
    def SortDataByCol(df, by='Ego'):
        sorted_df = df.sort_values(by=by)
        return sorted_df
    
    # Returns Number of Entries
    def GetNumberRows(self):
        return len(self.df)
    
    # Returns Number of Columns
    def GetNumberCols(self):
        return len(self.df.columns)
    
    # Returns value of single cell
    # Row is Index, Column is ColumnName (Ego, Father, Mother, ...)
        # df.iat is a possible alternative?
    def GetValue(self, row, col):
        try:
            return str(self.df.at[row, col])
        except IndexError:
            return None
    
    # Returns T/F if single value is ''
    # Row is Index, Column is ColumnName (Ego, Father, Mother, ...)
    def IsEmptyCell(self, row, col):
        return self.GetValue(row, col) == ''
    
    # Returns a single row from data
    def GetLine(self, index):
        try:
            return self.df.iloc[index].to_numpy()
        except IndexError:
            return None
    
    # Returns complete dataset
    def GetData(self):
        return self.df

    #endregion

    #region ========== UTILS OLD DESCENT ==========
    
    # # Returns Number of Entries
    # def GetNumberRows(self):
    #     return len(self.data)

    # # Returns Number of Columns
    # def GetNumberCols(self):
    #     return len(self.data[0])

    # # Determines if cell is empty
    # def IsEmptyCell(self, row, col):
    #     return not self.data[row][col] == ''

    # # Returns value of single cell
    # def GetValue(self, row, col):
    #     try:
    #         return str(self.data[row][col])
    #     except IndexError:
    #         return ''

    # # Returns a full row
    # def GetLine(self, row):
    #     try:
    #         return self.data[row]
    #     except IndexError:
    #         return ''
    
    # # Returns complete dataset
    # def getData(self):
    #     return self.data
    
    #endregion
    
    # # TODO: Generic Export Method that takes in a type to determine what data to include
    # def exportData(self, data, type):
    #     exportData = None
    #     match type:
    #         case "Relatedness":
    #             # exportData = Relatedness Export Data
    #             print("In Development")
    #         case "Kin":
    #             # exportData = Kin Export Data
    #             print("In Development")
    #         # ETC.
        
    #     #TODO: Export data using exportData
    #     pass