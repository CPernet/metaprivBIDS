.. metaprivBIDS Documentation documentation master file, created by
   sphinx-quickstart on Thu Sep  5 17:40:28 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to metaprivBIDS documentation!
======================================================

This documentation provides an overview of the metaprivBIDS Graphical User Interface, including installation instructions, basic usage, and a tutorial to get you started.

metaprivBIDS provides tools for data risk assessment, including methods:

- K-anonymity [1]_
   - Searching each record in the dataset to see if they are indistinguishable from at least k − 1 other records with respect to a set of quasi-identifiers.

- ℓ-diversity [2]_
   - Looking at the diversity of the sensitive attribute. A dataset satisfies ℓ-diversity if each group of indistinguishable records has at least ℓ diverse values for the sensitive attribute(s), preventing easy inference of sensitive information.

- Sample Unique Detection Algorithm (SUDA) [3]_
   - The SUDA (Sample Unique Detection Algorithm) identifies records in a dataset that are unique based on a combination of quasi-identifiers. It works by flagging records with rare attribute combinations, indicating a higher risk of re-identification.

- Personal Information Factor (PIF) [4]_
   - The personal Information Factor (PIF) measures the risk of re-identification by analyzing how a record's quasi-identifiers deviate from the overall distribution in the dataset. A higher PIF suggests that the record's combination of attributes is rare, making it more likely to be uniquely identifiable within the population.


- K-Global 
   - K-Global attempts to capture an individual variable's k-anonymity contribution in the context of all other quasi-identifiers. This is done by evaluating the difference in unique rows when a given variable is removed. To account for the fact that, for example, continuous variables often result in more unique entries, we normalise by each column's unique value counts, subsequently penalising variables with few unique values but a high impact on unique rows.


.. [1] Sweeney, L. (2002). k-Anonymity: A Model for Protecting Privacy. *International Journal of Uncertainty, Fuzziness and Knowledge-Based Systems*, 10(05), 557-570.
.. [2] Machanavajjhala, A., Kifer, D., Gehrke, J., & Venkitasubramaniam, M. (2007). ℓ-Diversity: Privacy Beyond k-Anonymity. *ACM Transactions on Knowledge Discovery from Data (TKDD)*, 1(1), 3-es.
.. [3] Elliott, M. J., & Skinner, C. J. (2000). Identifying population uniques using limited information. *Proceedings of the Annual Meeting of the American Statistical Association*.
.. [4] Information Governance ANZ. (2019). *Privacy Impact Assessment eReport.* https://www.infogovanz.com/wp-content/uploads/2020/01/191202-ACS-Privacy-eReport.pdf

License 
======================================================

 metaprivBIDS is licensed under the MIT License (https://opensource.org/licenses/MIT).

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   
   getting_started
   modules  
   examples

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
