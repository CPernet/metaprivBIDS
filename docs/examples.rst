.. _examples_section:

Example workflow
================

Start the browser application with ``metaprivBIDS-gui`` and work through one
functional group at a time:

1. In **Data**, upload ``Use_Case_Data/adult_mini.csv`` and review the preview
   and column profile.
2. In **Risk**, select the intended quasi-identifiers, optionally select
   ``salary-class`` as sensitive, and compute the privacy summary.
3. Compare K-global and K-combined results to identify variables or variable
   combinations that drive sample uniqueness.
4. In **Transform**, apply one generalisation at a time. Download the working
   data or restore an original column when a change is unsuitable.
5. In **PIF**, compute CIG/RIG, inspect the heat map and MAD outliers, and
   export the result table.
6. In **SUDA2**, run the R-backed analysis and review row, variable, and
   attribute-level contributions.

Every operation is also available through the :doc:`cli`, making browser
results reproducible in scripts.
