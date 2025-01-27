import os
import pathlib
import re

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output, State
import cufflinks as cf

# Initialize app

app = dash.Dash(
    __name__,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
)
app.title = "Indicadores de México"
server = app.server

# Load data

APP_PATH = str(pathlib.Path(__file__).parent.resolve())

# Cambiar datos para México
df_lat_lon = pd.read_csv(
    os.path.join(APP_PATH, os.path.join("data", "lat_lon_municipios.csv"))
)
df_lat_lon["CVE_MUN"] = df_lat_lon["CVE_MUN"].apply(lambda x: str(x).zfill(5))

df_full_data = pd.read_csv(
    os.path.join(APP_PATH, os.path.join("data", "indicadores_mexico.csv"))
)
df_full_data["CVE_MUN"] = df_full_data["CVE_MUN"].apply(lambda x: str(x).zfill(5))
df_full_data["Municipio"] = (
    df_full_data["Nombre Municipio"] + ", " + df_full_data.Estado.map(str)
)

YEARS = list(range(2010, 2024))  # Años relevantes para México

BINS = [
    "0-5",
    "5.1-10",
    "10.1-15",
    "15.1-20",
    "20.1-25",
    "25.1-30",
    "30.1-35",
    "35.1-40",
    "40.1-45",
    "45.1-50",
    "50.1-55",
    "55.1-60",
    ">60",
]

DEFAULT_COLORSCALE = [
    "#fff4e0",  # Beige claro
    "#ffe3c4",  # Tonos cálidos suaves
    "#ffce9a",
    "#ffb36b",
    "#ff9c45",
    "#ff8325",
    "#f87017",
    "#e9600f",
    "#d2510d",
    "#ba430c",
    "#9c380c",
    "#7f2e0c",
    "#62250b",
    "#471c0b",
    "#2f1408",
    "#1e0d05",
]

DEFAULT_OPACITY = 0.85


mapbox_access_token = "tokenMap"  
mapbox_style = "mapbox://styles/mapbox/light-v10"  # Un estilo claro para mapas
mexico_center_coords = {"lat": 23.6345, "lon": -102.5528}  # Coordenadas aproximadas del centro de México


# App layout

app.layout = html.Div(
    id="root",
    children=[
        html.Div(
            id="header",
            children=[
                html.A(
                    html.Img(id="logo", src=app.get_asset_url("mexico-logo.png")),
                    href="https://www.gob.mx/",
                ),
                html.A(
                    html.Button("Datos Nacionales", className="link-button"),
                    href="https://datos.gob.mx/",
                ),
                html.A(
                    html.Button("Código Fuente", className="link-button"),
                    href="https://github.com/tu-repo/mexico-dash",
                ),
                html.H4(children="Indicadores Nacionales de México"),
                html.P(
                    id="description",
                    children="Este dashboard presenta un análisis de indicadores \
                    nacionales de los municipios de México, tales como tasas de mortalidad, \
                    educación, salud, y más. Los datos están basados en fuentes oficiales y \
                    reflejan tendencias recientes.",
                ),
            ],
        ),
        html.Div(
            id="app-container",
            children=[
                html.Div(
                    id="left-column",
                    children=[
                        html.Div(
                            id="slider-container",
                            children=[
                                html.P(
                                    id="slider-text",
                                    children="Desliza para cambiar el año:",
                                ),
                                dcc.Slider(
                                    id="years-slider",
                                    min=min(YEARS),
                                    max=max(YEARS),
                                    value=min(YEARS),
                                    marks={
                                        str(year): {
                                            "label": str(year),
                                            "style": {"color": "#d94e1f"},  # Rojo cálido
                                        }
                                        for year in YEARS
                                    },
                                ),
                            ],
                        ),
                        html.Div(
                            id="heatmap-container",
                            children=[
                                html.P(
                                    "Mapa de calor de indicadores ajustados por municipio en el año {0}".format(
                                        min(YEARS)
                                    ),
                                    id="heatmap-title",
                                ),
                                dcc.Graph(
                                    id="municipio-choropleth",
                                    figure=dict(
                                        layout=dict(
                                            mapbox=dict(
                                                layers=[],
                                                accesstoken=mapbox_access_token,
                                                style=mapbox_style,
                                                center=dict(
                                                    lat=mexico_center_coords["lat"], 
                                                    lon=mexico_center_coords["lon"],
                                                ),
                                                pitch=0,
                                                zoom=5,  # Nivel de zoom adecuado para México
                                            ),
                                            autosize=True,
                                        ),
                                    ),
                                ),
                            ],
                        ),
                    ],
                ),
                html.Div(
                    id="graph-container",
                    children=[
                        html.P(id="chart-selector", children="Selecciona un gráfico:"),
                        dcc.Dropdown(
                            options=[
                                {
                                    "label": "Histograma de mortalidad total (año único)",
                                    "value": "show_absolute_deaths_single_year",
                                },
                                {
                                    "label": "Histograma de mortalidad total (2010-2024)",
                                    "value": "absolute_deaths_all_time",
                                },
                                {
                                    "label": "Tasa ajustada de mortalidad (año único)",
                                    "value": "show_death_rate_single_year",
                                },
                                {
                                    "label": "Tendencias en tasa ajustada de mortalidad (2010-2024)",
                                    "value": "death_rate_all_time",
                                },
                            ],
                            value="show_death_rate_single_year",
                            id="chart-dropdown",
                        ),
                        dcc.Graph(
                            id="selected-data",
                            figure=dict(
                                data=[dict(x=0, y=0)],
                                layout=dict(
                                    paper_bgcolor="#FFF8E1",  # Fondo cálido (beige claro)
                                    plot_bgcolor="#FFF8E1",
                                    autofill=True,
                                    margin=dict(t=75, r=50, b=100, l=50),
                                ),
                            ),
                        ),
                    ],
                ),
            ],
        ),
    ],
)


