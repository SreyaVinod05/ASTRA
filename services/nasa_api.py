
import requests
import pandas as pd
import streamlit as st

NASA_FEED_URL = "https://api.nasa.gov/neo/rest/v1/feed"
NASA_LOOKUP_URL = "https://api.nasa.gov/neo/rest/v1/neo"


@st.cache_data(ttl=1800)
def fetch_asteroids(start_date, end_date, api_key):

    params = {
        "start_date": start_date,
        "end_date": end_date,
        "api_key": api_key
    }

    response = requests.get(
        NASA_FEED_URL,
        params=params,
        timeout=30
    )

    response.raise_for_status()
    data = response.json()

    asteroid_list = []

    for approach_date, objects in data.get("near_earth_objects", {}).items():

        for asteroid in objects:

            approaches = asteroid.get("close_approach_data", [])

            approach = next(
                (
                    item for item in approaches
                    if item.get("close_approach_date") == approach_date
                ),
                None
            )

            if approach is None:
                continue

            diameter = asteroid.get(
                "estimated_diameter", {}
            ).get("kilometers", {})

            miss_distance = approach.get("miss_distance", {})
            relative_velocity = approach.get("relative_velocity", {})

            min_diameter = diameter.get("estimated_diameter_min")
            max_diameter = diameter.get("estimated_diameter_max")
            distance = miss_distance.get("kilometers")
            velocity = relative_velocity.get("kilometers_per_second")

            if any(value is None for value in [
                min_diameter, max_diameter, distance, velocity
            ]):
                continue

            asteroid_list.append({
                "Name": asteroid.get("name", "Unknown"),
                "ID": str(asteroid.get("id", "")),
                "Approach Date": approach_date,
                "Min Diameter (km)": float(min_diameter),
                "Max Diameter (km)": float(max_diameter),
                "Distance (km)": float(distance),
                "Velocity (km/s)": float(velocity),
                "Orbiting Body": approach.get("orbiting_body", "Unknown"),
                "Absolute Magnitude (H)": asteroid.get("absolute_magnitude_h"),
                "NASA URL": asteroid.get("nasa_jpl_url", ""),
                "Hazardous": asteroid.get(
                    "is_potentially_hazardous_asteroid", False
                )
            })

    return pd.DataFrame(asteroid_list)


@st.cache_data(ttl=1800)
def fetch_asteroid_details(asteroid_id, api_key):

    url = f"{NASA_LOOKUP_URL}/{asteroid_id}"

    response = requests.get(
        url,
        params={"api_key": api_key},
        timeout=30
    )

    response.raise_for_status()

    return response.json()
