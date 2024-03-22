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
    
    def createPandasDataFrame(self, data, columnOrder=['Ego', 'Father', 'Mother', 'Sex', 'Living']):
        num_columns = len(data[0])

        if columnOrder:
            column_names = columnOrder
        else:
            column_names = [f'Column{i+1}' for i in range(num_columns)]
        
        self.df = pd.DataFrame(data, columns=column_names)
    
        return self.df
    
    def sort_family_tree(df, by='Ego'):
        sorted_df = df.sort_values(by=by)
        return sorted_df

    def initializeTableFormat(self):
        self.dict ={}
        for i in self.data:
            self.dict[i[self.fieldDef['ego']]]={
                'dad':i[self.fieldDef['father']],
                'mom':i[self.fieldDef['mother']],
                'sex':i[self.fieldDef['sex']],
                'row':self.data.index(i)
            }
        pass
            
    def getData(self):
        return self.data
    
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