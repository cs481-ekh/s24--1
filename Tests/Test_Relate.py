import pytest
import pandas as pd
import numpy as np
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
    if len(data_manager.checkForErrors()) == 0:
        data_manager.createNxGraph()
    return data_manager

#region Relatedness

def test_self_relatedness(valid_data_manager):
    assert valid_data_manager.calculateRelatedness(1, 1) == 1

def test_father_relatedness(valid_data_manager):
    assert valid_data_manager.calculateRelatedness(3, 1) == 0.5

def test_mother_relatedness(valid_data_manager):
    assert valid_data_manager.calculateRelatedness(3, 2) == 0.5

def test_sibling_relatedness(valid_data_manager):
    assert valid_data_manager.calculateRelatedness(3, 4) == 0.25

def test_grandparent_relatedness(valid_data_manager):
    assert valid_data_manager.calculateRelatedness(6, 1) == 0.25

def test_cousin_relatedness(valid_data_manager):
    assert valid_data_manager.calculateRelatedness(14, 4) == 0.125
    assert valid_data_manager.calculateRelatedness(14, 15) == 0.0625

#endregion

#region ReturnValues

def test_relatedness_stats(valid_data_manager):
    stats = valid_data_manager.getRelatednessStats()
    assert len(stats) == len(valid_data_manager.df)
    assert stats.loc[12]['FgCon'] == 1.0
    assert stats.loc[11]['FgAll'] == 0.1
    assert stats.loc[12]['Number of Relatives'] == 1
    assert stats.loc[2]['FgAll'] == 0.325

#endregion