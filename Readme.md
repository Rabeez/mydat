# MyDAT (Data Analysis Tool)

This is a simple online data anlaysis and visualization tool in the vein of Tableau.

## Key features

- Upload multiple files (CSV, Excel) to create tables
- Specify per-column datatypes for all tables
- Link tables together into a *single* ready-to-analyse table with SQL-style joins/unions
- Multiple chart types
  - Scatter
  - Bar
  - Histogram
  - Matrix
- Export charts as
  - static PNG/SVG
  - interactive HTML

## Implementation details

- Web
  - HTMX
  - Tailwind CSS
  - FastAPI (python)
- Analysis
  - Pandas
  - Polars
- Visualization
  - Plotly
  - Altair
