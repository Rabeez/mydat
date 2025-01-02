import altair as alt
import geopandas as gpd
import polars as pl
from altair.theme import RangeConfigKwds, ConfigKwds, ThemeConfig
from catppuccin import PALETTE
from vega_datasets import data

colors = PALETTE.mocha.colors
RangeConfigKwds


@alt.theme.register("catppuccin_mocha", enable=True)
def catppuccin_mocha() -> alt.theme.ThemeConfig:
    return ThemeConfig(
        config=ConfigKwds(
            arc={"fill": colors.mauve.hex, "stroke": colors.mauve.hex},  # pyright: ignore[reportArgumentType]
            area={"fill": colors.mauve.hex},  # pyright: ignore[reportArgumentType]
            axis={  # pyright: ignore[reportArgumentType]
                "grid": True,
                "gridColor": colors.surface0.hex,
                "domainColor": colors.surface2.hex,
                "tickColor": colors.surface2.hex,
                "labelAngle": 0,
                "labelColor": colors.overlay0.hex,
                "labelFont": 'IBM Plex Sans Condensed, system-ui, -apple-system, BlinkMacSystemFont, ".SFNSText-Regular", sans-serif',
                "labelFontSize": 12,
                "labelFontWeight": 400,
                "titleColor": colors.text.hex,
                "titleFontSize": 12,
                "titleFontWeight": 600,
            },
            axisX={"titlePadding": 10},
            axisY={"titlePadding": 2.5},
            background=colors.base.hex,  # pyright: ignore[reportArgumentType]
            bar={"fill": colors.mauve.hex},  # pyright: ignore[reportArgumentType]
            circle={"fill": colors.mauve.hex, "stroke": colors.mauve.hex},  # pyright: ignore[reportArgumentType]
            point={"color": colors.mauve.hex},  # pyright: ignore[reportArgumentType]
            range={
                "category": [
                    colors.mauve.hex,
                    colors.green.hex,
                    colors.red.hex,
                    colors.blue.hex,
                    colors.peach.hex,
                    colors.teal.hex,
                    colors.pink.hex,
                    colors.lavender.hex,
                    colors.flamingo.hex,
                ],
                "diverging": [
                    "#f38ba8",  # red
                    "#ef9fc3",
                    "#e9b4d7",
                    "#e4c7e5",
                    "#e4d9ec",
                    "#e2daee",
                    "#e0dcef",
                    "#deddf0",
                    "#cfd1f2",
                    "#bcc7f5",
                    "#a5bdf7",
                    "#89b4fa",  # blue
                ],
                "heatmap": [
                    "#eeeeee",
                    "#e9e4f0",
                    "#e4daf2",
                    "#ded0f3",
                    "#d9c5f4",
                    "#d4bbf5",
                    "#cfb1f6",
                    "#caa6f7",  # mauve
                ],
                "ordinal": [
                    "#eeeeee",
                    "#e9e4f0",
                    "#e4daf2",
                    "#ded0f3",
                    "#d9c5f4",
                    "#d4bbf5",
                    "#cfb1f6",
                    "#caa6f7",  # mauve
                ],
                "ramp": [
                    "#eeeeee",
                    "#e9e4f0",
                    "#e4daf2",
                    "#ded0f3",
                    "#d9c5f4",
                    "#d4bbf5",
                    "#cfb1f6",
                    "#caa6f7",  # mauve
                ],
            },
            rect={"fill": colors.mauve.hex, "stroke": colors.mauve.hex},  # pyright: ignore[reportArgumentType]
            style={  # pyright: ignore[reportArgumentType]
                "guide-label": {
                    "fill": colors.overlay0.hex,
                    "font": 'IBM Plex Sans,system-ui,-apple-system,BlinkMacSystemFont,".sfnstext-regular",sans-serif',
                    "fontWeight": 400,
                },
                "guide-title": {
                    "fill": colors.overlay0.hex,
                    "font": 'IBM Plex Sans,system-ui,-apple-system,BlinkMacSystemFont,".sfnstext-regular",sans-serif',
                    "fontWeight": 400,
                },
            },
            title={
                "anchor": "start",
                "color": colors.text.hex,  # pyright: ignore[reportArgumentType]
                "dy": -15,
                "font": 'IBM Plex Sans,system-ui,-apple-system,BlinkMacSystemFont,".sfnstext-regular",sans-serif',
                "fontSize": 16,
                "fontWeight": 600,
            },
            view={"fill": colors.base.hex, "stroke": colors.base.hex},  # pyright: ignore[reportArgumentType]
        )
    )


_ = alt.renderers.enable("browser")

df = pl.from_dataframe(data.cars())
# print(df.head())
#
# adf = df.group_by("Origin").agg(pl.mean("Miles_per_Gallon"))
# print(adf)
#
# chart = alt.Chart(adf).mark_bar().encode(x="Origin", y="Miles_per_Gallon")
# chart.show()


bars = (
    alt.Chart(df.group_by("Cylinders").len()).mark_bar().encode(x="Cylinders", y="len")
)
line = (
    alt.Chart(df.group_by("Origin", pl.col("Year").dt.year()).len())
    .mark_line()
    .encode(x="Year", y="len", color="Origin")
)
points = (
    alt.Chart(df.group_by("Origin", pl.col("Year").dt.year()).len())
    .mark_point()
    .encode(x=alt.X("Year").scale(zero=False), y="len", color="Origin")
)
scatter = (
    alt.Chart(df)
    .mark_point()
    .encode(x="Miles_per_Gallon", y="Displacement", color="Acceleration")
)
gbar = (
    alt.Chart(df.group_by("Origin", pl.col("Year").dt.year()).len())
    .mark_bar()
    .encode(x="Year", y="len", color="Origin")
)
areas = (
    alt.Chart(
        df.group_by("Origin", pl.col("Year").dt.year())
        .len()
        .with_columns(p=pl.col("len") / pl.col("len").sum().over("Year"))
    )
    .mark_area()
    .encode(x="Year", y="p", color="Origin")
)


gdf_us_counties = gpd.read_file(
    data.us_10m.url, engine="fiona", driver="TopoJSON", layer="counties"
)
df_us_unemp = data.unemployment()

mheat = (
    alt.Chart(gdf_us_counties)
    .mark_geoshape()
    .transform_lookup(
        lookup="id",
        from_=alt.LookupData(data=df_us_unemp, key="id", fields=["rate"]),  # pyright: ignore[reportArgumentType]
    )
    .encode(alt.Color("rate:Q"))
    .project(type="albersUsa")
)

layout = (bars | line | points) & (scatter | gbar) & (areas | mheat)
layout = layout.properties(title="This is a test for themes").interactive()
layout.show()
