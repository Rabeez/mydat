import altair as alt
import geopandas as gpd
import polars as pl
from catppuccin import PALETTE
from vega_datasets import data

colors = PALETTE.mocha.colors


@alt.theme.register("catppuccin_mocha", enable=True)
def catppuccin_mocha() -> alt.theme.ThemeConfig:
    return alt.theme.ThemeConfig(
        config=alt.theme.ConfigKwds(
            arc=alt.theme.RectConfigKwds(
                fill=colors.mauve.hex,  # pyright: ignore[reportArgumentType]
                stroke=colors.mauve.hex,  # pyright: ignore[reportArgumentType]
            ),
            area=alt.theme.AreaConfigKwds(fill=colors.mauve.hex),  # pyright: ignore[reportArgumentType]
            axis=alt.theme.AxisConfigKwds(
                grid=True,
                gridColor=colors.surface0.hex,  # pyright: ignore[reportArgumentType]
                domainColor=colors.surface2.hex,  # pyright: ignore[reportArgumentType]
                tickColor=colors.surface2.hex,  # pyright: ignore[reportArgumentType]
                labelAngle=0,
                labelColor=colors.overlay2.hex,  # pyright: ignore[reportArgumentType]
                labelFont='IBM Plex Sans Condensed, system-ui, -apple-system, BlinkMacSystemFont, ".SFNSText-Regular", sans-serif',
                labelFontSize=12,
                labelFontWeight=400,
                titleColor=colors.text.hex,  # pyright: ignore[reportArgumentType]
                titleFontSize=12,
                titleFontWeight=600,
            ),
            axisX=alt.theme.AxisConfigKwds(titlePadding=10),
            axisY=alt.theme.AxisConfigKwds(titlePadding=2.5),
            background=colors.base.hex,  # pyright: ignore[reportArgumentType]
            bar=alt.theme.BarConfigKwds(fill=colors.mauve.hex),  # pyright: ignore[reportArgumentType]
            circle=alt.theme.MarkConfigKwds(
                fill=colors.mauve.hex,  # pyright: ignore[reportArgumentType]
                stroke=colors.mauve.hex,  # pyright: ignore[reportArgumentType]
            ),
            point=alt.theme.MarkConfigKwds(color=colors.mauve.hex),  # pyright: ignore[reportArgumentType]
            range=alt.theme.RangeConfigKwds(
                category=[
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
                diverging=[
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
                heatmap=[
                    "#eeeeee",
                    "#e9e4f0",
                    "#e4daf2",
                    "#ded0f3",
                    "#d9c5f4",
                    "#d4bbf5",
                    "#cfb1f6",
                    "#caa6f7",  # mauve
                ],
                ordinal=[
                    "#eeeeee",
                    "#e9e4f0",
                    "#e4daf2",
                    "#ded0f3",
                    "#d9c5f4",
                    "#d4bbf5",
                    "#cfb1f6",
                    "#caa6f7",  # mauve
                ],
                ramp=[
                    "#eeeeee",
                    "#e9e4f0",
                    "#e4daf2",
                    "#ded0f3",
                    "#d9c5f4",
                    "#d4bbf5",
                    "#cfb1f6",
                    "#caa6f7",  # mauve
                ],
            ),
            legend=alt.theme.LegendConfigKwds(
                labelColor=colors.overlay2.hex,  # pyright: ignore[reportArgumentType]
                labelFont='IBM Plex Sans Condensed, system-ui, -apple-system, BlinkMacSystemFont, ".SFNSText-Regular", sans-serif',
                labelFontSize=12,
                labelFontWeight=400,
                titleColor=colors.text.hex,  # pyright: ignore[reportArgumentType]
                titleFontSize=12,
                titleFontWeight=600,
            ),
            rect=alt.theme.RectConfigKwds(
                fill=colors.mauve.hex,  # pyright: ignore[reportArgumentType]
                stroke=colors.mauve.hex,  # pyright: ignore[reportArgumentType]
            ),
            style={
                "guide-label": {
                    "fill": colors.overlay2.hex,
                    "font": 'IBM Plex Sans,system-ui,-apple-system,BlinkMacSystemFont,".sfnstext-regular",sans-serif',
                    "fontWeight": 400,
                },
                "guide-title": {
                    "fill": colors.overlay2.hex,
                    "font": 'IBM Plex Sans,system-ui,-apple-system,BlinkMacSystemFont,".sfnstext-regular",sans-serif',
                    "fontWeight": 400,
                },
            },  # pyright: ignore[reportArgumentType]
            title=alt.theme.TitleConfigKwds(
                anchor="start",
                color=colors.text.hex,  # pyright: ignore[reportArgumentType]
                dy=-15,
                font='IBM Plex Sans,system-ui,-apple-system,BlinkMacSystemFont,".sfnstext-regular",sans-serif',
                fontSize=16,
                fontWeight=600,
            ),
            view=alt.theme.ViewConfigKwds(fill=colors.base.hex, stroke=colors.base.hex),  # pyright: ignore[reportArgumentType]
        ),
    )


_ = alt.renderers.enable("browser")

cars_df = pl.from_dataframe(data.cars())
# print(df.head())
#
# adf = df.group_by("Origin").agg(pl.mean("Miles_per_Gallon"))
# print(adf)
#
# chart = alt.Chart(adf).mark_bar().encode(x="Origin", y="Miles_per_Gallon")
# chart.show()


bars = alt.Chart(cars_df.group_by("Cylinders").len()).mark_bar().encode(x="Cylinders", y="len")
line = (
    alt.Chart(cars_df.group_by("Origin", pl.col("Year").dt.year()).len())
    .mark_line()
    .encode(x="Year", y="len", color="Origin")
)
points = (
    alt.Chart(cars_df.group_by("Origin", pl.col("Year").dt.year()).len())
    .mark_point()
    .encode(x=alt.X("Year").scale(zero=False), y="len", color="Origin")
)
scatter = (
    alt.Chart(cars_df)
    .mark_point()
    .encode(x="Miles_per_Gallon", y="Displacement", color="Acceleration")
)
gbar = (
    alt.Chart(cars_df.group_by("Origin", pl.col("Year").dt.year()).len())
    .mark_bar()
    .encode(x="Year", y="len", color="Origin")
)
areas = (
    alt.Chart(
        cars_df.group_by("Origin", pl.col("Year").dt.year())
        .len()
        .with_columns(p=pl.col("len") / pl.col("len").sum().over("Year")),
    )
    .mark_area()
    .encode(x="Year", y="p", color="Origin")
)


gdf_us_counties = gpd.read_file(
    data.us_10m.url,
    engine="fiona",
    driver="TopoJSON",
    layer="counties",
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
