def CountNumbers(file_path):
    total_entries = 0
    with open(file_path, 'r') as file:
        for line in file:
            numbers = line.strip().split('\t')
            total_entries += len(numbers)
    return total_entries

file_path = 'sn_matrix_23'
total_entries = CountNumbers(file_path)

print(f'Total number of entries: {total_entries}')

