import os
import tempfile
import streamlit as st
import folium
from streamlit_folium import folium_static, st_folium
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import geocoder
from shapely.geometry import LineString, Polygon, Point
import geopandas as gpd

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

df = pd.DataFrame(data)

# Streamlit configuration
st.set_page_config(page_title="Dashboard with Folium Map and Plots", layout="wide")

# Title and subtitle
st.title("Full-Page Dashboard with Folium Map and Plots")
st.subheader("Interactive map and plot options")

# Wide layout with two columns
col1, col2 = st.columns([2, 0.8])

# Column 1 - Maps and Plots
with col2:
    # Plot options
    st.subheader("Plot Options")
    selected_plot = st.selectbox(
        "Select a plot:", ["Bar Plot", "Pie Chart", "Scatter Plot"]
    )

    if selected_plot == "Bar Plot":
        st.subheader("Bar Plot")
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.barplot(x="City", y="Population", data=df, ax=ax)
        plt.xlabel("City")
        plt.ylabel("Population")
        plt.title("Population by City")
        st.pyplot(fig)

    elif selected_plot == "Pie Chart":
        st.subheader("Pie Chart")
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.pie(df["Population"], labels=df["City"], autopct="%1.1f%%")
        plt.title("Population Distribution")
        st.pyplot(fig)

    elif selected_plot == "Scatter Plot":
        st.subheader("Scatter Plot")
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.scatterplot(x="Longitude", y="Latitude", size="Population", data=df, ax=ax)
        plt.xlabel("Longitude")
        plt.ylabel("Latitude")
        plt.title("Population Distribution on Map")
        st.pyplot(fig)

        # Checkbox for Folium Heatmap


# Column 2 - Dropdown and Options
with col1:
    # Folium Map
    st.subheader("Folium Map")

    basemap_options = {
        "OpenStreetMap": folium.TileLayer("OpenStreetMap"),
        "CartoDB Dark_Matter": folium.TileLayer("CartoDB dark_matter"),
        "Stamen Terrain": folium.TileLayer("Stamen Terrain"),
        "ESRI Imagery": folium.TileLayer(
            "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            attr="ESRI Imagery",
            name="ESRI Imagery",
        ),
    }

    basemap_selection = st.selectbox("Select Basemap", list(basemap_options.keys()))

    # Create the map with selected basemap
    m = folium.Map(
        location=[df["Latitude"].mean(), df["Longitude"].mean()], zoom_start=4
    )
    folium.LatLngPopup().add_to(m)
    folium.plugins.MousePosition().add_to(m)
    folium.plugins.Fullscreen().add_to(m)
    # Enable drawing control
    draw_plugin = folium.plugins.Draw(export=False)
    draw_plugin.add_to(m)
    basemap_options[basemap_selection].add_to(m)

    # Add the draw control to the map
    m.add_child(draw_plugin)

    # Add markers for cities
    for index, row in df.iterrows():
        if row["City"] == "London":
            folium.Marker(
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

    # st.subheader("Folium Heatmap")
    show_heatmap = st.checkbox("Show Heatmap")
    if show_heatmap:
        folium.plugins.HeatMap(
            data=df[["Latitude", "Longitude", "Population"]], radius=15
        ).add_to(m)

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

    def handle_upload(uploaded_file):
        if uploaded_file.name.endswith(".geojson") or uploaded_file.name.endswith(
            ".json"
        ):
            # data = uploaded_file.read()
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
        elif uploaded_file.name.endswith(".shp"):
            with tempfile.TemporaryDirectory() as temp_dir:
                # Save the uploaded shapefile to a temporary directory
                # for ext in [".shp", ".shx", ".dbf", ".prj"]:
                temp_file_path = os.path.join(
                    temp_dir, uploaded_file.name
                )
                with open(temp_file_path, "wb") as temp_file:
                    temp_file.write(uploaded_file.getvalue())
                    
                os.environ["SHAPE_RESTORE_SHX"] = "YES"
                gdf = gpd.read_file(temp_file_path)

                # Copy the shapefile components to a different location
                # dest_dir = "./temp_shapefile"
                # os.makedirs(dest_dir, exist_ok=True)
                # for ext in [".shp", ".shx", ".dbf", ".prj", ".csv"]:
                #     temp_file_path = os.path.join(
                #         temp_dir, uploaded_file.name.replace(".shp", ext)
                #     )
                #     dest_file_path = os.path.join(
                #         dest_dir, uploaded_file.name.replace(".shp", ext)
                #     )
                #     shutil.copy(temp_file_path, dest_file_path)

                # Set SHAPE_RESTORE_SHX config option to YES
            

              # gpd.read_file(dest_dir)

            # print(temp_path)

            # Read the shapefile using geopandas

            # gdf = gpd.read_file(
            #     shp_path,
            #     shx=shx_path,
            #     dbf=dbf_path,
            #     prj=prj_path,
            #     usecols="all",
            #     encoding="utf-8",
            # )
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
        type=["geojson", "shp", "json"],
        accept_multiple_files=False,
        key="upload",
    )
    if uploaded_file is not None:
        handle_upload(uploaded_file)

    # st_folium(m, width=900, height=600)
    folium_static(m)

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
