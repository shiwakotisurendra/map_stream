import streamlit as st
import folium
from streamlit_folium import folium_static
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import geocoder
from shapely.geometry import LineString, Polygon, Point

# Sample data for the capital cities of Europe
data = {
    'City': ['London', 'Paris', 'Madrid', 'Berlin', 'Rome', 'Athens', 'Vienna', 'Amsterdam'],
    'Population': [8961989, 2140526, 3266126, 3769495, 2872800, 6640466, 1911191, 873555]
}

# Retrieve latitude and longitude coordinates for each city
latitudes = []
longitudes = []
for city in data['City']:
    g = geocoder.osm(city)
    latitudes.append(g.lat)
    longitudes.append(g.lng)

data['Latitude'] = latitudes
data['Longitude'] = longitudes

df = pd.DataFrame(data)

# Streamlit configuration
st.set_page_config(page_title="Dashboard with Folium Map and Plots",layout="wide")

# Title and subtitle
st.title("Full-Page Dashboard with Folium Map and Plots")
st.subheader("Interactive map and plot options")

# Wide layout with two columns
col1, col2 = st.columns([2, 0.8])

# Column 1 - Maps and Plots
with col2:

    # Plot options
    st.subheader("Plot Options")
    selected_plot = st.selectbox("Select a plot:", ["Bar Plot", "Pie Chart", "Scatter Plot"])

    if selected_plot == "Bar Plot":
        st.subheader("Bar Plot")
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.barplot(x='City', y='Population', data=df, ax=ax)
        plt.xlabel('City')
        plt.ylabel('Population')
        plt.title('Population by City')
        st.pyplot(fig)

    elif selected_plot == "Pie Chart":
        st.subheader("Pie Chart")
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.pie(df['Population'], labels=df['City'], autopct='%1.1f%%')
        plt.title('Population Distribution')
        st.pyplot(fig)

    elif selected_plot == "Scatter Plot":
        st.subheader("Scatter Plot")
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.scatterplot(x='Longitude', y='Latitude', size='Population', data=df, ax=ax)
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.title('Population Distribution on Map')
        st.pyplot(fig)

        # Checkbox for Folium Heatmap


# Column 2 - Dropdown and Options
with col1:
# Folium Map
    st.subheader("Folium Map")


    basemap_options = {
        'OpenStreetMap': folium.TileLayer('OpenStreetMap'),
        'CartoDB Dark_Matter': folium.TileLayer('CartoDB dark_matter'),
        'Stamen Terrain': folium.TileLayer('Stamen Terrain'),
        'ESRI Imagery': folium.TileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', attr='ESRI Imagery', name='ESRI Imagery')
    }

    basemap_selection = st.selectbox("Select Basemap", list(basemap_options.keys()))

    # Create the map with selected basemap
    m = folium.Map(location=[df['Latitude'].mean(), df['Longitude'].mean()], zoom_start=4)
        # Enable drawing control
    draw_plugin = folium.plugins.Draw(export=True)
    draw_plugin.add_to(m)
    basemap_options[basemap_selection].add_to(m)



    # Add the draw control to the map
    m.add_child(draw_plugin)

    # Add markers for cities
    for index, row in df.iterrows():
        if row['City'] == 'London':
            folium.Marker([row['Latitude'], row['Longitude']], popup=row['City'],
                          icon=folium.Icon(color='blue', icon='cloud')).add_to(m)
        elif row['City'] == 'Paris':
            folium.Marker([row['Latitude'], row['Longitude']], popup=row['City'],
                          icon=folium.Icon(color='red', icon='heart')).add_to(m)
        
        elif row['City'] == 'Rome':
            folium.Marker([row['Latitude'], row['Longitude']], popup=row['City'],
                          icon=folium.Icon(color='green', icon='heart')).add_to(m)
        elif row['City'] == 'Vienna':
            folium.Marker([row['Latitude'], row['Longitude']], popup=row['City'],
                          icon=folium.Icon(color='grey', icon='heart')).add_to(m)
        else:
            folium.Marker([row['Latitude'], row['Longitude']], popup=row['City']).add_to(m)

    #st.subheader("Folium Heatmap")
    show_heatmap = st.checkbox("Show Heatmap")
    if show_heatmap:
        folium.plugins.HeatMap(data=df[['Latitude', 'Longitude', 'Population']], radius=15).add_to(m)



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