# Understand Metrics

metaprivBIDS measures sample uniqueness, sensitive-value diversity, and
information gain. Start by choosing **quasi-identifiers**: attributes that
someone might know about a participant. Choose the **sensitive attribute**
separately when assessing what could be learned about that participant.

## Worked example: Table 2

The following three six-person datasets reproduce the values in Table 2 of
[Kibsgaard et al. (2026), *Assessing metadata privacy in neuroimaging*](https://doi.org/10.1162/IMAG.a.1144)
([open-access full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC12926773/)).
The table is reformatted below under the article's
[CC BY 4.0 licence](https://creativecommons.org/licenses/by/4.0/).
Here, **sex assigned at birth and area are quasi-identifiers**; **disease
status is the sensitive attribute**. Row numbers are only reading aids.

### Scenario A

| Row | Sex assigned at birth | Area | Disease status |
| --- | --- | --- | --- |
| 1 | Female | City X | Yes |
| 2 | Male | Suburb | Yes |
| 3 | Male | Rural | Yes |
| 4 | Male | Suburb | No |
| 5 | Male | City X | No |
| 6 | Male | City X | No |

### Scenario B

| Row | Sex assigned at birth | Area | Disease status |
| --- | --- | --- | --- |
| 1 | Female | City X | Yes |
| 2 | Female | City X | Yes |
| 3 | Male | Rural | Yes |
| 4 | Male | Suburb | Yes |
| 5 | Male | City X | No |
| 6 | Male | City X | No |

### Scenario C

| Row | Sex assigned at birth | Area | Disease status |
| --- | --- | --- | --- |
| 1 | Female | City X | Yes |
| 2 | Female | City X | No |
| 3 | Male | Rural | Yes |
| 4 | Male | Rural | No |
| 5 | Male | City X | Yes |
| 6 | Male | City X | No |

## k-anonymity and sample-unique rows

**k-anonymity** is the smallest group size when rows are grouped by the
selected quasi-identifiers. A **sample-unique row** belongs to a group of
size one. Disease status does not define these groups.

In A, the Female/City X and Male/Rural groups each contain one person. In B,
Male/Rural and Male/Suburb remain singletons. In C, every group has two people.
The current application's results are:

| Metric | A | B | C |
| --- | --- | --- | --- |
| Sample-unique rows | 2 | 2 | 0 |
| k-anonymity | 1 | 1 | 2 |
| l-diversity | 1 | 1 | 2 |

## l-diversity

**l-diversity** is the smallest number of distinct sensitive values within
any quasi-identifier group. metaprivBIDS implements distinct-value diversity.

In B, the two Female/City X participants cannot be distinguished using these
quasi-identifiers, but both have disease status Yes: group membership reveals
that status. In C, each pair contains Yes and No, giving l-diversity 2.
This explains why repeated quasi-identifiers alone do not prevent sensitive
information disclosure. These k and l results agree with Table 2.

## K-global: contribution of one variable

K-global follows Equation 1 of the paper: remove each quasi-identifier and
count the decrease in **distinct combinations**, divided by that variable's
distinct non-missing value count.

```{math}
K_i = \frac{U(Q) - U(Q \setminus \{i\})}{V_i}
```

Here, {math}`U(A)` counts distinct combinations of the columns in {math}`A`,
regardless of how many participants share them. It does not count only
singletons. Higher values indicate a larger reduction in distinct combinations
upon removal. The application rounds K-global to one decimal place.

A and B each contain four distinct sex/area combinations, three areas, and
two sex values. Thus sex contributes {math}`(4-3)/2=0.5`, and area contributes
{math}`(4-2)/3`, displayed as 0.7 (0.67 in the paper).

C contains three combinations, each shared by two people. Removing either
variable leaves two distinct values, giving {math}`(3-2)/2=0.5` for both.
The absence of singleton records therefore does not imply zero K-global.

| K-global source | A: sex / area | B: sex / area | C: sex / area |
| --- | --- | --- | --- |
| Published Table 2 | 0.5 / 0.67 | 0.5 / 0.67 | 0.5 / 0.5 |
| Application (one decimal) | 0.5 / 0.7 | 0.5 / 0.7 | 0.5 / 0.5 |

## K-combined: contribution of several variables

K-combined applies the same distinct-combination logic to a subset of
quasi-identifiers {math}`C`:

```{math}
K_C = \frac{U(Q) - U(Q \setminus C)}{U(C)}
```

It reports the subset's distinct-combination count, the count after excluding
that subset, and the score. For complete data, a one-variable subset gives
the same value as K-global before rounding. This is an additional application
feature, not a metric reported in Table 2.

For C's full sex/area pair, the subset has three distinct combinations.
Removing both columns leaves one empty combination shared by all six rows,
so the score is {math}`(3-1)/3`, approximately 0.667. For A and B, the full-pair
score is {math}`(4-1)/4=0.75`.

**Counting conventions:** for a nonempty dataset, selecting no remaining
columns gives one empty combination; an empty dataset has zero combinations.
Missing values participate in combination counts. K-global excludes missing
values from its per-variable denominator, whereas K-combined includes them
in its subset denominator. A zero denominator produces `NaN`.

The exported column names `unique_rows_after_removal`, `unique_rows`, and
`unique_rows_excluding_columns` are retained for compatibility and now denote
distinct combinations. Earlier versions counted only singletons in K-global
and K-combined; recalculating may change their results. The privacy summary's
sample-unique count, k-anonymity, and l-diversity retain their original meanings.

## SUDA2: minimal combinations that single someone out

SUDA (Special Uniques Detection Algorithm) searches for minimal sample-unique
combinations: removing any attribute from such a combination makes it
non-unique. Smaller combinations receive greater weight, and a record can
have several contributing combinations. See the paper's Section 1.1.

In A, Female alone and Rural alone each single out a participant. In C,
neither a single quasi-identifier nor their pair singles anyone out.
metaprivBIDS calls R's `sdcMicro::suda2` and exports raw scores, disclosure
scores, and variable/cell contributions. Disclosure scores depend on the
sampling-fraction setting; distinguish them from the raw SUDA score.

## CIG, RIG, and PIF: information revealed by the other variables

**Cell information gain (CIG)** uses KL divergence to compare a variable's
overall distribution with its distribution conditional on the other selected
variables, as described in Section 1.1 of the paper.

For an information-gain analysis including all three example columns, B's
Female/City X group determines disease status, while in C every sex/area group
has the same Yes/No balance as the whole dataset. This illustrates why
information gain and uniqueness answer different questions. The browser
excludes the designated sensitive attribute from quasi-identifier selections;
the Python API can explicitly select all three columns for this illustration.

The application uses `piflib` to compute CIG, sums CIG across columns to obtain
each participant's **row information gain (RIG)**, and reports the requested
RIG percentile as the **Personal Information Factor (PIF)** (95th by default).
PIF is therefore a dataset summary at a chosen percentile; individual scores
in the exported table are RIG. Table 2 does not report numerical SUDA or PIF
results.

## Reading the results together

Use k and l to inspect the smallest groups, K-global and K-combined to explore
variable removal, and SUDA2 and information gain to investigate individual
records. The application also flags two-sided median absolute deviation
(MAD) outliers in RIG and disclosure scores; these are review prompts, not
proof of identification. As discussed in the paper's Sections 2.2.1 and 4.4,
interpret scores alongside what an outside observer could know and what the
variables mean.

See [Command line](cli.rst) for metric commands and
[Examples](examples.rst) for the browser workflow.
