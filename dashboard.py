from dash import Dash, html, Input, Output, dcc #type:ignore
import dash_bootstrap_components as dbc #type:ignore
import plotly.express as px #type:ignore
import pandas as pd #type:ignore

df = pd.read_csv("clean_jobs.csv")

#initialise app
app=Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

#kpis
def gen_kpi_card(title, value, color):
    return dbc.Card(
        dbc.CardBody([html.H6(title, className="card-title", style={"textAlign":"center", "color":color, "fontweight":"bold"}),
                      html.H4(value, className="card-text", style={"textAlign":"center","fontweight":"bold"})
                      ]), className="shadow-sm rounded-3",
                      style={"background": f"linear-gradient(135deg, #737CA1, #6495ED)"}
    )


#app layout
app.layout=dbc.Container([
    #1st row- title + job role dropdown
    dbc.Row([
        dbc.Col(html.H1("📊 Job Market Dashboard",className = "heading1" ,style={"textAlign":"left","margin":"10px"}), width=8,
                style={"textAlign": "center","color": "#2C3E50","background": "linear-gradient(to right, #6A82FB, #FC5C7D)",
                       "padding": "5px 0px","borderRadius": "5px","fontFamily": "Arial, sans-serif","fontWeight": "bold",
                       "fontSize": "15px","textShadow": "2px 2px 4px rgba(0,0,0,0.3)"
        }),
        dbc.Col(
            # html.Label("Select Job Role:"),
            dcc.Dropdown(
                options=[
                    {"label": "Data Analyst", "value": "Data Analyst"},
                    {"label": "Data Engineer", "value": "Data Engineer"},
                    {"label": "Data Scientist", "value": "Data Scientist"},
                    {"label": "ML Engineer", "value": "ML Engineer"},
                    {"label": "AI Engineer", "value": "AI Engineer"},
                    {"label": "Miscellaneous", "value": "Miscellaneous"}
                ],
                value="Data Analyst", #default value
                id="role-dropdown"), width=4 )
    ], className = "rows", align="center"),

    #2nd row: bar chart + kpis
    dbc.Row([
        dbc.Col(dcc.Graph(id='bar-chart'), width=8,style={"margin-bottom": "8px"}),
        dbc.Col([
            dbc.Row([
                dbc.Col(id="kpi1", width=12),
            ], className="mb-3"),
            dbc.Row([
                dbc.Col(id="kpi4", width=12)
            ], className="mt-3"),
            dbc.Row([
                dbc.Col(id="kpi2", width=12)
            ], className="mt-3")

        ], width=4)
    ], className="rows2"),

    #3rd row- donut + heatmap + map
    dbc.Row([
        dbc.Col(dcc.Graph(id="donut-chart"), width=4),
        dbc.Col(dcc.Graph(id="heatmap"), width=4),
        dbc.Col(dcc.Graph(id="map"), width=4)
    ])
],fluid=True)


#callbacks
@app.callback(
    [Output("bar-chart", "figure"),
     Output("donut-chart", "figure"),
     Output("heatmap", "figure"),
     Output("map", "figure"),
     Output("kpi1", "children"),
     Output("kpi2", "children"),
    #  Output("kpi3", "children"),
     Output("kpi4", "children")],
    [Input("role-dropdown", "value")]
)

