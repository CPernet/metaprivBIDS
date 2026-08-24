Command-line interface
======================

Every analysis and transformation is available without the browser GUI. The
examples below use ``conda run``, so they work unchanged in PowerShell, Git
Bash, and Linux without activating the environment. When the environment is
already active, omit ``conda run --name metaprivbids``.

Run ``metaprivBIDS --help`` to list commands or
``metaprivBIDS COMMAND --help`` for the complete options of one command.

Inspect data and measure privacy
--------------------------------

.. code-block:: console

   conda run --name metaprivbids metaprivBIDS inspect Use_Case_Data/adult_mini.csv
   conda run --name metaprivbids metaprivBIDS inspect Use_Case_Data/adult_mini.csv --continuous-threshold 45 --output column_profile.csv
   conda run --name metaprivbids metaprivBIDS privacy Use_Case_Data/adult_mini.csv --columns age,education,marital-status,occupation,relationship,sex --sensitive salary-class
   conda run --name metaprivbids metaprivBIDS k-global Use_Case_Data/adult_mini.csv --columns age,education,marital-status,occupation --output k_global.csv
   conda run --name metaprivbids metaprivBIDS k-combined Use_Case_Data/adult_mini.csv --columns age,education,marital-status,occupation --min-size 2 --max-size 4 --output k_combined.csv

``inspect`` profiles storage and inferred analysis types. ``privacy`` reports
sample uniqueness, k-anonymity, and optional l-diversity. ``k-global``
evaluates variables individually; ``k-combined`` evaluates combinations.

Transform values
----------------

.. code-block:: console

   conda run --name metaprivbids metaprivBIDS round input.csv --column age --exponent 1 --mode nearest --output rounded.csv
   conda run --name metaprivbids metaprivBIDS bin input.csv --column age --bins 5 --output binned_by_count.csv
   conda run --name metaprivbids metaprivBIDS bin input.csv --column age --width 10 --output binned_by_width.csv
   conda run --name metaprivbids metaprivBIDS remove-decimals input.csv --column age --output whole_numbers.csv
   conda run --name metaprivbids metaprivBIDS noise input.csv --column age --distribution laplacian --scale 2 --seed 42 --output laplacian_noise.csv
   conda run --name metaprivbids metaprivBIDS noise input.csv --column age --distribution gaussian --scale 2 --seed 42 --output gaussian_noise.csv
   conda run --name metaprivbids metaprivBIDS combine input.csv --column occupation --values Sales,Service --replacement Customer-facing --output generalized.csv

Rounding modes are ``nearest``, ``up``, and ``down``. The non-negative
exponent selects the power of ten: ``0`` means units, ``1`` tens, and ``2``
hundreds. Binning uses equal-width intervals; provide exactly one of ``--bins``
or ``--width``. Noise distributions are ``laplacian`` and ``gaussian``. An
optional seed makes the noise reproducible.

Replace direct identifiers
--------------------------

.. code-block:: console

   conda run --name metaprivbids metaprivBIDS pseudonymize input.csv --id-column ID --output released.csv --key-output identifier_key.csv

This command replaces every complete, unique identifier with a unique
alphanumeric value of the same displayed length and randomly reorders the
released rows. The separate old-to-new key can reverse the operation. Store it
as sensitive data and never distribute it with the released dataset.

Compute CIG, RIG, and PIF
-------------------------

.. code-block:: console

   conda run --name metaprivbids metaprivBIDS cig input.csv --columns age,education,occupation --percentile 95 --output cig_values.csv --summary-output cig_summary.csv --outliers-output rig_outliers.csv --outlier-threshold 2.2414

The main output contains row- and cell-level CIG/RIG values. The optional
summary and robust MAD outlier tables are separate exports. Use
``--mask-value nan`` or another value when it should be masked during the
calculation.

Compute SUDA2
-------------

.. code-block:: console

   conda run --name metaprivbids metaprivBIDS suda input.csv --columns age,education,occupation --sample-fraction 0.2 --output suda_scores.csv --contribution-percent-output suda_contribution_percent.csv --attribute-contributions-output suda_attribute_contributions.csv --attribute-level-output suda_attribute_levels.csv

SUDA2 runs through R and ``sdcMicro``. The main output contains record scores;
the optional exports contain cell percentages, variable contributions, and
attribute-level contributions. Use ``--missing-value NUMBER`` for an explicit
missing-value code and ``--legacy-scores`` only when legacy scaling is needed.

Inspect JSON metadata
---------------------

.. code-block:: console

   conda run --name metaprivbids metaprivBIDS metadata metadata.json
   conda run --name metaprivbids metaprivBIDS metadata metadata.json --column age

Without ``--column``, the complete JSON file is printed. With it, only the
entry associated with that column is printed.
