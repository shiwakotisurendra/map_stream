import os
import tempfile
import streamlit as st
import folium
from streamlit_folium import folium_static, st_folium
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import geocoder
from shapely.geometry import LineString, Polygon, Point, shape, box
import geopandas as gpd
import requests
from branca.element import Figure

# Streamlit configuration
st.set_page_config(page_title="Dashboard with Folium Map and Plots", layout="wide")


@st.cache_data
def europe_capital():
    # Sample data for the capital cities of Europe
    data = {
        "City": [
            "London",
            "Paris",
            "Madrid",
            "Berlin",
            "Rome",
            "Athens",
            "Vienna",
            "Amsterdam",
        ],
        "Population": [
            8961989,
            2140526,
            3266126,
            3769495,
            2872800,
            6640466,
            1911191,
            873555,
        ],
    }

    # Retrieve latitude and longitude coordinates for each city
    latitudes = []
    longitudes = []
    for city in data["City"]:
        g = geocoder.osm(city)
        latitudes.append(g.lat)
        longitudes.append(g.lng)

    data["Latitude"] = latitudes
    data["Longitude"] = longitudes

    df = pd.DataFrame(data).dropna()
    return df


def get_admin_boundaries(place):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": place, "format": "json", "polygon_geojson": 1, "limit": 1}

    response = requests.get(url, params=params)
    data = response.json()

    if len(data) > 0:
        return data[0]["geojson"]
    else:
        return None


df = europe_capital()


def get_gdf_from_name(name):
    get_gdf = gpd.GeoDataFrame(
        geometry=[shape(get_admin_boundaries(name))], crs="epsg:4326"
    )

    return get_gdf


# Title and subtitle
st.title("Full-Page Dashboard with Folium Map and Plots")
st.subheader("Interactive map and plot options")


def display_map(df):

    df_cleaned = df.dropna(subset=["Latitude", "Longitude"])

    if not df_cleaned.empty:
        # Calculate the mean of Latitude and Longitude from cleaned DataFrame
        center_lat = df_cleaned["Latitude"].mean()
        center_lon = df_cleaned["Longitude"].mean()

        # Create Folium map with the calculated center
        m = folium.Map(location=[center_lat, center_lon], zoom_start=4)

        # Add markers for cities
        for index, row in df_cleaned.iterrows():
            folium.Marker([row["Latitude"], row["Longitude"]],
                          tooltip=row["City"],
                          popup=row["City"]).add_to(m)

        return m
    else:
        # If the DataFrame is empty after dropping NaN values, return None
        m= folium.Map(location=[50.9375, 6.9603], zoom_start=4) 
        return m


# Wide layout with two columns
col1, col2 = st.columns([2, 0.2])

# # Column 1 - Maps and Plots
# with col2:
#     # Plot options
#     st.subheader("Plot Options")
#     selected_plot = st.selectbox(
#         "Select a plot:", ["Bar Plot", "Pie Chart", "Scatter Plot"]
#     )

#     if selected_plot == "Bar Plot":
#         st.subheader("Bar Plot")
#         fig, ax = plt.subplots(figsize=(8, 6))
#         sns.barplot(x="City", y="Population", data=df, ax=ax)
#         plt.xlabel("City")
#         plt.ylabel("Population")
#         plt.title("Population by City")
#         st.pyplot(fig)

#     elif selected_plot == "Pie Chart":
#         st.subheader("Pie Chart")
#         fig, ax = plt.subplots(figsize=(8, 6))
#         ax.pie(df["Population"], labels=df["City"], autopct="%1.1f%%")
#         plt.title("Population Distribution")
#         st.pyplot(fig)

#     elif selected_plot == "Scatter Plot":
#         st.subheader("Scatter Plot")
#         fig, ax = plt.subplots(figsize=(8, 6))
#         sns.scatterplot(x="Longitude", y="Latitude", size="Population", data=df, ax=ax)
#         plt.xlabel("Longitude")
#         plt.ylabel("Latitude")
#         plt.title("Population Distribution on Map")
#         st.pyplot(fig)

        # Checkbox for Folium Heatmap