def update_dashboard(selected_role):
    dff=pd.DataFrame(df[df["Job Roles"]==selected_role])

    #bar chart- top cities
    city_counts=dff["Location"].value_counts().head(5).reset_index()
    city_counts.columns=["City","Jobs"]
    fig_bar=px.bar(city_counts, x="Jobs", y="City", height=350,color="City", color_discrete_sequence=px.colors.sequential.Sunset_r,
                   title=f"Top Cities for {selected_role}", template="plotly_dark")

    #donut chart- job roles share
    job_counts = df["Job Roles"].value_counts().reset_index()
    job_counts.columns = ["Job Role", "Jobs"]
    fig_donut = px.pie(job_counts, values="Jobs", names="Job Role", hole=0.5, height=390,
                       title="Job Roles Share", template="plotly_dark")
    
    #box
    fig_box = px.box(dff,x="Job Roles",y="Min Experience",title="Experience Distribution per Job Role", template="plotly_dark", height=390)
    
    #map- jobs by location
    city_coords = {
    "Mumbai": {"lat": 19.0760, "lon": 72.8777},"Delhi NCR": {"lat": 28.6139, "lon": 77.2090},"New Delhi": {"lat": 28.6139, "lon": 77.2090},
    "Noida": {"lat": 28.5355, "lon": 77.3910},"Gurugram": {"lat": 28.4595, "lon": 77.0266},"Bengaluru": {"lat": 12.9716, "lon": 77.5946},
    "Hyderabad": {"lat": 17.3850, "lon": 78.4867},"Pune": {"lat": 18.5204, "lon": 73.8567},"Chennai": {"lat": 13.0827, "lon": 80.2707},
    "Kolkata": {"lat": 22.5726, "lon": 88.3639},"Ahmedabad": {"lat": 23.0225, "lon": 72.5714},"Indore": {"lat": 22.7196, "lon": 75.8577},
    "Lucknow": {"lat": 26.8467, "lon": 80.9462},"Jaipur": {"lat": 26.9124, "lon": 75.7873},"Kochi": {"lat": 9.9312, "lon": 76.2673},
    "Nagpur": {"lat": 21.1458, "lon": 79.0882},"Surat": {"lat": 21.1702, "lon": 72.8311},"Raipur": {"lat": 21.2514, "lon": 81.6296},
    "Ludhiana": {"lat": 30.9010, "lon": 75.8573},"Mohali": {"lat": 30.7046, "lon": 76.7179},"Dehradun": {"lat": 30.3165, "lon": 78.0322},
    "Agra": {"lat": 27.1767, "lon": 78.0081},"Kanpur": {"lat": 26.4499, "lon": 80.3319},"Gwalior": {"lat": 26.2183, "lon": 78.1828},
    "Madurai": {"lat": 9.9252, "lon": 78.1198},"Bhubaneswar": {"lat": 20.2961, "lon": 85.8245},"Cuttack": {"lat": 20.4625, "lon": 85.8828},
}
    map_data = dff["Location"].value_counts().reset_index()
    map_data.columns = ["City","Jobs"]

    map_data = map_data[map_data["City"].isin(city_coords.keys())]

    map_data["lat"] = map_data["City"].apply(lambda x: city_coords[x]["lat"])
    map_data["lon"] = map_data["City"].apply(lambda x: city_coords[x]["lon"])

    fig_map = px.scatter_map(map_data, lat="lat", lon="lon", size="Jobs", color="City",
    hover_name="City",hover_data={"Jobs": True, "lat": False, "lon": False},
    map_style="carto-darkmatter",zoom=4,title="Jobs by Major Cities",height=390, template="plotly_dark"
)
    fig_map.update_layout(margin={"l":0, "r":0, "t":35, "b":0})

    #kpis
    total_jobs = df.shape[0]
    filtered_jobs = dff.shape[0]
    job_share = (filtered_jobs / total_jobs) * 100
    kpi1 = gen_kpi_card("Job Share (%)", f"{job_share:.2f}%", "#151B54")

    kpi2=gen_kpi_card("Avg Min Exp", round(dff["Min Experience"].mean(),1), "#8B0000")

    # top_industry = dff["Industry"].value_counts().idxmax()
    # top_industry_pct = round((dff["Industry"].value_counts().max() / len(dff)) * 100, 1)
    # kpi3 = gen_kpi_card("Top Industry", f"{top_industry} ({top_industry_pct}%)", "#28A745")
    # kpi3 = gen_kpi_card("Unique Companies", dff["Company"].nunique(), "#28A745")

    top_role = df["Job Roles"].value_counts().idxmax()
    top_role_pct = round((df["Job Roles"].value_counts().max() / len(df)) * 100, 1)
    kpi4 = gen_kpi_card("Top Role Demand", f"{top_role}", "#006600")

    dcc.Graph(
    id="bar-chart",
    style={
        "border": "1px solid #444",
        "borderRadius": "10px",
    })
    dcc.Graph(
    id="donut-chart",
    style={
        "border": "1px solid #444",
        "borderRadius": "10px",
    })
    dcc.Graph(
    id="heatmap",
    style={
        "border": "1px solid #444",
        "borderRadius": "10px",
    })
    dcc.Graph(
    id="map",
    style={
        "border": "1px solid #444",
        "borderRadius": "10px",
    }
)


    return fig_bar,fig_donut, fig_box, fig_map, kpi1, kpi2, kpi4


if __name__=='__main__':
    app.run(debug=True)
