Getting started
===============

metaprivBIDS uses Conda for the compiled Python/R boundary and ``uv`` for the
Python application. This keeps ``sdcMicro`` and ``rpy2`` on a known-compatible
R runtime while retaining fast Python package installation.

Cross-platform installation
---------------------------

Install a current Miniforge release, clone the repository, and open PowerShell,
Git Bash, or a Linux terminal in its root directory. The provided installers
also locate Conda when a default Windows installation is not on ``PATH``:

.. code-block:: powershell

   powershell -ExecutionPolicy Bypass -File .\scripts\install.ps1

.. code-block:: bash

   bash scripts/install.sh

Alternatively, open the Start-menu **Miniforge Prompt** on Windows or any
Conda-enabled Linux terminal. The same manual commands then work in PowerShell
and Bash:

.. code-block:: console

   conda env create --file environment.yml
   conda run --name metaprivbids uv pip install -e .
   conda run --name metaprivbids metaprivBIDS --help

Activation is intentionally not required. ``conda run --name metaprivbids``
selects the correct Python/R environment without depending on shell-specific
Conda initialization. ``uv`` detects the Conda prefix supplied by ``conda run``
and installs the editable Python package into it.

Do not use ``uv sync`` with this environment: it can remove dependencies owned
by Conda. Update an existing installation with:

.. code-block:: console

   conda env update --name metaprivbids --file environment.yml
   conda run --name metaprivbids uv pip install -e .

Tests and notebooks
-------------------

Test dependencies are optional:

.. code-block:: console

   conda run --name metaprivbids uv pip install -e ".[test]"
   conda run --name metaprivbids python -m pytest -q

PowerShell and Bash both accept the double-quoted ``".[test]"`` argument. For
the executable tutorial, install its separate extra and launch Jupyter:

.. code-block:: console

   conda run --name metaprivbids uv pip install -e ".[notebook]"
   conda run --name metaprivbids jupyter lab MetaprivBIDS_CoreLogic_Tutorial.ipynb

Local browser interface
-----------------------

.. code-block:: console

   conda run --name metaprivbids metaprivBIDS-gui

The application opens at ``http://127.0.0.1:8080``. It binds to the local
loopback interface, and uploaded data remains in the local process.

Command line
------------

``metaprivBIDS`` is the non-interactive entry point. For example, this one-line
command is portable between PowerShell and Bash:

.. code-block:: console

   conda run --name metaprivbids metaprivBIDS privacy Use_Case_Data/adult_mini.csv --columns age,education,occupation --sensitive salary-class

See :doc:`cli` for every command and :doc:`examples` for a short workflow.

Documentation screenshots
-------------------------

The GUI walkthrough images are reproducible and stored in ``docs/_static``.
They can be refreshed after interface changes without taking screenshots by
hand:

.. code-block:: console

   conda run --name metaprivbids uv pip install -e ".[screenshots]"
   conda run --name metaprivbids python scripts/capture_docs_screenshots.py

Linux and macOS contributors must first install the Playwright Chromium
runtime with ``python -m playwright install chromium`` inside the environment.
Windows uses the installed Microsoft Edge browser. See :doc:`examples` for the
generated walkthrough.

Optional activation
-------------------

Users who prefer shorter commands can initialize Conda once, restart the
terminal, and activate the environment:

.. code-block:: powershell

   conda init powershell
   conda activate metaprivbids

.. code-block:: bash

   conda init bash
   conda activate metaprivbids

After activation, commands such as ``metaprivBIDS-gui`` and
``python -m pytest -q`` can be run directly.

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
