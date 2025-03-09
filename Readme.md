# MyDAT (Data Analysis Tool)

This is a simple online data anlaysis and visualization tool in the vein of Tableau.

## Learning Outcomes

- Hypermedia-driven web development (HTMX)
- TailwindCSS
- FastAPI latest techniques
- Jinja advanced features
- Python polymorphic types
- HTTP file upload
- Custom plotly theme (unified UI)
- User state in SQLite

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
