from fasthtml.common import *
from fasthtml import *

import plotly.graph_objects as go
import plotly.io as pio

import requests
import pandas as pd

app = FastHTML()

count = 0
df = pd.read_csv("../data/geo.csv", header=0, sep="|")

# Fetch capital cities when the module is loaded
def load_capitals():

    url = "https://restcountries.com/v3.1/all"
    response = requests.get(url)
    data = response.json()
    
    capitals = []
    latitudes = []
    longitudes = []
    for country in data:
        capital = country.get('capital', [None])[0]
        if capital:
            try:
                lat = country['latlng'][0]
                lng = country['latlng'][1]
            except KeyError:
                lat = None
                lng = None
            capitals.append(capital)
            latitudes.append(lat)
            longitudes.append(lng)

    return pd.DataFrame({'city': capitals, 'lat': latitudes, 'lng': longitudes})

# Load capitals immediately
df_capitals = load_capitals()

@app.get("/")
def home():

    cities = sorted(df_capitals["city"].astype(str).tolist())
    cities.insert(0, "Paris")
    options = [Option(city, value=city) for city in cities]
    form_html = Form(
        P(""),
        Select(*options, id="city-dropdown", name="city-dropdown"),
        Button("(Re)Center", hx_post="/plot", hx_target="#plot-container", hx_swap="innerHTML")
    )

    return Title("FastHTML"), Main(
        H1("Count Demo"),
        P(f"Count is set to {count}", id="count"),
        Button("Increment", hx_post="/increment", hx_target="#count", hx_swap="innerHTML"),
        H1("Plot geo data"),
        form_html,
        P(""),
        Html(Div("No data available yet.", id="plot-container"))
    )

@app.post("/increment")
def increment():
    print("incrementing")
    global count
    count += 1
    return f"Count is set to {count}"

@app.post("/plot")
async def plot(request: Request):
    form_data = await request.form()  # Use await here
    selected_city = form_data["city-dropdown"]
    selected_row = df_capitals[df_capitals["city"] == selected_city].iloc[0]
    lat = selected_row["lat"]
    lon = selected_row["lng"]

    fig = go.Figure(go.Scattermapbox(
        lat=df["lat"],
        lon=df["lng"],
        mode='markers',
        marker=dict(
            size=9,
            color='red'
        ),
        text=df["city"],
        hoverinfo='text'
    ))

    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        mapbox_style="open-street-map",
        mapbox_bounds={"west": -180, "east": 180, "south": -90, "north": 90},
        mapbox={'center': {'lat': lat, 'lon': lon}, 'zoom': 5},  # Center on selected city
        width=1024, height=768
    )

    log_message = "Data loaded and plot generated! Shape: %s"%str(df.shape)
    javascript_log = f"<script>console.log('{log_message}');</script>"

    plot_html = pio.to_html(fig, full_html=False)
    return plot_html + javascript_log

if __name__ == '__main__': 
    serve()
