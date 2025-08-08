Getting Started
===============

Welcome to the Getting Started guide for metaprivBIDS.
This Python build tool enables a user to calculate a variety of different data privacy metrics on tabular data from a user interface.  

Installation
------------

The metaprivBIDS software runs on multiple platforms (e.g. Linux, macOS, Windows) that have a Python 3.7 installation.
It is recommended (but not required) to first create a virtual environment. This can be done with ``venv`` or, if pygraphviz fails (as it happens), with ``conda``.

.. code-block:: bash

    python -m venv metapriv
    source metapriv/bin/activate

or

.. code-block:: bash

    conda config --add pkgs_dirs ~/conda_pkgs
    conda create --name venv -c conda-forge "python>=3.7" graphviz pygraphviz r-base r-sdcMicro rpy2
    conda activate venv

You can then install metaprivBIDS by cloning the git repository.

.. code-block:: bash

    git clone https://github.com/CPernet/metaprivBIDS.git


To execute the program, make sure all dependencies from pyproject.toml are available in a Python 3.7 environment.
This can be done by running

.. code-block:: bash

    cd metaprivBIDS
    pip install -e . 


Basic Usage
-----------

Once installed, you can call and execute the program globally from any directory using the terminal/command prompt. This means you don't need to navigate to the program's installation folder; you can run it from anywhere.

.. code-block:: bash
    
    metaprivBIDS


prompting the program to start.


Command-Line Execution
----------------------
 
After following the installation guide, the metrics within the MetaprivBIDS tool can be called through an import statement without making use of the GUI.   

e.g. 

.. code-block:: python 

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




Next Steps
----------


- Explore the :ref:`Examples <examples_section>` to see an interactive tutorial on how to navigate the graphical user interface for MetaprivBIDS.

