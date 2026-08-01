---
name: data-analyst
version: 1.1.0
author: hermeshub
license: MIT
description: End-to-end data analysis with visualization and reporting. SQL queries, stats, charts.
tags: [data-analysis, sql, charts, statistics, visualization]
requires_tools: [terminal]
---

# Data Analyst

End-to-end data analysis with visualization and reporting.

## When to Use

- User provides a dataset (CSV, JSON, Excel, SQLite)
- User asks for data exploration, trends, or patterns
- User needs charts, graphs, or visualizations
- User wants statistical analysis or hypothesis testing
- User asks for a summary report from data

## Procedure

1. **Load & inspect** — shape, dtypes, nulls, head
2. **Clean** — handle missing values, fix types, remove duplicates
3. **Explore** — distributions, correlations, outliers
4. **Analyze** — answer the specific question or find patterns
5. **Visualize** — create appropriate charts
6. **Report** — structured findings with actionable insights

## Quick Stats

```python
import pandas as pd
df = pd.read_csv("data.csv")
print(df.describe())
print(df.info())
print(df.isnull().sum())
```

## Visualization

```python
import matplotlib.pyplot as plt
import seaborn as sns

# Distribution
sns.histplot(df['column'], kde=True)

# Correlation
sns.heatmap(df.corr(), annot=True)

# Time series
df.plot(x='date', y='value', figsize=(12,6))
plt.savefig('chart.png', dpi=150, bbox_inches='tight')
```

## Statistical Tests

```python
from scipy import stats

# T-test
t_stat, p_val = stats.ttest_ind(group_a, group_b)

# Correlation
r, p = stats.pearsonr(x, y)
```

## Output Format

- Always start with a data summary (rows, columns, types)
- Show key statistics before diving into analysis
- Every chart must have title, axis labels, and legend
- End with actionable recommendations

## Pitfalls

- Always check for null values before calculations
- Verify data types (strings disguised as numbers)
- Watch for survivorship bias in time series
- State sample sizes and confidence intervals
- Don't confuse correlation with causation

## Verification

- Row counts match expected after cleaning
- Charts render correctly and save to disk
- Statistical results include p-values and effect sizes
