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

#region Relatedness

def test_no_crash(valid_data_manager):
    assert valid_data_manager.calculateRelatedness(0, 0, set()) == 1

def test_father_relatedness(valid_data_manager):
    assert valid_data_manager.calculateRelatedness(3, 1, set()) == 0.5

def test_mother_relatedness(valid_data_manager):
    assert valid_data_manager.calculateRelatedness(3, 2, set()) == 0.5

def test_sibling_relatedness(valid_data_manager):
    assert valid_data_manager.calculateRelatedness(3, 4, set()) == 0.25

def test_grandparent_relatedness(valid_data_manager):
    assert valid_data_manager.calculateRelatedness(6, 1, set()) == 0.25

def test_cousin_relatedness(valid_data_manager):
    assert valid_data_manager.calculateRelatedness(14, 4, set()) == 0.125
    assert valid_data_manager.calculateRelatedness(14, 15, set()) == 0.0625

#endregion