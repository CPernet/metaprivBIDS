# metaprivBIDS

[![Documentation Status](https://readthedocs.org/projects/metaprivbids/badge/?version=latest)](https://metaprivbids.readthedocs.io/en/latest/?badge=latest)




This Python build tool enables a given user to calculate a variety of different data privacy metrics on tabular data from a user interface. 

# Methods

#### Assesing Privacy risk: 

- K-anonymity [^1]
- ℓ-diversity [^2]
- Sample Unique Detection Algorithm (SUDA) [^3]
- Privacy Information Factor (PIF) [^4]

[^1]: Sweeney, L. (2002). k-Anonymity: A Model for Protecting Privacy. *International Journal of Uncertainty, Fuzziness and Knowledge-Based Systems*, 10(05), 557-570.
[^2]: Machanavajjhala, A., Kifer, D., Gehrke, J., & Venkitasubramaniam, M. (2007). ℓ-Diversity: Privacy Beyond k-Anonymity. *ACM Transactions on Knowledge Discovery from Data (TKDD)*, 1(1), 3-es.
[^3]: Elliott, M. J., & Skinner, C. J. (2000). Identifying population uniques using limited information. *Proceedings of the Annual Meeting of the American Statistical Association*.
[^4]: Information Governance ANZ. (2019). *Privacy Impact Assessment eReport.* [Link](https://www.infogovanz.com/wp-content/uploads/2020/01/191202-ACS-Privacy-eReport.pdf)


#### Mitigating Privacy Risk

- Noise addition
- Field generalisation
- Rounded Approximation 


# Input data format

Input can be in either CSV or TSV format. 
For meta information an option of load of json file is possible. 

# Software installation


### Option 1
The metaprivBIDS software runs on multiple platforms (e.g. Linux, MacOS, Windows) that have a Python 3 installation.
It is recommended (but not required) to first create a virtual environment.

  
 In the event of permission issues for system dependent files, you might want to set the pkgs_dirs option in Conda's configuration to use a directory that is writable by you.
 
```console 
conda config --add pkgs_dirs ~/conda_pkgs
```
Creates the environment. 

```console 
conda create --name venv python=3.x.x
```

Activates the environment. 

```console
conda activate venv 
```

Graphviz requires system level dependencies as well as rpy2 and might need to be installed with 

```console
conda create --name venv -c conda-forge "python>=3.7" graphviz pygraphviz r-base r-sdcMicro rpy2
```

if not available. 

You can then install metaprivBIDS by first cloning the git repository.

```console
git clone https://github.com/CPernet/metaprivBIDS.git
```

cd into the MetaprivBIDS folder  

```console
cd MetaprivBIDS
```
and then run 

```console
pip install -e . 
```


### Option 2 


```console 
python -m venv venv
source venv/bin/activate
```

You can then install metaprivBIDS by cloning the git repository.

```console
git clone https://github.com/CPernet/metaprivBIDS.git
```


# Dependencies

To execute the program make sure all dependencies from pyproject.toml is available in a python 3.7 environment as stated in the software installation. 
This can be done by first ```cd``` into the MetaprivBIDS directory and then running

```console
pip install -e . 
```

# Usage

To execute the program run from command line 

```console
metaprivBIDS
```

prompting the program to start.


# Command-Line Execution
After following the installation guide, the metrics within the MetaprivBIDS tool can be called through an import statement without making use of the GUI.   

e.g. 

```python
from metaprivBIDS.metaprivBIDS.corelogic.metapriv_corelogic import metaprivBIDS_core_logic
metapriv = metaprivBIDS_core_logic()

# Load the data
data_info = metapriv.load_data('metaprivBIDS/Use_Case_Data/adult_mini.csv')

# Inspect {column, unique value count, column type}
data = data_info["data"]
print("Column Types:",'\n')
print(data_info["column_types"],'\n')

# Select Quasi-Identifiers
selected_columns = ["age", "education", "marital-status", "occupation", "relationship","sex","salary-class"]
results_k_global = metapriv.find_lowest_unique_columns(data, selected_columns)
print('Find Influential Columns:','\n')
print(results_k_global)

# Compute Personal Information Factor 
pif_value, cig_df = metapriv.compute_cig(data, selected_columns)
print("PIF Value:", pif_value)
print("CIG DataFrame:")
print(cig_df)


# Run SUDA2 computation
results_suda = metapriv.compute_suda2(data, selected_columns, sample_fraction=0.3, missing_value=-999)

# Access results
data_with_scores = results_suda["data_with_scores"]
attribute_contributions = results_suda["attribute_contributions"]
attribute_level_contributions = results_suda["attribute_level_contributions"]
```




## Related tools








