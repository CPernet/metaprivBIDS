import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch
from metaprivBIDS.corelogic.metapriv_corelogic import metaprivBIDS_core_logic


@pytest.fixture
def mock_data():
    # Create a simple mock dataset for testing
    return pd.DataFrame({
        'salary': [50000, 60000, 70000, 50000, 60000],
        'city': ['New York', 'Los Angeles', 'New York', 'San Francisco', 'Los Angeles'],
        'department': ['HR', 'Engineering', 'Marketing', 'HR', 'Engineering'],
        'age': [25, 35, 45, 25, 35]
    })


@pytest.fixture
def mp():
    # Return an instance of the metaprivBIDS_core_logic class
    return metaprivBIDS_core_logic()


def test_load_data(mp, tmpdir, mock_data):
    # Create a temporary CSV file for testing load_data
    csv_file = tmpdir.join("data.csv")
    mock_data.to_csv(csv_file, index=False)

    result = mp.load_data(str(csv_file))

    assert result['data'].equals(mock_data), "Loaded data should match the mock data"
    assert 'salary' in result['column_unique_counts'], "Column 'salary' should be counted"


def test_find_lowest_unique_columns(mp, mock_data):
    selected_columns = ['salary', 'city', 'department']
    results = mp.find_lowest_unique_columns(mock_data, selected_columns)

    assert isinstance(results, dict), "Results should be a dictionary"
    assert 'salary' in results, "Column 'salary' should be in the results"


def test_calculate_unique_rows(mp, mock_data):
    selected_columns = ['salary', 'city', 'department']
    sensitive_attr = 'salary'

    unique_rows_stats = mp.calculate_unique_rows(mock_data, selected_columns, sensitive_attr)

    assert isinstance(unique_rows_stats, dict), "The result should be a dictionary"
    assert 'total_rows' in unique_rows_stats, "Total rows should be present in the result"
    assert 'k_anonymity' in unique_rows_stats, "k-anonymity should be in the result"
    assert 'l_diversity' in unique_rows_stats, "l-diversity should be in the result"


def test_compute_combined_column_contribution(mp, mock_data):
    selected_columns = ['salary', 'city', 'department']
    result_df = mp.compute_combined_column_contribution(mock_data, selected_columns, min_size=1, max_size=2)

    assert len(result_df) > 0, "The result dataframe should not be empty"
    assert 'Combination' in result_df.columns, "Result should contain column 'Combination'"
    assert 'Unique Rows' in result_df.columns, "Result should contain column 'Unique Rows'"


def test_round_values(mp, mock_data):
   
    precision = 1 
    modified_data = mp.round_values(mock_data.copy(), 'age', precision)
   
    expected_values = [30, 40, 50, 30, 40]  
    assert (modified_data['age'] == expected_values).all(), "Ages should be rounded to the nearest 10"






def test_revert_to_original(mp, mock_data):
    mp.round_values(mock_data.copy(), 'age', 1)  # First round the values
    reverted_data = mp.revert_to_original(mock_data.copy(), 'age')

    assert reverted_data['age'].equals(mock_data['age']), "Reverted data should match the original data"


def test_add_noise(mp, mock_data):
    noisy_data = mp.add_noise(mock_data.copy(), 'age', 'laplacian')

    assert not noisy_data['age'].equals(mock_data['age']), "Noisy data should differ from the original"





def test_combine_values(mp, mock_data):
    combined_values_history = mp.combine_values(mock_data, 'city')

    assert 'city' in combined_values_history, "City column should be tracked in combined values history"
    assert combined_values_history['city'][0][1] == 'Big City', "New York and Los Angeles should be replaced by 'Big City'"


def test_compute_cig(mp, mock_data):
   
    with patch('piflib.pif_calculator.compute_cigs') as mock_compute_cigs, \
         patch('builtins.input', side_effect=['', '50']): 
        
      
        mock_compute_cigs.return_value = pd.DataFrame({'RIG': [0, 1, 2, 3, 4]})

      
        pif_value, cig_df_sorted = mp.compute_cig(mock_data, ['salary', 'city', 'department'])

      
        mock_compute_cigs.assert_called_once()

       
        assert pif_value == 2.0  
        assert not cig_df_sorted.empty  


def test_describe_cig(mp):
    cig_data = pd.DataFrame(np.random.rand(5, 5), columns=list('ABCDE'))
    cig_data['RIG'] = np.random.rand(5)
    description = mp.describe_cig(cig_data)

    assert isinstance(description, pd.DataFrame), "Description should be a DataFrame"
    assert 'A' in description.columns, "The description should contain data columns"


def test_generate_heatmap(mp):
    cig_data = pd.DataFrame(np.random.rand(5, 5), columns=list('ABCDE'))
    cig_data['RIG'] = np.random.rand(5) 

    mp.generate_heatmap(cig_data)


def test_plot_tree_graph(mp, mock_data):
    combined_values_history = mp.combine_values(mock_data, 'city')
    mp.plot_tree_graph(mock_data, 'city')
