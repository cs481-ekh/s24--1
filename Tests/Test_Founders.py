import pytest
import numpy
import DataManager

# Fixture to create a sample DataManager instance to use in multiple tests
@pytest.fixture
def sample_data_manager():
    # Create a sample DataManager instance with a CSV file
    sample_file = 'Assets/TestData/HomemadeTestSet.csv'
    data_manager = DataManager.DataManager(sample_file)
    data_manager.generateBackendData(columns=['ID', 'FatherID', 'MotherID', 'Sex', 'Living'], \
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
    data_manager.generateBackendData(columns=['ID', 'FatherID', 'MotherID', 'Sex', 'Living'], \
                                       values=['M', 'F', 'Y', 'N', ''], \
                                       removeHeader=True)
    return data_manager

#region Founders
    
# Test getFounders function
def test_get_founders(valid_data_manager):
    # Test getFounders function to ensure founders are found
    #assert valid_data_manager.getFounders() != None
    assert len(valid_data_manager.getFounders()) == 6

# Test getFounders function
def test_update_df_with_founders(valid_data_manager):
    # Test getFounders function updates dataframe
    assert len(valid_data_manager.df) == 15
    valid_data_manager.getFounders()
    #assert valid_data_manager.getFounders() != None
    assert len(valid_data_manager.df) == 17

# Test getFounderStats function and subfunctions
def test_founder_statistics(valid_data_manager):
    valid_data_manager.getFounders()
    # Test getFounderStats function returns list of 5 elements
    assert len(valid_data_manager.getFounderStats()) == 5
    # Test values of those 5 elements using getter functions
    assert valid_data_manager.getFounderCount() == 6
    assert valid_data_manager.getMaxDescendants() == 19
    assert valid_data_manager.getMaxLivingDescendants() == 19
    assert valid_data_manager.getAvgDescendants() == 5.833
    assert valid_data_manager.getAvgLivingDescendants() == 5.833

#endregion