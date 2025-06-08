import streamlit as st
import pandas as pd
import random
from geopy.distance import geodesic
import plotly.graph_objects as go
import base64

# Set up the Streamlit app layout to wide
st.set_page_config(layout="wide")

# Function to play background sound continuously without controls
def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio autoplay loop>
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)

# Load country data
country_data = pd.read_csv('country_data.csv')

# Start page
if 'show_game' not in st.session_state:
    st.session_state.show_game = False

if not st.session_state.show_game:
    st.markdown('<h1 style="color: black;">Welcome to the Globle Guessing Game!</h1>', unsafe_allow_html=True)
    st.markdown('<h2 style="color: black;">Can you guess the mystery country based on your distance from it?</h2>', unsafe_allow_html=True)
    st.markdown('<h3 style="color: black;">Few Instructions on How to Play</h1>', unsafe_allow_html=True)
    st.markdown('<h4 style="color: black;">     -->You have only 7 guesses.', unsafe_allow_html=True)
    st.markdown('<h4 style="color: black;">     -->The first letter of the name should be capital.', unsafe_allow_html=True)
    st.markdown('<h4 style="color: black;">     -->You can rotate the globe using your cursor.', unsafe_allow_html=True)
    st.markdown('<h4 style="color: black;">     -->Double click the buttons if they don\'t work the first time.', unsafe_allow_html=True)
    st.markdown('<h4 style="color: black;">Press to start the game', unsafe_allow_html=True)
    st.markdown('<h4 style="color: black;">Have Fun Globling!!', unsafe_allow_html=True)
    if st.button("Start Game"):
        st.session_state.show_game = True
else:
    # Play background sound
    background_sound_path = 'BackGroundSound.mp3'  # Replace with your file path
    autoplay_audio(background_sound_path)

# Center the title at the top of the page with custom colors
st.markdown(
    """
    <style>
    .custom-title {
        font-size: 3em;
        font-weight: bold;
        text-align: center;
        margin-top: 20px;
        margin-bottom: 20px;
    }
    /* Set the background image */
    .stApp {
        background-image: url("https://media.istockphoto.com/id/500548022/vector/cartoon-flat-seamless-landscape.jpg?s=612x612&w=0&k=20&c=L2DXn9LKDr4K-Kz7jr9feeltlVt9TSSWiBuqUsPY-54="); /* Replace with your image URL */
        background-size: cover; /* Cover the entire background */
        background-repeat: no-repeat; /* Prevent repeating */
        background-attachment: fixed; /* Keep the background fixed */
        background-position: center; /* Center the background */
    }
    .custom-label {
        color: black;
        font-size: 1.5em;
        font-weight: bold;
        background-color: rgba(255, 200, 255, 0.5);  /* Optional: Adjust font size if desired */
        border-radius: 3px;
    }
    .custom-label2 {
        color: black;
        font-size: 1.2em;  /* Optional: Adjust font size if desired */
        background-color: rgba(255, 200, 255, 0.5)
    }
    .custom-hint {
        color: black; /* Bright color for hints */
        font-weight: bold; /* Make it bold */
        font-size: 1.2em; /* Slightly larger font size */
        background-color: rgba(255, 255, 155, 0.8); /* Light background for contrast */
        padding: 5px; /* Padding for better visibility */
        border-radius: 5px; /* Rounded corners */
    }
    .custom-success {
        color: green; /* Bright color for hints */
        font-weight: bold; /* Make it bold */
        font-size: 1.2em; /* Slightly larger font size */
        background-color: rgba(155, 255, 155, 0.8); /* Light background for contrast */
        padding: 5px; /* Padding for better visibility */
        border-radius: 5px; /* Rounded corners */
    }
    .custom-info {
        color: black; /* Bright blue for info messages */
        font-weight: bold; /* Make it bold */
        font-size: 1.2em; /* Slightly larger font size */
        background-color: rgba(155, 155, 255, 0.8); /* Light background for contrast */
        padding: 5px; /* Padding for better visibility */
        border-radius: 5px; /* Rounded corners */
    }
    .custom-warning {
        color: black; /* Bright red for warnings */
        font-weight: bold; /* Make it bold */
        font-size: 1.2em; /* Slightly larger font size */
        background-color: rgba(255, 155, 155, 0.8); /* Light background for contrast */
        padding: 5px; /* Padding for better visibility */
        border-radius: 5px; /* Rounded corners */
    }
    </style>
    <div class="custom-title">
        <span style="color: black;">G</span>
        <span style="color: blue;">L</span>
        <span style="color: green;">O</span>
        <span style="color: red;">B</span>
        <span style="color: blue;">L</span>
        <span style="color: black;">E</span>
        <span style="color: green;">!!</span>
    </div>
    """,
    unsafe_allow_html=True
)

# Initialize session state variables if they don't exist
if 'mystery_country' not in st.session_state:
    st.session_state.mystery_country = random.choice(country_data['Country'].tolist())
    st.session_state.guesses = []
    st.session_state.show_markers = True  # Initialize marker visibility
    st.session_state.last_guess_coords = (0, 0)

