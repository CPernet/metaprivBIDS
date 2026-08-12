# Functionality inventory and browser GUI plan

This inventory is the acceptance checklist for replacing the PySide6 GUI. The
new interface must call `metaprivBIDS.corelogic`; privacy calculations and
transformations must not be reimplemented in event handlers.

## Data workspace

- Load CSV or TSV data and show its row/column dimensions.
- Preview the current working data in a sortable, paginated table.
- Profile columns: data type, distinct values, inferred categorical/continuous
  role, and missing-value count.
- Select multiple quasi-identifiers and one optional sensitive attribute.
- Load JSON metadata and inspect metadata for the selected column.
- Download the current transformed dataset as CSV.
- Restore a single column from the originally loaded data.

## Risk analysis

- Report total rows and columns, selected quasi-identifier count, sample-unique
  rows, k-anonymity, and optional l-diversity.
- Compute K-global contribution for each selected quasi-identifier.
- Compute K-combined contribution for selectable combination-size bounds.
- Export K-global and K-combined result tables.

## PIF / information gain

- Select variables, percentile, and an optional missing/mask value.
- Compute cell information gain (CIG), row information gain (RIG), and the PIF
  at the requested percentile.
- Show and export the complete CIG/RIG table.
- Show per-variable descriptive statistics and highlight the highest mean.
- Display a CIG heat map.
- Detect two-sided robust MAD outliers in RIG, display a box plot, and export
  the outlier table.

## SUDA2

- Select variables, sampling fraction, optional missing-value code, and score
  convention.
- Run `sdcMicro::suda2` through `rpy2`.
- Display and export row scores, percentage contribution by cell, variable
  contribution, and attribute-level contribution.
- Display a disclosure-score box plot and MAD outliers.

## Anonymisation

- Round a numeric column to a selected power of ten using nearest, upward, or
  downward rounding.
- Remove decimals by truncating values toward zero.
- Add Laplacian or Gaussian noise with explicit scale and optional random seed.
- Combine two or more categorical values under a replacement label.
- Record categorical combinations and display their generalisation hierarchy.
- Revert a transformed column to its initially loaded values.
- Keep all transformations available from both the browser and CLI.

## Interaction and safety

- Show actionable validation errors rather than stack traces.
- Disable analyses until data and required selections are available.
- Keep each browser session's data separate and in memory.
- Bind only to the local loopback interface by default; do not upload data to
  an external service.
- Make long SUDA2 calculations non-blocking and show progress.

## Collaborative implementation sequence

1. Data loading, profiling, preview, selection, and export.
2. Privacy summary, K-global, and K-combined.
3. One transformation at a time: rounding, decimal removal, noise,
   generalisation, hierarchy, and revert.
4. PIF/CIG tables, summaries, heat map, outlier plot, and exports.
5. SUDA2 tables, plots, and exports.
6. Cross-platform browser checks on Windows, macOS, and Linux; polish only
   after each functional checkpoint is accepted.
