#USAGE: python convertToCSV.py

with open(r'C:\Users\peter\Dropbox\CS481\PersonalDescent\Source\SN_matrix_23', 'r') as infile, \
     open(r'C:\Users\peter\Dropbox\CS481\PersonalDescent\Source\out.csv', 'w') as outfile:
    for line in infile:
        outfile.write(','.join(line.split()) + '\n')