# Function to create the 3D globe visualization
def create_globe(show_markers, lon=None, lat=None):
    fig = go.Figure()

    # Add land and water as a static background layer
    fig.update_geos(
        projection_type="orthographic",
        showland=True,
        landcolor='green',
        oceancolor='lightblue',
        showocean=True,
        showcountries=True,
        projection_rotation=dict(lon=lon if lon else 0, lat=lat if lat else 0)
    )

    # Prepare marker colors based on guesses
    marker_colors = ['rgba(255, 255, 255, 1)'] * len(country_data)

    for guess, distance in st.session_state.guesses:
        if guess == st.session_state.mystery_country:
            idx = country_data[country_data['Country'] == guess].index[0]
            marker_colors[idx] = 'rgba(255, 0, 0, 0.5)'
        else:
            idx = country_data[country_data['Country'] == guess].index[0]
            max_distance = 10000
            color_value = max_distance / distance
            r = int(80 * color_value)
            marker_colors[idx] = f'rgba({r}, 0, 0, 1)'

    # Add markers only if show_markers is True
    fig.add_trace(go.Scattergeo(
        lon=country_data['Longitude'],
        lat=country_data['Latitude'],
        text=country_data['Country'],
        mode='markers' if show_markers else 'none',
        marker=dict(
            size=7,
            color=marker_colors if show_markers else ['rgba(0, 0, 0, 0)'] * len(country_data),
        ),
        hoverinfo='text'
    ))

    # Background image
    fig.update_layout(
        images=[dict(
            source="https://images.pexels.com/photos/957061/milky-way-starry-sky-night-sky-star-957061.jpeg?cs=srgb&dl=pexels-felixmittermeier-957061.jpg&fm=jpg",
            xref="paper", yref="paper",
            x=0, y=0,
            sizex=1, sizey=1,
            xanchor="left", yanchor="bottom",
            opacity=0.5,
            layer="below")],
        margin=dict(l=0, r=0, t=0, b=0),
        geo=dict(showframe=False)
    )

    return fig

# Function to convert kilometers to miles
def convert_km_to_miles(km):
    return km * 0.621371

# Maximum number of guesses allowed
MAX_GUESSES = 7

# Create two columns: one for guessing input and one for the globe
col1, col2 = st.columns([1, 2])

# Left column for input and guesses
with col1:
    st.markdown('<div class="custom-label">Enter your guess!!:</div>', unsafe_allow_html=True)
    guess = st.text_input("")

    if len(st.session_state.guesses) >= MAX_GUESSES:
        answer = f"The Mystery country was {st.session_state.mystery_country}."
        st.markdown(f'<div class="custom-info">{answer}</div>', unsafe_allow_html=True)
        st.markdown('<div class="custom-warning">Maximum guesses reached! Please restart the game.</div>', unsafe_allow_html=True)
    else:
        if st.button("Submit Guess"):
            if guess in country_data['Country'].values:
                if guess in [g[0] for g in st.session_state.guesses]:
                    st.markdown('<div class="custom-warning">You\'ve already guessed that country!</div>', unsafe_allow_html=True)
                else:
                    lat_long_mystery = (
                        country_data[country_data['Country'] == st.session_state.mystery_country]['Latitude'].values[0],
                        country_data[country_data['Country'] == st.session_state.mystery_country]['Longitude'].values[0]
                    )
                    lat_long_guess = (
                        country_data[country_data['Country'] == guess]['Latitude'].values[0],
                        country_data[country_data['Country'] == guess]['Longitude'].values[0]
                    )
                    distance = geodesic(lat_long_mystery, lat_long_guess).kilometers

                    st.session_state.guesses.append((guess, distance))
                    st.session_state.last_guess_coords = lat_long_guess

                    if guess == st.session_state.mystery_country:
                        st.markdown('<div class="custom-success">Correct! You guessed the country! </div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="custom-info">Please restart the game</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="custom-hint">Distance to mystery: {distance:.2f} km. Try again!</div>', unsafe_allow_html=True)
                        if len(st.session_state.guesses) == 4:
                            mystery_country_row = country_data[country_data['Country'] == st.session_state.mystery_country]
                            hint = f"Hint: The mystery country is in {mystery_country_row['Continent'].values[0]}."
                            st.markdown(f'<div class="custom-info">{hint}</div>', unsafe_allow_html=True)

            else:
                st.markdown('<div class="custom-warning">Country not found in the list!</div>', unsafe_allow_html=True)

    st.markdown('<div class="custom-label">Your guesses so far:</div>', unsafe_allow_html=True)
    for g, dist in st.session_state.guesses:
        st.write(f'<div class="custom-label2"> - {g}: {dist:.2f} km away</div>', unsafe_allow_html=True)

    if st.button("Miles Converter"):
        for g, dist in st.session_state.guesses:
            miles = convert_km_to_miles(dist)
            st.write(f'<div class="custom-label2"> - {g}: {miles:.2f} miles away</div>', unsafe_allow_html=True)

    if st.button("Restart Game"):
        st.session_state.mystery_country = random.choice(country_data['Country'].tolist())
        st.session_state.guesses = []

# Right column for the globe
with col2:
    lat, lon = st.session_state.last_guess_coords
    st.plotly_chart(create_globe(st.session_state.show_markers, lon=lon, lat=lat), use_container_width=True)
    if st.button("Hide Markers"):
        st.session_state.show_markers = not st.session_state.show_markers 