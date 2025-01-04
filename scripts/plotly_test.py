import plotly.express as px
import polars as pl

gapminder = pl.DataFrame(px.data.gapminder())
df_2007 = gapminder.filter(pl.col("year") == 2007)

fig = px.scatter(
    df_2007,
    x="gdpPercap",
    y="lifeExp",
    size="pop",
    color="continent",
    log_x=True,
    size_max=60,
    template="plotly_dark",
    title="Gapminder 2007",
)
fig.show()
