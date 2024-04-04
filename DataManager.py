import pandas as pd # Excellent Documentation: https://pandas.pydata.org/docs/reference/frame.html
import numpy as np

# Math Files
import Founders


class DataManager:
    # Initializes DataManager using Input File Name (../Example.csv)
    def __init__(self, filename):
        try:
            self.data = []
            self.df = None # DataFrame
            self.rm = None # Relate Matrix DataFrame
            self.founders = None # Founders DataFrame
            self.founderStats = None # Founders Descendant Stats

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
    # Requires 
            # Self for data input
            # Column Names from input file to select (Order Matters; Ego, Father, Mother, Sex, Living)
            # Expected Values from input file (Order Matters; Male, Female, Living, Dead, Missing Value)
            # Remove Header (First row is column names)
    def createPandasDataFrame(self, columns=['Ego', 'Father', 'Mother', 'Sex', 'Living'], values=['M', 'F', 'Y', 'N', ''], removeHeader=True):
        if self.data is None:
            print("You can't create the DataFrame: Data is None")
            return

        num_columns = len(self.data[0])
        column_names = self.data[0]

        # Removes first row if it is header
        if removeHeader:
            del self.data[0]
        
        # Puts Data into DataFrame
        self.df = pd.DataFrame(self.data, columns=column_names)

        # Replace input values to internal Standard (Sex: M/F, Living: Y/N, Missing: None)
        self.df.replace(values[0], 'M', inplace=True)
        self.df.replace(values[1], 'F', inplace=True)
        self.df.replace(values[2], 'Y', inplace=True)
        self.df.replace(values[3], 'N', inplace=True)
        self.df.replace(values[4], None, inplace=True)

        # Filters out all columns except: Ego, Father, Mother, Sex, Living
        self.df = self.df[[columns[0], columns[1], columns[2], columns[3], columns[4]]]

        # Change Column Names to internal Standard (Ego, Father, Mother, Sex, Living)
        self.df = self.df.rename(columns={columns[0]: 'Ego', \
                                          columns[1]: 'Father', \
                                          columns[2]: 'Mother', \
                                          columns[3]: 'Sex', \
                                          columns[4]: 'Living' })

        # TODO: Possible Solutions to Error in RMatrix (Ego, Father, Mother must be same Type!)

        self.df['Ego'] = pd.to_numeric(self.df['Ego'], errors='coerce', downcast='integer')
        self.df['Father'] = pd.to_numeric(self.df['Father'], errors='coerce', downcast='integer')
        self.df['Mother'] = pd.to_numeric(self.df['Mother'], errors='coerce', downcast='integer')
        
        self.df['Sex'] = self.df['Sex'].astype(str)
        self.df['Living'] = self.df['Living'].astype(str)

        return self.df
    
    # Validates DataFrame Logic
    # TODO: Create Incest Warnings
    def checkForErrors(self):
        # Initialize a list to store error messages
        error_messages = []

        # Check if Father references a male individual
        errors_father_sex = self.df[self.df['Father'].isin(self.df['Ego'])]
        errors_father_sex = errors_father_sex[errors_father_sex['Father'].map(self.df.set_index('Ego')['Sex']) != 'M']
        if not errors_father_sex.empty:
            for ego in errors_father_sex['Ego']:
                error_messages.append(f"Error for Ego {ego}: Father references a non-male individual.")

        # Check if Mother references a female individual
        errors_mother_sex = self.df[self.df['Mother'].isin(self.df['Ego'])]
        errors_mother_sex = errors_father_sex[errors_father_sex['Mother'].map(self.df.set_index('Ego')['Sex']) != 'F']
        if not errors_mother_sex.empty:
            for ego in errors_mother_sex['Ego']:
                error_messages.append(f"Error for Ego {ego}: Mother references a non-female individual.")

        # Check if Father is the same as Ego
        errors_father_egos = self.df[self.df['Father'] == self.df['Ego']]
        if not errors_father_egos.empty:
            for ego in errors_father_egos['Ego']:
                error_messages.append(f"Error for Ego {ego}: Father is the same as Ego.")

        # Check if Mother is the same as Ego
        errors_mother_ego = self.df[self.df['Mother'] == self.df['Ego']]
        if not errors_mother_ego.empty:
            for ego in errors_mother_ego['Ego']:
                error_messages.append(f"Error for Ego {ego}: Mother is the same as Ego.")
        
        # Check if Sex is valid Character
        errors_invalid_sex_egos = self.df[(self.df['Sex'] != 'M') & (self.df['Sex'] != 'F')]
        if not errors_invalid_sex_egos.empty:
            for ego in errors_invalid_sex_egos['Ego']:
                error_messages.append(f"Error for Ego {ego}: Sex colunm is an unexpected value.")
        
        # Check if Sex is valid Character
        errors_invalid_sex_egos = self.df[(self.df['Living'] != 'Y') & (self.df['Living'] != 'N')]
        if not errors_invalid_sex_egos.empty:
            for ego in errors_invalid_sex_egos['Ego']:
                error_messages.append(f"Error for Ego {ego}: Living colunm is an unexpected value.")


        # Add additional checks and error messages as needed.
                
        for line in error_messages:
            print(line)

        # Return all error messages
        return error_messages

    #region ========== Module Access =========

    # TODO: Relate Here

    #region ========= Founders =========

    # Returns Dataframe of Founders and creates a property with same data
    # Founders include: No Parents OR Non-existing Parents (Gets Added)
    def getFounders(self):
        self.df, self.founders = Founders.findFounders(self.df)
        return self.founders
    
    # Returns List[5] of Stats
    # List Oder: [Founders Count, Max Descendants, Max Living Descendants, Avg Descendants, Avg Living Descendants]
    def getFounderStats(self):
        self.founderStats = Founders.getStats(self.df, self.founders)
        return self.founderStats
    
    # Returns Founders Count
    def getFounderCount(self):
        if self.founderStats == None:
            self.founderStats = self.getFoundersStats()
        return self.founderStats[0]
    
    # Returns Max Descendants
    def getMaxDescendants(self):
        if self.founderStats == None:
            self.founderStats = self.getFoundersStats()
        return self.founderStats[1]
    
    # Returns Max Living Descendants
    def getMaxLivingDescendants(self):
        if self.founderStats == None:
            self.founderStats = self.getFoundersStats()
        return self.founderStats[2]
    
    # Returns Average Descendants
    def getAvgDescendants(self):
        if self.founderStats == None:
            self.founderStats = self.getFoundersStats()
        return self.founderStats[3]
    
    # Returns Average Living Descendants
    def getAvgLivingDescendants(self):
        if self.founderStats == None:
            self.founderStats = self.getFoundersStats()
        return self.founderStats[4]

    #endregion

    # TODO: Lineage Here
        
    # TODO: Kin Counter Here
        
    # TODO: Kin Here
        
    # TODO: Groups Here
        
    # TODO: Plot Here
        
    # TODO: PCA Here

    #endregion

    #region ========== MATH + PyPedal ==========

    

    # Returns a DataFrame of size N x N
    # Calculates the relatedness of each individual to each individual
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
    # TODO: Currently Returns Error: `Error calculating RMatrix: Cannot index by location index with a non-integer key`
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
        
        print(f"{i} {j}\n{self.df}")
        # Check if individuals i and j are distantly related through common ancestors
        print(f"Test:\n{type(self.df[self.df['Ego'] == i]['Mother'].iloc[0])}")
        for parent_i in [self.df[self.df['Ego'] == i]['Father'].iloc[0], [self.df['Ego'] == i]['Mother'].iloc[0]]:
            if pd.notnull(parent_i):
                for parent_j in [self.df[self.df['Ego'] == j]['Father'].iloc[0], self.df[self.df['Ego'] == j]['Mother'].iloc[0]]:
                    if pd.notnull(parent_j):
                        relatedness = self.calculateRelatedness(parent_i, parent_j, visited)
                        if relatedness > 0:
                            # Found a common ancestor
                            return relatedness * 0.5  # Relatedness is halved for each generation

        # Individuals i and j are not related
        return 0
    
    def isParent(self, i, j):
        # Check if individual i is a parent of individual j
        return self.df[self.df['Ego'] == j]['Father'].iloc[0] == i or self.df[self.df['Ego'] == j]['Mother'].iloc[0] == i
    
    def isSibling(self, i, j):
        # Check if individuals i and j share at least one parent
        return self.df[self.df['Ego'] == i]['Father'].iloc[0] == self.df[self.df['Ego'] == j]['Father'].iloc[0] or \
               self.df[self.df['Ego'] == i]['Mother'].iloc[0] == self.df[self.df['Ego'] == j]['Mother'].iloc[0]


    #endregion

    #region ========== Pandas Utils ==========

    def convert_to_int(value):
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

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
            ret = str(self.df.at[row, col])
            if ret == 'None':
                return None
            return ret
        except IndexError:
            return None
    
    # Returns T/F if single value is ''
    # Row is Index, Column is ColumnName (Ego, Father, Mother, ...)
    def IsEmptyCell(self, row, col):
        return self.GetValue(row, col) == None
    
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