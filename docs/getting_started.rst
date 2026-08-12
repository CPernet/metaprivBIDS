Getting started
===============

metaprivBIDS uses Conda for the compiled Python/R boundary and ``uv`` for the
Python application dependencies. This keeps ``sdcMicro`` and ``rpy2`` on a
known-compatible R runtime while retaining fast Python package installation.

Installation
------------

Install Miniforge or another Conda distribution, clone the repository, and
run these commands from its root directory:

.. code-block:: console

   conda env create -f environment.yml
   conda activate metaprivbids
   uv pip install -e ".[test]"

Verify both Python and the R bridge:

.. code-block:: console

   python -m pytest -q

Local browser interface
-----------------------

.. code-block:: console

   metaprivBIDS-gui

The application opens at ``http://127.0.0.1:8080``. It is deliberately bound
to the loopback interface, and uploaded data remains in the local process.

Command line
------------

``metaprivBIDS`` is the non-interactive entry point. For example:

.. code-block:: console

   metaprivBIDS privacy Use_Case_Data/adult_mini.csv \
     --columns age,education,occupation \
     --sensitive salary-class

See :doc:`cli` for every command and :doc:`examples` for a short workflow.

Python API
----------

.. code-block:: python

   from metaprivBIDS.corelogic import calculate_privacy_metrics, load_tabular_data

   data = load_tabular_data("Use_Case_Data/adult_mini.csv")
   metrics = calculate_privacy_metrics(
       data,
       ["age", "education", "occupation"],
       sensitive_attribute="salary-class",
   )

The functions are non-interactive, do not mutate their input dataframe, and
are shared by the CLI and browser interface.
