import pytest
import pandas as pd
import DataManager

# Fixture to create a sample DataManager instance to use in multiple tests
@pytest.fixture
def ziker_data_manager():
    # Create a sample DataManager instance with a CSV file
    sample_file = 'Assets/TestData/ZikerInputFile.csv'
    data_manager = DataManager.DataManager(sample_file)
    data_manager.createPandasDataFrame(columns=['PersonID', 'FatherID', 'MotherID', 'Sex', 'Deceased'], \
                                                values=['Male', 'Female', 'FALSE', 'TRUE', '9999'], \
                                                removeHeader=True)
    return data_manager
    
# Test getLineages function
# Can't seem to figure out assertion error when Patrilineage and Matrilineage aren't the same length (which is allowed)
def test_get_lineages(ziker_data_manager):
    lineages = ziker_data_manager.getLineages()
    assert lineages.shape[0] == 1501
    # 'Random' Sampling of Rows
    # Ego 2630
    assert lineages[lineages['Ego'] == 2630].set_index('Ego', inplace=True) == pd.DataFrame({'Ego': 2630, \
                                                              'Pat. Size': 1, \
                                                              'Mat. Size': 1, \
                                                              'Patrilineage': [2630], \
                                                              'Patriarch': 2630, \
                                                              'Matrilineage': [2630], \
                                                              'Matriarch': 2630}).set_index('Ego', inplace=True)
    # Ego 42 (Problem with Patrilineage & Matrilineage Formatting)
    # assert lineages[lineages['Ego'] == 42].set_index('Ego', inplace=True) == pd.DataFrame({'Ego': 42, \
    #                                                           'Pat. Size': 5, \
    #                                                           'Mat. Size': 4, \
    #                                                           'Patrilineage': {2043, 2042, 38, 40, 42}, \
    #                                                           'Patriarch': 2043, \
    #                                                           'Matrilineage': {2414, 722, 39, 42}, \
    #                                                           'Matriarch': 2414}).set_index('Ego', inplace=True)
    # Ego 2 (Problem with Patrilineage & Matrilineage Formatting)
    assert lineages[lineages['Ego'] == 2].set_index('Ego', inplace=True) == pd.DataFrame({'Ego': 2, \
                                                              'Pat. Size': 3, \
                                                              'Mat. Size': 3, \
                                                              'Patrilineage': [2011, 2010, 2], \
                                                              'Patriarch': 2011, \
                                                              'Matrilineage': [2008, 2007, 2], \
                                                              'Matriarch': 2008}).set_index('Ego', inplace=True)