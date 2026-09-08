metaprivBIDS documentation
==========================

metaprivBIDS is a local disclosure-risk workbench for tabular data. It offers
the same reusable privacy and anonymisation functions through a Python API,
command-line interface, and cross-platform browser interface.

Risk assessment includes:

- k-anonymity and l-diversity;
- K-global and K-combined contribution analysis;
- Personal Information Factor (PIF), cell information gain (CIG), and row
  information gain (RIG); and
- SUDA2 through the R ``sdcMicro`` package.

Mitigation includes direct-identifier pseudonymisation with row shuffling,
equal-width binning, rounding, decimal removal, Laplacian or Gaussian noise,
categorical generalisation, and per-column reversion.

.. toctree::
   :maxdepth: 2
   :caption: Contents

   getting_started
   understand_metrics
   cli
   examples
   functionality
   modules

License
-------

metaprivBIDS is licensed under the MIT License.

Indices
-------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