# Column 2 - Dropdown and Options
with col1:
    # Folium Map
    st.subheader("Folium Map")

    basemap_options = {
        "OpenStreetMap": folium.TileLayer("OpenStreetMap"),
        "OSM TopoMap": folium.TileLayer(
            "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
            name="OpenStreetMap",
            attr="Map data © OpenStreetMap contributors",
        ),
        "OSM_HOT_Map": folium.TileLayer(
            "https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png",
            max_zoom=19,
            attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Tiles style by <a href="https://www.hotosm.org/" target="_blank">Humanitarian OpenStreetMap Team</a> hosted by <a href="https://openstreetmap.fr/" target="_blank">OpenStreetMap France</a>',
        ),
        "OpenTopoMap": folium.TileLayer(
            "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
            max_zoom=17,
            attr='Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, <a href="http://viewfinderpanoramas.org">SRTM</a> | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a> (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)',
        ),
        "PublicTransport": folium.TileLayer(
            "https://tileserver.memomaps.de/tilegen/{z}/{x}/{y}.png",
            max_zoom=18,
            attr='Map <a href="https://memomaps.de/">memomaps.de</a> <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        ),
        "CartoDB Dark_Matter": folium.TileLayer("CartoDB dark_matter"),
        "CartoDB Positron": folium.TileLayer("CartoDB Positron"),
        "CartoDB Voyager": folium.TileLayer("CartoDB Voyager"),
        "ESRI NatGeoWorldMap": folium.TileLayer(
            "https://server.arcgisonline.com/ArcGIS/rest/services/NatGeo_World_Map/MapServer/tile/{z}/{y}/{x}",
            attr="ESRI NatGeoMap",
            name="ESRI NatGeoMap",
        ),
        "ESRI Imagery": folium.TileLayer(
            "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            attr="ESRI Imagery",
            name="ESRI Imagery",
        ),
        "CyclOSM": folium.TileLayer(
            "https://{s}.tile-cyclosm.openstreetmap.fr/cyclosm/{z}/{x}/{y}.png",
            attr='<a href="https://github.com/cyclosm/cyclosm-cartocss-style/releases" title="CyclOSM - Open Bicycle render">CyclOSM</a> | Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
            name="Cyle OSM",
        ),
    }

    # basemap_selection = st.selectbox("Select Basemap", list(basemap_options.keys()))

    # Create the map with selected basemap
    m = display_map(df)
    folium.plugins.Geocoder().add_to(m)
    # folium.plugins.Geocoder().add_to(m)
    # Figure(width="100%",height="70%").add_child(m)

    # folium.TileLayer(show=False).add_to(m)

    folium.TileLayer("CartoDB Voyager", show=False).add_to(m)

    fg = folium.FeatureGroup(name="openseamap", overlay=True, control=True).add_to(m)

    folium.TileLayer("CartoDB dark_matter", show=False).add_to(m)
    folium.TileLayer(
        "https://tileserver.memomaps.de/tilegen/{z}/{x}/{y}.png",
        max_zoom=18,
        attr='Map <a href="https://memomaps.de/">memomaps.de</a> <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        name="PublicTransport",
        show=False,
    ).add_to(m)
    folium.TileLayer(
        "https://server.arcgisonline.com/ArcGIS/rest/services/World_Terrain_Base/MapServer/tile/{z}/{y}/{x}",
        attr="Tiles &copy; Esri &mdash; Source: USGS, Esri, TANA, DeLorme, and NPS",
        name="EsriWorldTerrain",
        max_zoom=13,
        show=False,
    ).add_to(m)
    folium.TileLayer(
        "https://server.arcgisonline.com/ArcGIS/rest/services/NatGeo_World_Map/MapServer/tile/{z}/{y}/{x}",
        attr="ESRI NatGeoMap",
        name="ESRI NatGeoMap",
        show=False,
    ).add_to(m)
    folium.TileLayer(
        "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
        name="OSMTopoMap",
        attr="Map data © OpenStreetMap contributors",
        show=False,
    ).add_to(m)
    folium.TileLayer(
        "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="ESRI Imagery",
        name="ESRI Imagery",
        show=False,
    ).add_to(m)
    folium.TileLayer(
        "https://{s}.tile-cyclosm.openstreetmap.fr/cyclosm/{z}/{x}/{y}.png",
        attr='<a href="https://github.com/cyclosm/cyclosm-cartocss-style/releases" title="CyclOSM - Open Bicycle render">CyclOSM</a> | Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        name="Cyle OSM",
        show=False,
    ).add_to(m)
    folium.TileLayer(
        "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}",
        max_zoom=20,
        attr='Tiles courtesy of the <a href="https://usgs.gov/">U.S. Geological Survey</a>',
        name="USGS_Imagery",
        show=False,
    ).add_to(m)

    folium.TileLayer(
        "https://basemap.nationalmap.gov/arcgis/rest/services/USGSTopo/MapServer/tile/{z}/{y}/{x}",
        max_zoom=20,
        attr='Tiles courtesy of the <a href="https://usgs.gov/">U.S. Geological Survey</a>',
        name="USGS_TopoMap",
        show=False,
    ).add_to(m)
    # folium.TileLayer("NASAGIBS Blue Marble").add_to(m)
    # folium.TileLayer("OpenStreetMap",show=True).add_to(m)
    folium.TileLayer(
        "http://tiles.openseamap.org/seamark/{z}/{x}/{y}.png",
        name="OpenSeaMap",
        attr="Map data © OpenSeaMap contributors",
    ).add_to(fg)
    folium.LayerControl().add_to(m)

    folium.LatLngPopup().add_to(m)
    folium.plugins.MousePosition().add_to(m)
    folium.plugins.Fullscreen().add_to(m)

    folium.plugins.LocateControl(auto_start=False).add_to(m)
    folium.plugins.MeasureControl(
        position="topright",
        primary_length_unit="meters",
        secondary_length_unit="miles",
        primary_area_unit="sqmeters",
        secondary_area_unit="acres",
    ).add_to(m)
    folium.plugins.MiniMap().add_to(m)
    # folium.plugins.ScrollZoomToggler().add_to(m)
    # folium.plugins.PolyLineOffset(locations=[[df["Latitude"].mean(), df["Longitude"].mean()]]).add_to(m)

    # Enable drawing control
    draw_plugin = folium.plugins.Draw(export=True, edit_options={"edit": True})
    draw_plugin.add_to(m)
    # basemap_options[basemap_selection].add_to(m)

    # Add the draw control to the map
    m.add_child(draw_plugin)
    city_name = st.text_input("Enter the place name")
    if city_name:
        folium.GeoJson(get_gdf_from_name(city_name)).add_to(m)

    # Add markers for cities
    for index, row in df.iterrows():
        if row["City"] == "London":
            folium.plugins.BoatMarker(
                [row["Latitude"], row["Longitude"]],
                tooltip=row["City"],
                popup=row["City"],
                icon=folium.Icon(color="orange", icon="cloud"),
            ).add_to(m)
        elif row["City"] == "Paris":
            folium.Marker(
                [row["Latitude"], row["Longitude"]],
                tooltip=row["City"],
                popup=row["City"],
                icon=folium.Icon(color="red", icon="heart"),
            ).add_to(m)

        elif row["City"] == "Rome":
            folium.Marker(
                [row["Latitude"], row["Longitude"]],
                tooltip=row["City"],
                popup=row["City"],
                icon=folium.Icon(color="green", icon="heart"),
            ).add_to(m)
        elif row["City"] == "Vienna":
            folium.Marker(
                [row["Latitude"], row["Longitude"]],
                tooltip=row["City"],
                popup=row["City"],
                icon=folium.Icon(color="darkpurple", icon="heart"),
            ).add_to(m)
        else:
            folium.Marker(
                [row["Latitude"], row["Longitude"]],
                tooltip=row["City"],
                popup=row["City"],
            ).add_to(m)

    # # st.subheader("Folium Heatmap")
    show_heatmap = st.checkbox("Show Heatmap")
    if show_heatmap:
        folium.plugins.HeatMap(
            data=df[["Latitude", "Longitude", "Population"]], radius=15
        ).add_to(fg)
    # st.subheader("OpenSeaMap")
    # show_openseamap = st.checkbox("Show Openseamap")
    # if show_openseamap:
    #     folium.TileLayer('http://tiles.openseamap.org/seamark/{z}/{x}/{y}.png',
    #                  name='OpenSeaMap',
    #                  attr='Map data © OpenSeaMap contributors').add_to(m)
    # Shapefile/GeoJSON Upload
    """"""
    # st.subheader("Upload Shapefile or GeoJSON")
    # uploaded_file = st.file_uploader(
    #     "Upload a Shapefile or GeoJSON file", type=["shp", "geojson"]
    # )

    # if uploaded_file is not None:
    #     try:
    #         # Load the uploaded file using geopandas
    #         gdf = gpd.read_file(uploaded_file)

    #         # for i,v in gdf.iterrows():

    #         #     tooltip = "<br>".join([f"{col}: {v[col]}" for col in gdf.columns if col != 'geometry'])
    #         #     marker = folium.Marker(
    #         #         location=[v.geometry.centroid.y, v.geometry.centroid.x],
    #         #         tooltip=tooltip
    #         #     )
    #         #     #marker = folium.Marker(location=[v.geometry.centroid.y, v.geometry.centroid.x], tooltip=f"{v.STATE_CODE},<br>{v.GaPa_NaPa},<br>{v.DISTRICT}")
    #         #     marker.add_to(m)
    #         # Add the loaded shapefile/GeoJSON to the map
    #         def highlight_function(feature):
    #             return {
    #                 "fillColor": "#ff0000",
    #                 "color": "#000000",
    #                 "weight": 1,
    #                 "fillOpacity": 0.5,
    #             }

    #         jsond = folium.GeoJson(gdf, highlight_function=highlight_function).add_to(m)
    #         folium.GeoJsonPopup(
    #             fields=[col for col in gdf.columns if col != "geometry"]
    #         ).add_to(jsond)
    #         folium.GeoJsonTooltip(
    #             fields=[col for col in gdf.columns if col != "geometry"],
    #             style=(
    #                 """background-color: grey; color: white; font-family:"
    #      courier new; font-size: 24px; padding: 10px;"""
    #             ),aliases=['State Number:','District:','local unit:','local unit type:','Province:']
    #         ).add_to(jsond)

    #     except Exception as e:
    #         st.error(
    #             "Error loading file. Please make sure it is a valid Shapefile or GeoJSON."
    #         )
    @st.cache_data
    def get_temp_dir():
        return tempfile.TemporaryDirectory().name

    tempdir = get_temp_dir()

    def handle_upload(uploaded_file):

        if type(uploaded_file) == list and (
            any(".geojson" in file.name for file in uploaded_file)
            or any(".json" in file.name for file in uploaded_file)
        ):  # or any('.json' in file.name for file in uploaded_file)):
            # data = uploaded_file.read()
            for uploaded_file in uploaded_file:
                gdf = gpd.read_file(uploaded_file)

            # geojson_layer = folium.GeoJson(data)
            # geojson_layer.add_to(m)
            # Add the loaded shapefile/GeoJSON to the map
            def highlight_function(feature):
                return {
                    "fillColor": "#ff0000",
                    "color": "#000000",
                    "weight": 1,
                    "fillOpacity": 0.5,
                }

            jsond = folium.GeoJson(gdf, highlight_function=highlight_function).add_to(m)
            folium.GeoJsonPopup(
                fields=[col for col in gdf.columns if col != "geometry"]
            ).add_to(jsond)
            folium.GeoJsonTooltip(
                fields=[col for col in gdf.columns if col != "geometry"],
                style=(
                    """background-color: grey; color: white; font-family:"
        courier new; font-size: 24px; padding: 10px;"""
                ),
            ).add_to(jsond)

        elif type(uploaded_file) != list and (
            uploaded_file.name.endswith(".geojson")
            or uploaded_file.name.endswith(".json")
        ):
            gdf = gpd.read_file(uploaded_file)

            def highlight_function(feature):
                return {
                    "fillColor": "#ff0000",
                    "color": "#000000",
                    "weight": 1,
                    "fillOpacity": 0.5,
                }

            jsond = folium.GeoJson(gdf, highlight_function=highlight_function).add_to(m)
            folium.GeoJsonPopup(
                fields=[col for col in gdf.columns if col != "geometry"]
            ).add_to(jsond)
            folium.GeoJsonTooltip(
                fields=[col for col in gdf.columns if col != "geometry"],
                style=(
                    """background-color: grey; color: white; font-family:"
        courier new; font-size: 24px; padding: 10px;"""
                ),
            ).add_to(jsond)

        elif any(".shp" in file.name for file in uploaded_file):

            with tempfile.TemporaryDirectory() as temp_dir:

                # Save the uploaded shapefile to a temporary directory
                for uploaded_file in uploaded_file:
                    temp_file_path = os.path.join(temp_dir, uploaded_file.name)
                    print(temp_file_path)
                    if uploaded_file.name.endswith(".shp"):
                        shp_path = temp_file_path
                    with open(temp_file_path, "wb") as temp_file:
                        temp_file.write(uploaded_file.getbuffer())

                gdf = gpd.read_file(shp_path)
            os.environ["SHAPE_RESTORE_SHX"] = "YES"

            print(shp_path)

            #############################################################################
            # with tempfile.TemporaryDirectory() as temp_dir:
            #     # Save the uploaded shapefile to a temporary directory
            #     # for ext in [".shp", ".shx", ".dbf", ".prj"]:
            #     temp_file_path = os.path.join(
            #         temp_dir, uploaded_file.name
            #     )
            #     with open(temp_file_path, "wb") as temp_file:
            #         temp_file.write(uploaded_file.getvalue())

            #     os.environ["SHAPE_RESTORE_SHX"] = "YES"
            #############################################################################

            print(gdf.head())
            # Assign a CRS to the GeoDataFrame if it is not already defined
            if gdf.crs is None:
                gdf.crs = "EPSG:4326"
            # Convert the shapefile to GeoJSON format
            gdf = gdf.to_crs("EPSG:4326")

            # geojson_layer = folium.GeoJson(json.loads(geojson_data))
            def highlight_function(feature):
                return {
                    "fillColor": "#ff0000",
                    "color": "#000000",
                    "weight": 1,
                    "fillOpacity": 0.5,
                }

            jsond = folium.GeoJson(gdf, highlight_function=highlight_function).add_to(m)
            folium.GeoJsonPopup(
                fields=[col for col in gdf.columns if col != "geometry"]
            ).add_to(jsond)
            folium.GeoJsonTooltip(
                fields=[col for col in gdf.columns if col != "geometry"],
                style=(
                    """background-color: grey; color: white; font-family:"
        courier new; font-size: 24px; padding: 10px;"""
                ),
            ).add_to(jsond)
        # geojson_layer.add_to(m)

    # Add the file upload button to the Streamlit app
    st.sidebar.header("Upload Shapefile or GeoJSON")
    uploaded_file = st.sidebar.file_uploader(
        "Upload",
        type=["geojson", "shx", "prj", "dbf", "shp", "json"],
        accept_multiple_files=True,
        key="upload",
    )
    if uploaded_file is not None:
        handle_upload(uploaded_file)

    # st_folium(m, width=900, height=600)
    output = folium_static(m, width=1500, height=900)

    # #Save the drawn object
    # drawn_json = draw_plugin.last_draw
    # drawn_type = drawn_json['type']
    # coordinates = drawn_json['coordinates']

    # if drawn_type == 'LineString':
    #     line = LineString(coordinates)
    #     st.write("Line Object:", line)
    #     # You can save the line object or perform other operations with it

    # elif drawn_type == 'Polygon':
    #     polygon = Polygon(coordinates)
    #     st.write("Polygon Object:", polygon)
    #     # You can save the polygon object or perform other operations with it

    # elif drawn_type == 'Point':
    #     point = Point(coordinates)
    #     st.write("Point Object:", point)
    #     # You can save the point object or perform other operations with it

    # if st.button("Save Object"):
    #     # Perform save operation here
    #     st.write("Object saved successfully!")

# Add any other components or sections as needed.