@app.callback(
    Output("municipio-choropleth", "figure"),
    [Input("years-slider", "value")],
    [State("municipio-choropleth", "figure")],
)
def display_map(year, figure):
    cm = dict(zip(BINS, DEFAULT_COLORSCALE))

    # Configuración de datos para el mapa
    data = [
        dict(
            lat=df_lat_lon["Latitud"],
            lon=df_lat_lon["Longitud"],
            text=df_lat_lon["Información"],
            type="scattermapbox",
            hoverinfo="text",
            marker=dict(size=5, color="white", opacity=0),
        )
    ]

    # Anotaciones de leyenda
    annotations = [
        dict(
            showarrow=False,
            align="right",
            text="<b>Tasa ajustada por municipio<br>por año</b>",
            font=dict(color="#d94e1f"),  # Rojo cálido
            bgcolor="#FFF8E1",  # Fondo cálido
            x=0.95,
            y=0.95,
        )
    ]

    for i, bin in enumerate(reversed(BINS)):
        color = cm[bin]
        annotations.append(
            dict(
                arrowcolor=color,
                text=bin,
                x=0.95,
                y=0.85 - (i / 20),
                ax=-60,
                ay=0,
                arrowwidth=5,
                arrowhead=0,
                bgcolor="#FFF8E1",
                font=dict(color="#d94e1f"),
            )
        )

    # Ajuste del centro y zoom si ya hay figura
    if "layout" in figure:
        lat = figure["layout"]["mapbox"]["center"]["lat"]
        lon = figure["layout"]["mapbox"]["center"]["lon"]
        zoom = figure["layout"]["mapbox"]["zoom"]
    else:
        # Coordenadas centradas en México
        lat = 23.63450
        lon = -102.55278
        zoom = 5

    # Configuración del layout del mapa
    layout = dict(
        mapbox=dict(
            layers=[],
            accesstoken=mapbox_access_token,
            style=mapbox_style,
            center=dict(lat=lat, lon=lon),
            zoom=zoom,
        ),
        hovermode="closest",
        margin=dict(r=0, l=0, t=0, b=0),
        annotations=annotations,
        dragmode="lasso",
    )

    # Capa base geojson para municipios de México
    base_url = "https://geojson-mexico-source-example/"  # Cambia a tu URL de GeoJSON
    for bin in BINS:
        geo_layer = dict(
            sourcetype="geojson",
            source=base_url + str(year) + "/" + bin + ".geojson",
            type="fill",
            color=cm[bin],
            opacity=DEFAULT_OPACITY,
            fill=dict(outlinecolor="#afafaf"),
        )
        layout["mapbox"]["layers"].append(geo_layer)

    # Crear figura final
    fig = dict(data=data, layout=layout)
    return fig


@app.callback(Output("heatmap-title", "children"), [Input("years-slider", "value")])
def update_map_title(year):
    return "Mapa de calor de tasas ajustadas por edad de mortalidad por intoxicaciones en el año {0}".format(year)

