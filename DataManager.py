

class DataManager:
    # Initializes DataManager using Input File
    def __init__(self, file):
        try:
            self.data = []
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
        
# TODO: Reimplement if Ziker ever uses Non-CSV Files
    # Broken!!!!
    # def determineSepChar(self, d):
    #     sepchars = ['\t', ',', ' ']
    #     counts = {s: [] for s in sepchars}
    #     for line in d[:100]:
    #         for sep in sepchars:
    #             counts[sep].append(line.count(sep))
    #     for sep, count_list in counts.items():
    #         if count_list[0] != 0 and count_list.count(count_list[0]) == len(count_list):
    #             return sep
    #     return None
            
    def getData(self):
        return self.data