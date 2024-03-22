import pytest
import DataManager

def test_data_manager_initialization():
    dm = DataManager('/Assets/TestData/HomemadeTestSet.csv')
    assert dm.data is not None

# Fixture to create a sample DataManager instance to use in multiple tests
@pytest.fixture
def sample_data_manager():
    # Create a sample DataManager instance with a CSV file
    sample_file = '/Assets/TestData/HomemadeTestSet.csv'
    data_manager = DataManager(sample_file)
    return data_manager

# Test IsEmptyCell function
def test_is_empty_cell(sample_data_manager):
    # Test IsEmptyCell function with known empty and non-empty cells
    assert sample_data_manager.IsEmptyCell(0, 0) == False  # Non-empty cell
    assert sample_data_manager.IsEmptyCell(0, 1) == True   # Empty cell

# Test GetValue function
def test_get_value(sample_data_manager):
    # Test GetValue function to ensure correct value retrieval
    assert sample_data_manager.GetValue(0, 0) == '1'
    assert sample_data_manager.GetValue(0, 1) == ''           # Empty cell

# Test GetLine function
def test_get_line(sample_data_manager):
    # Test GetLine function to ensure correct row retrieval
    assert sample_data_manager.GetLine(0) == ['1', '', '', 'M', 'N']
    assert sample_data_manager.GetLine(100) == ''                            # Out of range index

# Test GetNumberRows function
def test_get_number_rows(sample_data_manager):
    # Test GetNumberRows function to ensure correct number of rows
    assert sample_data_manager.GetNumberRows() == 100

# Test GetNumberCols function
def test_get_number_cols(sample_data_manager):
    # Test GetNumberCols function to ensure correct number of columns
    assert sample_data_manager.GetNumberCols() == 5
