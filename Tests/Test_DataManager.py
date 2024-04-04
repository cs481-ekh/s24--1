import pytest
import numpy
import DataManager

def test_data_manager_initialization():
    dm = DataManager.DataManager('Assets/TestData/HomemadeTestSet.csv')
    dm.createPandasDataFrame(columns=['ID', 'FatherID', 'MotherID', 'Sex', 'Living'], \
                             values=['M', 'F', 'Y', 'N', ''], \
                             removeHeader=True)
    assert dm.data is not None
    assert dm.df is not None

# Fixture to create a sample DataManager instance to use in multiple tests
@pytest.fixture
def sample_data_manager():
    # Create a sample DataManager instance with a CSV file
    sample_file = 'Assets/TestData/HomemadeTestSet.csv'
    data_manager = DataManager.DataManager(sample_file)
    data_manager.createPandasDataFrame(columns=['ID', 'FatherID', 'MotherID', 'Sex', 'Living'], \
                                       values=['M', 'F', 'Y', 'N', ''], \
                                       removeHeader=True)
    return data_manager

# Fixture to create a sample DataManager instance to use in multiple tests
# Uses Small Valid File
@pytest.fixture
def valid_data_manager():
    # Create a sample DataManager instance with a CSV file
    sample_file = 'Assets/TestData/ValidTestData.csv'
    data_manager = DataManager.DataManager(sample_file)
    data_manager.createPandasDataFrame(columns=['ID', 'FatherID', 'MotherID', 'Sex', 'Living'], \
                                       values=['M', 'F', 'Y', 'N', ''], \
                                       removeHeader=True)
    return data_manager

#region Validation

# Test checkForErrors function
def test_check_for_errors(sample_data_manager):
    assert len(sample_data_manager.checkForErrors()) == 0

#endregion

#region Utils

# Test IsEmptyCell function
def test_is_empty_cell(sample_data_manager):
    # Test IsEmptyCell function with known empty and non-empty cells
    assert sample_data_manager.IsEmptyCell(0, 'Ego') == False  # Non-empty cell
    assert sample_data_manager.IsEmptyCell(0, 'Father') == True   # Empty cell

# Test GetValueUsingColName function
def test_get_value(sample_data_manager):
    # Test GetValue function to ensure correct value retrieval
    assert sample_data_manager.GetValue(0, 'Ego') == '1'
    assert sample_data_manager.GetValue(0, 'Father') == None           # Empty cell

# Test GetNumberRows function
def test_get_number_rows(sample_data_manager):
    # Test GetNumberRows function to ensure correct number of rows
    assert sample_data_manager.GetNumberRows() == 100

# Test GetNumberCols function
def test_get_number_cols(sample_data_manager):
    # Test GetNumberCols function to ensure correct number of columns
    assert sample_data_manager.GetNumberCols() == 5

#endregion