@app.callback(
    Output("selected-data", "figure"),
    [
        Input("municipio-choropleth", "selectedData"),
        Input("chart-dropdown", "value"),
        Input("years-slider", "value"),
    ],
)
def display_selected_data(selectedData, chart_dropdown, year):
    if selectedData is None:
        return dict(
            data=[dict(x=0, y=0)],
            layout=dict(
                title="Haz clic y arrastra en el mapa para seleccionar municipios",
                paper_bgcolor="#1f2630",
                plot_bgcolor="#1f2630",
                font=dict(color="#2cfec1"),
                margin=dict(t=75, r=50, b=100, l=75),
            ),
        )
    
    pts = selectedData["points"]
    fips = [str(pt["text"].split("<br>")[-1]) for pt in pts]
    for i in range(len(fips)):
        if len(fips[i]) == 4:
            fips[i] = "0" + fips[i]
    dff = df_full_data[df_full_data["Municipio Código"].isin(fips)]
    dff = dff.sort_values("Año")

    regex_pat = re.compile(r"Unreliable", flags=re.IGNORECASE)
    dff["Tasa Ajustada"] = dff["Tasa Ajustada"].replace(regex_pat, 0)

    if chart_dropdown != "tasa_mortalidad_total":
        title = "Muertes absolutas por municipio, <b>1999-2016</b>"
        AGGREGATE_BY = "Muertes"
        if "mostrar_muertes_absolutas_un_año" == chart_dropdown:
            dff = dff[dff.Año == year]
            title = "Muertes absolutas por municipio, <b>{0}</b>".format(year)
        elif "mostrar_tasa_mortalidad_un_año" == chart_dropdown:
            dff = dff[dff.Año == year]
            title = "Tasa ajustada por edad de mortalidad por municipio, <b>{0}</b>".format(year)
            AGGREGATE_BY = "Tasa Ajustada"

        dff[AGGREGATE_BY] = pd.to_numeric(dff[AGGREGATE_BY], errors="coerce")
        muertes_o_tasa_por_fips = dff.groupby("Municipio")[AGGREGATE_BY].sum()
        muertes_o_tasa_por_fips = muertes_o_tasa_por_fips.sort_values()
        # Solo consideramos valores mayores a cero:
        muertes_o_tasa_por_fips = muertes_o_tasa_por_fips[muertes_o_tasa_por_fips > 0]
        fig = muertes_o_tasa_por_fips.iplot(
            kind="bar", y=AGGREGATE_BY, title=title, asFigure=True
        )

        fig_layout = fig["layout"]
        fig_data = fig["data"]

        fig_data[0]["text"] = muertes_o_tasa_por_fips.values.tolist()
        fig_data[0]["marker"]["color"] = "#2cfec1"  # Color cálido
        fig_data[0]["marker"]["opacity"] = 1
        fig_data[0]["marker"]["line"]["width"] = 0
        fig_data[0]["textposition"] = "outside"
        fig_layout["paper_bgcolor"] = "#1f2630"
        fig_layout["plot_bgcolor"] = "#1f2630"
        fig_layout["font"]["color"] = "#2cfec1"
        fig_layout["title"]["font"]["color"] = "#2cfec1"
        fig_layout["xaxis"]["tickfont"]["color"] = "#2cfec1"
        fig_layout["yaxis"]["tickfont"]["color"] = "#2cfec1"
        fig_layout["xaxis"]["gridcolor"] = "#5b5b5b"
        fig_layout["yaxis"]["gridcolor"] = "#5b5b5b"
        fig_layout["margin"]["t"] = 75
        fig_layout["margin"]["r"] = 50
        fig_layout["margin"]["b"] = 100
        fig_layout["margin"]["l"] = 50

        return fig

fig = dff.iplot(
    kind="area",
    x="Año",
    y="Tasa Ajustada",
    text="Municipio",
    categories="Municipio",
    colors=[
        "#FF6347",  # Tomate (rojo cálido)
        "#FF4500",  # Naranja oscuro
        "#4682B4",  # Azul acero
        "#EE82EE",  # Violeta
        "#3CB371",  # Verde medio
        "#FFD700",  # Oro
        "#8B4513",  # Marrón
        "#808080",  # Gris
        "#FF6347",  # Tomate (rojo cálido)
    ],
    vline=[year],
    asFigure=True,
)

for i, trace in enumerate(fig["data"]):
    trace["mode"] = "lines+markers"
    trace["marker"]["size"] = 4
    trace["marker"]["line"]["width"] = 1
    trace["type"] = "scatter"
    for prop in trace:
        fig["data"][i][prop] = trace[prop]

# Only show first 500 lines
fig["data"] = fig["data"][0:500]

fig_layout = fig["layout"]

# Modificación para los títulos en español
fig_layout["yaxis"]["title"] = "Tasa de mortalidad ajustada por edad por municipio"
fig_layout["xaxis"]["title"] = "Año"
fig_layout["yaxis"]["fixedrange"] = True
fig_layout["xaxis"]["fixedrange"] = False
fig_layout["hovermode"] = "closest"
fig_layout["title"] = "<b>{0}</b> municipios seleccionados".format(len(fips))
fig_layout["legend"] = dict(orientation="v")
fig_layout["autosize"] = True
fig_layout["paper_bgcolor"] = "#1f2630"
fig_layout["plot_bgcolor"] = "#1f2630"
fig_layout["font"]["color"] = "#2cfec1"
fig_layout["xaxis"]["tickfont"]["color"] = "#2cfec1"
fig_layout["yaxis"]["tickfont"]["color"] = "#2cfec1"
fig_layout["xaxis"]["gridcolor"] = "#5b5b5b"
fig_layout["yaxis"]["gridcolor"] = "#5b5b5b"

if len(fips) > 500:
    fig["layout"]["title"] = "Tasa de mortalidad ajustada por edad por municipio <br>(solo se muestran los primeros 500)"

return fig


if __name__ == "__main__":
    app.run_server(debug=True)
