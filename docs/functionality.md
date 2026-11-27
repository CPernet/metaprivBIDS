# Functionality reference

The browser, command line, and Python API use the reusable functions in
`metaprivBIDS.corelogic`. Privacy calculations and transformations are not
reimplemented in GUI event handlers.

## Data workspace

- Load CSV or TSV data and show its row/column dimensions.
- Preview the current working data in a sortable, paginated table.
- Profile columns: storage type, distinct values, missing-value count, an
  editable categorical/continuous analysis role, and a separate direct-
  identifier privacy role.
- Select multiple quasi-identifiers and one optional sensitive attribute.
- Select every eligible quasi-identifier with a checkbox while excluding the
  sensitive attribute and direct identifier; individual selections remain
  editable.
- Load JSON metadata and inspect metadata for the selected column.
- Download the current transformed dataset as CSV.
- Restore a single column from the originally loaded data.

## Risk analysis

- Report total rows and columns, selected quasi-identifier count, sample-unique
  rows, k-anonymity, and optional l-diversity.
- Compute K-global contribution for each selected quasi-identifier.
- Compute K-combined contribution for selectable combination-size bounds.
- Select all eligible quasi-identifiers for contribution analysis with the
  same editable checkbox behavior used by the privacy summary.
- Export K-global and K-combined result tables.

## PIF / information gain

- Select variables, percentile, and an optional missing/mask value.
- Select all eligible quasi-identifiers with one checkbox.
- Compute cell information gain (CIG), row information gain (RIG), and the PIF
  at the requested percentile.
- Show and export the complete CIG/RIG table.
- Show per-variable descriptive statistics and highlight the highest mean.
- Display a CIG heat map.
- Detect two-sided robust MAD outliers in RIG, display a box plot, and export
  the outlier table; plot hover labels identify the source row.

## SUDA2

- Select variables, sampling fraction, optional missing-value code, and score
  convention.
- Select all eligible quasi-identifiers with one checkbox.
- Run `sdcMicro::suda2` through `rpy2`.
- Display and export row scores, percentage contribution by cell, variable
  contribution, and attribute-level contribution.
- Display a disclosure-score box plot and MAD outliers; plot hover labels
  identify the source row.

## Anonymisation

- Select a complete, unique direct-identifier column, replace its values with
  unique same-length alphanumeric pseudonyms, and shuffle/reset the released
  row order.
- Exclude the designated direct identifier from quasi-identifier selections
  and from ordinary numeric and categorical transformation menus.
- Retain the old-to-new identifier key in the local session and export it as a
  separate sensitive CSV for renaming related datasets.
- Round a numeric column to a selected power of ten using nearest, upward, or
  downward rounding.
- Bin a numeric column into a chosen number of equal-width intervals or into
  intervals with a fixed width, preserving missing values. Previews and exports
  use compact JSON array labels such as `[20,25]`. Intervals include their lower
  bound and exclude their upper bound, except for the final interval, which
  includes both. A constant column uses equal bounds, such as `[22,22]`.
- Optionally replace numeric values with the midpoint of the interval bounds
  (the median of the bounds, not the sample median) and add a `<column>_range`
  column. For example, `age` becomes `22.5` with `age_range` set to `[20,25]`.
  Existing range columns are protected from overwriting. Missing values remain
  missing in both columns. Enable **Use median and add range column** in the
  browser or pass `--median` to the CLI `bin` command.
- Export the working copy as CSV or TSV; TSV uses `n/a` for missing values.
  For BIDS numeric `age`, use median mode. If a JSON dictionary is loaded,
  update the age definition and define `age_range`, retaining units and
  unrelated entries. Data downloads bundle the table and updated dictionary
  in a ZIP; a separate JSON download is also available. Loading the dictionary
  after binning applies the same definitions. Restoring the original column
  restores its dictionary entry and removes the generated range column.
  CLI `bin --metadata participants.json` writes an updated sidecar next to
  the output table; `--metadata-output` selects a different destination.
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
