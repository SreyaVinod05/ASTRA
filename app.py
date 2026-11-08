
from services.nasa_api import (
    fetch_asteroids,
    fetch_asteroid_details
)
import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import streamlit.components.v1 as components

from datetime import date, timedelta


# =====================================================
# 1. PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="ASTRA | NASA Asteroid Tracker",
    page_icon="🪐",
    layout="wide"
)

NASA_FEED_URL = "https://api.nasa.gov/neo/rest/v1/feed"
NASA_LOOKUP_URL = "https://api.nasa.gov/neo/rest/v1/neo"


# =====================================================
# 2. DASHBOARD DESIGN
# =====================================================

st.markdown("""
<style>

.stApp {
    background-color: #0b1020;
    color: #ffffff;
}

[data-testid="stMetric"] {
    background-color: #17233d;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #30466b;
}

h1 {
    color: #8ab4ff;
}

h2, h3 {
    color: #ffffff;
}

[data-testid="stSidebar"] {
    background-color: #151c2e;
}

.stButton button {
    border-radius: 8px;
}

</style>
""", unsafe_allow_html=True)


# =====================================================
# 2A. ASTRA LANDING PAGE + 3D SPACE SCENE
# =====================================================

if "astra_page" not in st.session_state:
    st.session_state.astra_page = "home"

def render_astra_landing_page():
    st.markdown("""
    <style>
    .stApp {
        background:
            radial-gradient(ellipse at 50% 15%, rgba(30, 64, 115, .38), transparent 48%),
            linear-gradient(180deg, #050914 0%, #091326 55%, #050914 100%);
    }
    .astra-eyebrow {
        color: #75c9ff;
        letter-spacing: .32em;
        font-size: .78rem;
        font-weight: 700;
        text-align: center;
        margin-top: 1.4rem;
    }
    .astra-hero-title {
        color: #f3f7ff;
        text-align: center;
        font-size: clamp(3.2rem, 9vw, 6.5rem);
        line-height: 1;
        letter-spacing: .16em;
        font-weight: 800;
        margin: .35rem 0 .8rem 0;
        text-shadow: 0 0 32px rgba(80, 160, 255, .32);
    }
    .astra-hero-subtitle {
        color: #b6c8e6;
        text-align: center;
        font-size: clamp(1rem, 2vw, 1.25rem);
        max-width: 760px;
        margin: 0 auto 1.3rem auto;
    }
    .astra-small-note {
        color: #8298ba;
        text-align: center;
        font-size: .82rem;
        letter-spacing: .08em;
    }
    div.stButton > button[kind="primary"] {
        background: linear-gradient(100deg, #1769aa, #4b8df8);
        color: white;
        border: 1px solid rgba(151, 207, 255, .55);
        border-radius: 999px;
        padding: .85rem 2rem;
        font-weight: 800;
        letter-spacing: .12em;
        box-shadow: 0 0 28px rgba(55, 140, 255, .28);
        transition: all .2s ease;
    }
    div.stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 0 38px rgba(55, 140, 255, .5);
        border-color: #b5e2ff;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="astra-eyebrow">NEAR-EARTH OBJECT MONITORING</div>', unsafe_allow_html=True)
    st.markdown('<div class="astra-hero-title">ASTRA</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="astra-hero-subtitle">'
        'Explore the space around Earth. Track asteroid approaches, '
        'study orbital data, and explore insights powered by NASA.'
        '</div>',
        unsafe_allow_html=True
    )

    # Three.js scene runs inside an isolated HTML component.
    # If the CDN is unavailable, the rest of the dashboard still works.
    three_d_scene = r"""
    <div id="astra-scene" style="width:100%;height:410px;position:relative;overflow:hidden;background:transparent;">
      <div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;color:#9bb9df;font:14px sans-serif;letter-spacing:2px;">
        INITIALIZING 3D SPACE...
      </div>
    </div>
    <script type="module">
      import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js';

      const host = document.getElementById('astra-scene');
      host.innerHTML = '';

      const scene = new THREE.Scene();
      const camera = new THREE.PerspectiveCamera(42, host.clientWidth / host.clientHeight, 0.1, 100);
      camera.position.set(0, 0, 6.3);

      const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      renderer.setSize(host.clientWidth, host.clientHeight);
      renderer.outputColorSpace = THREE.SRGBColorSpace;
      host.appendChild(renderer.domElement);

      scene.add(new THREE.AmbientLight(0x9bb8e8, 1.35));
      const keyLight = new THREE.DirectionalLight(0xc5e2ff, 3.0);
      keyLight.position.set(-3, 4, 5);
      scene.add(keyLight);
      const rimLight = new THREE.PointLight(0x398cff, 18, 18);
      rimLight.position.set(3, -1, -2);
      scene.add(rimLight);

      // Procedurally roughen an icosphere to create an asteroid-like surface.
      const geometry = new THREE.IcosahedronGeometry(1.42, 5);
      const position = geometry.attributes.position;
      for (let i = 0; i < position.count; i++) {
        const x = position.getX(i), y = position.getY(i), z = position.getZ(i);
        const n = Math.sin(x * 8.1 + y * 5.7) * Math.cos(z * 7.4 + x * 3.2);
        const m = Math.sin(y * 13.0 - z * 8.0) * 0.035;
        const scale = 1 + n * 0.055 + m;
        position.setXYZ(i, x * scale, y * scale, z * scale);
      }
      geometry.computeVertexNormals();

      const asteroidMaterial = new THREE.MeshStandardMaterial({
        color: 0x777f8d, roughness: 0.96, metalness: 0.08,
        flatShading: false
      });
      const asteroid = new THREE.Mesh(geometry, asteroidMaterial);
      asteroid.rotation.set(0.4, 0.2, 0.1);
      scene.add(asteroid);

      // Small crater-like details on the visible surface.
      const craterMaterial = new THREE.MeshStandardMaterial({
        color: 0x343d4b, roughness: 1, metalness: 0
      });
      const craterGroup = new THREE.Group();
      for (let i = 0; i < 24; i++) {
        const crater = new THREE.Mesh(
          new THREE.SphereGeometry(0.07 + (i % 4) * 0.018, 12, 10),
          craterMaterial
        );
        const phi = Math.acos(-1 + (2 * i) / 24);
        const theta = Math.sqrt(24 * Math.PI) * phi;
        const r = 1.405;
        crater.position.set(
          r * Math.sin(phi) * Math.cos(theta),
          r * Math.cos(phi),
          r * Math.sin(phi) * Math.sin(theta)
        );
        crater.lookAt(0, 0, 0);
        crater.scale.set(1, 0.35, 1);
        craterGroup.add(crater);
      }
      asteroid.add(craterGroup);

      // Orbit arc.
      const orbitPoints = [];
      for (let i = 0; i <= 180; i++) {
        const a = (i / 180) * Math.PI * 2;
        orbitPoints.push(new THREE.Vector3(Math.cos(a) * 2.18, Math.sin(a) * 0.72, 0));
      }
      const orbitGeometry = new THREE.BufferGeometry().setFromPoints(orbitPoints);
      const orbit = new THREE.LineLoop(
        orbitGeometry,
        new THREE.LineBasicMaterial({ color: 0x398cff, transparent: true, opacity: 0.48 })
      );
      orbit.rotation.set(0.7, 0.25, -0.2);
      scene.add(orbit);

      // Star particles.
      const starGeometry = new THREE.BufferGeometry();
      const starPositions = [];
      for (let i = 0; i < 850; i++) {
        starPositions.push(
          (Math.random() - 0.5) * 22,
          (Math.random() - 0.5) * 13,
          (Math.random() - 0.5) * 12 - 2
        );
      }
      starGeometry.setAttribute('position', new THREE.Float32BufferAttribute(starPositions, 3));
      const stars = new THREE.Points(
        starGeometry,
        new THREE.PointsMaterial({ color: 0xb9d8ff, size: 0.018, transparent: true, opacity: 0.8 })
      );
      scene.add(stars);

      let pointerX = 0, pointerY = 0;
      host.addEventListener('pointermove', (event) => {
        const rect = host.getBoundingClientRect();
        pointerX = ((event.clientX - rect.left) / rect.width - 0.5) * 0.28;
        pointerY = ((event.clientY - rect.top) / rect.height - 0.5) * 0.18;
      });

      function animate() {
        requestAnimationFrame(animate);
        asteroid.rotation.y += 0.0028;
        asteroid.rotation.x += 0.0007;
        asteroid.rotation.y += pointerX * 0.0005;
        asteroid.rotation.x += pointerY * 0.0005;
        orbit.rotation.z += 0.00035;
        stars.rotation.y += 0.00008;
        renderer.render(scene, camera);
      }
      animate();

      const resizeObserver = new ResizeObserver(() => {
        const width = host.clientWidth;
        const height = host.clientHeight;
        camera.aspect = width / height;
        camera.updateProjectionMatrix();
        renderer.setSize(width, height);
      });
      resizeObserver.observe(host);
    </script>
    """
    components.html(three_d_scene, height=425, scrolling=False)

    st.markdown(
        '<div class="astra-small-note">NASA NEOWS DATA  &nbsp; • &nbsp; '
        'ORBITAL INSIGHTS  &nbsp; • &nbsp; SPACE EXPLORATION</div>',
        unsafe_allow_html=True
    )
    st.write("")
    left, center, right = st.columns([1, 1.25, 1])
    with center:
        if st.button("🚀  EXPLORE ASTRA", type="primary", use_container_width=True):
            st.session_state.astra_page = "dashboard"
            st.rerun()

    st.markdown(
        '<div class="astra-small-note" style="margin-top:1.5rem;">'
        'AN EDUCATIONAL ASTEROID MONITORING EXPERIENCE'
        '</div>',
        unsafe_allow_html=True
    )


if st.session_state.astra_page == "home":
    render_astra_landing_page()
    st.stop()



# 


# =====================================================
# 5. SIDEBAR
# =====================================================

st.sidebar.title("🪐 ASTRA")

st.sidebar.caption(
    "NASA Near-Earth Asteroid Monitoring System"
)

if st.sidebar.button("← Back to ASTRA Home", use_container_width=True):
    st.session_state.astra_page = "home"
    st.rerun()

st.sidebar.markdown("---")

api_key = st.sidebar.text_input(
    "NASA API Key",
    value="DEMO_KEY",
    type="password",
    help="Enter your personal NASA API key or use DEMO_KEY."
)

st.sidebar.markdown("---")

st.sidebar.subheader("📅 Date Selection")

today = date.today()

date_range = st.sidebar.date_input(
    "Select asteroid approach dates",
    value=(
        today - timedelta(days=6),
        today
    ),
    max_value=today + timedelta(days=7)
)

st.sidebar.caption(
    "NASA's feed supports a maximum 7-day date interval."
)

if st.sidebar.button("🔄 Refresh NASA Data", use_container_width=True):

    fetch_asteroids.clear()
    fetch_asteroid_details.clear()

    st.rerun()

st.sidebar.markdown("---")

st.sidebar.info(
    "Data source: NASA Near Earth Object Web Service (NeoWs)"
)


# =====================================================
# 6. MAIN HEADER
# =====================================================

st.title("🪐 ASTRA")

st.subheader(
    "Near-Earth Asteroid Tracking Dashboard"
)

st.markdown(
    """
    Monitor near-Earth asteroids using real data from NASA.
    Explore asteroid size, speed, distance and close approaches.
    """
)

st.markdown("---")


# =====================================================
# 7. DATE VALIDATION
# =====================================================

if len(date_range) != 2:

    st.warning("Please select both start and end dates.")

    st.stop()

start_date = date_range[0]
end_date = date_range[1]

if start_date > end_date:

    st.error("Start date cannot be after end date.")

    st.stop()

if (end_date - start_date).days > 6:

    st.error("Please select a maximum 7-day date interval.")

    st.stop()


if not api_key.strip():

    st.error("Please enter a NASA API key.")

    st.stop()


# =====================================================
# 8. FETCH NASA DATA
# =====================================================

try:

    with st.spinner("Connecting to NASA and retrieving asteroid data..."):

        df = fetch_asteroids(
            start_date.isoformat(),
            end_date.isoformat(),
            api_key.strip()
        )

except requests.exceptions.HTTPError as error:

    status_code = error.response.status_code

    if status_code == 429:

        st.error(
            "NASA API request limit reached. "
            "Wait before trying again or use your personal API key."
        )

    elif status_code == 403:

        st.error(
            "NASA API access denied. Check your API key."
        )

    elif status_code == 400:

        st.error(
            "NASA rejected the selected dates or request. "
            "Check the date range and try again."
        )

    else:

        st.error(
            f"NASA API error: HTTP {status_code}"
        )

    st.stop()

except requests.exceptions.Timeout:

    st.error(
        "NASA server took too long to respond. Please try again."
    )

    st.stop()

except requests.exceptions.RequestException as error:

    st.error(
        f"Unable to connect to NASA: {error}"
    )

    st.stop()

except ValueError:

    st.error(
        "NASA returned data that could not be processed."
    )

    st.stop()


# =====================================================
# 9. CHECK DATA
# =====================================================

if df.empty:

    st.warning(
        "No asteroid records were found for the selected dates."
    )

    st.stop()


# =====================================================
# 10. ASTEROID OVERVIEW
# =====================================================

st.header("📊 Asteroid Overview")

total_asteroids = len(df)

hazardous_count = int(
    df["Hazardous"].sum()
)

closest_distance = df[
    "Distance (km)"
].min()

largest_diameter = df[
    "Max Diameter (km)"
].max()

average_velocity = df[
    "Velocity (km/s)"
].mean()

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Asteroids",
    f"{total_asteroids}"
)

col2.metric(
    "Potentially Hazardous",
    f"{hazardous_count}"
)

col3.metric(
    "Closest Approach",
    f"{closest_distance:,.0f} km"
)

col4.metric(
    "Largest Diameter",
    f"{largest_diameter:.3f} km"
)

st.caption(
    f"Average relative velocity: {average_velocity:.2f} km/s"
)

st.markdown("---")


# =====================================================
# 11. ASTEROID EXPLORER
# =====================================================

st.header("🔭 Asteroid Explorer")

search = st.text_input(
    "Search asteroid by name",
    placeholder="Enter asteroid name..."
)

col_filter1, col_filter2 = st.columns(2)

with col_filter1:

    hazardous_only = st.checkbox(
        "Show potentially hazardous asteroids only"
    )

with col_filter2:

    sort_by = st.selectbox(
        "Sort asteroid data by",
        [
            "Distance (km)",
            "Max Diameter (km)",
            "Velocity (km/s)",
            "Approach Date"
        ]
    )

filtered_df = df.copy()

if search:

    filtered_df = filtered_df[
        filtered_df["Name"].str.contains(
            search,
            case=False,
            na=False,
            regex=False
        )
    ]

if hazardous_only:

    filtered_df = filtered_df[
        filtered_df["Hazardous"] == True
    ]

filtered_df = filtered_df.sort_values(
    by=sort_by,
    ascending=True
)

st.caption(
    f"Showing {len(filtered_df)} of {total_asteroids} asteroid records."
)

if filtered_df.empty:

    st.info("No asteroids match your search.")

else:

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "NASA URL": st.column_config.LinkColumn(
                "NASA Information"
            ),
            "Hazardous": st.column_config.CheckboxColumn(
                "Potentially Hazardous"
            )
        }
    )

    csv_data = filtered_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="⬇️ Download asteroid data (CSV)",
        data=csv_data,
        file_name="astra_asteroid_data.csv",
        mime="text/csv"
    )


st.markdown("---")


# =====================================================
# 12. ADVANCED DATA ANALYTICS
# =====================================================

st.header("📈 Asteroid Data Analytics")

tab1, tab2, tab3, tab4 = st.tabs([

    "Size Analysis",

    "Distance Analysis",

    "Hazard Analysis",

    "Velocity Analysis"

])


# -----------------------------------------------------
# TAB 1: SIZE ANALYSIS
# -----------------------------------------------------

with tab1:

    st.subheader("Top 10 Largest Asteroids")

    largest_df = df.nlargest(
        10,
        "Max Diameter (km)"
    )

    fig1 = px.bar(
        largest_df,
        x="Max Diameter (km)",
        y="Name",
        orientation="h",
        color="Max Diameter (km)",
        title="Asteroid Size Comparison",
        template="plotly_dark"
    )

    fig1.update_layout(
        yaxis={
            "categoryorder": "total ascending"
        }
    )

    st.plotly_chart(
        fig1,
        use_container_width=True
    )

    st.subheader("Asteroid Size Distribution")

    fig_size = px.histogram(
        df,
        x="Max Diameter (km)",
        nbins=15,
        title="Distribution of Asteroid Diameters",
        template="plotly_dark"
    )

    st.plotly_chart(
        fig_size,
        use_container_width=True
    )


# -----------------------------------------------------
# TAB 2: DISTANCE ANALYSIS
# -----------------------------------------------------

with tab2:

    st.subheader("Asteroid Distance from Earth")

    fig2 = px.scatter(
        df,
        x="Distance (km)",
        y="Max Diameter (km)",
        color="Hazardous",
        hover_name="Name",
        hover_data=[
            "Approach Date",
            "Velocity (km/s)"
        ],
        title="Asteroid Distance vs Size",
        template="plotly_dark"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    closest_df = df.nsmallest(
        10,
        "Distance (km)"
    )

    st.subheader("10 Closest Asteroid Approaches")

    fig_closest = px.bar(
        closest_df,
        x="Distance (km)",
        y="Name",
        orientation="h",
        title="Closest Asteroids to Earth",
        template="plotly_dark"
    )

    fig_closest.update_layout(
        yaxis={
            "categoryorder": "total ascending"
        }
    )

    st.plotly_chart(
        fig_closest,
        use_container_width=True
    )


# -----------------------------------------------------
# TAB 3: HAZARD ANALYSIS
# -----------------------------------------------------

with tab3:

    st.subheader("Asteroid Hazard Classification")

    hazard_data = pd.DataFrame({

        "Classification": [
            "Potentially Hazardous",
            "Not Classified as Hazardous"
        ],

        "Count": [
            hazardous_count,
            total_asteroids - hazardous_count
        ]

    })

    fig3 = px.pie(
        hazard_data,
        names="Classification",
        values="Count",
        title="Asteroid Classification",
        hole=0.5,
        template="plotly_dark"
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )

    st.info(
        "Potentially hazardous is a NASA classification based on "
        "orbital characteristics and estimated size. It does not "
        "mean that an asteroid is predicted to collide with Earth."
    )


# -----------------------------------------------------
# TAB 4: VELOCITY ANALYSIS
# -----------------------------------------------------

with tab4:

    st.subheader("Asteroid Relative Velocity")

    fig4 = px.bar(
        df.nlargest(10, "Velocity (km/s)"),
        x="Name",
        y="Velocity (km/s)",
        color="Velocity (km/s)",
        title="Top 10 Fastest Asteroids",
        template="plotly_dark"
    )

    st.plotly_chart(
        fig4,
        use_container_width=True
    )

    st.metric(
        "Average Relative Velocity",
        f"{average_velocity:.2f} km/s"
    )


st.markdown("---")


# =====================================================
# 13. INDIVIDUAL ASTEROID PROFILE
# =====================================================

st.header("🌌 Individual Asteroid Profile")

# Use asteroid ID as the selection value.
# This avoids ambiguity when names repeat.

asteroid_options = (
    df.drop_duplicates(subset=["ID"])
    .set_index("ID")["Name"]
    .to_dict()
)

selected_id = st.selectbox(
    "Choose an asteroid",
    options=list(asteroid_options.keys()),
    format_func=lambda asteroid_id:
        asteroid_options[asteroid_id]
)

selected_info = df[
    df["ID"] == selected_id
].iloc[0]

st.subheader(selected_info["Name"])

detail1, detail2, detail3 = st.columns(3)

detail1.metric(
    "Asteroid ID",
    selected_info["ID"]
)

detail2.metric(
    "Maximum Diameter",
    f'{selected_info["Max Diameter (km)"]:.4f} km'
)

detail3.metric(
    "Velocity",
    f'{selected_info["Velocity (km/s)"]:.2f} km/s'
)

detail4, detail5, detail6 = st.columns(3)

detail4.metric(
    "Earth Distance",
    f'{selected_info["Distance (km)"]:,.0f} km'
)

detail5.metric(
    "Approach Date",
    selected_info["Approach Date"]
)

detail6.metric(
    "Absolute Magnitude",
    f'{selected_info["Absolute Magnitude (H)"]:.2f}'
    if pd.notna(selected_info["Absolute Magnitude (H)"])
    else "N/A"
)

st.write(
    "**Orbiting Body:**",
    selected_info["Orbiting Body"]
)

st.write(
    "**Potentially Hazardous:**",
    "Yes" if selected_info["Hazardous"] else "No"
)

if selected_info["NASA URL"]:

    st.markdown(
        f"[View official NASA/JPL information]({selected_info['NASA URL']})"
    )

st.markdown("### Full NASA Asteroid Information")

if st.button("Fetch full NASA asteroid profile"):

    try:

        with st.spinner("Fetching individual asteroid information..."):

            details = fetch_asteroid_details(
                selected_id,
                api_key.strip()
            )

        st.success("NASA asteroid profile retrieved successfully!")

        orbital_data = details.get(
            "orbital_data", {}
        )

        profile1, profile2, profile3 = st.columns(3)

        profile1.metric(
            "Orbit Period",
            f'{orbital_data.get("orbital_period", "N/A")} days'
        )

        profile2.metric(
            "Inclination",
            f'{orbital_data.get("inclination", "N/A")}°'
        )

        profile3.metric(
            "Eccentricity",
            orbital_data.get("eccentricity", "N/A")
        )

        st.write(
            "**Orbit Determination Date:**",
            orbital_data.get(
                "orbit_determination_date", "N/A"
            )
        )

        st.write(
            "**First Observation:**",
            orbital_data.get(
                "first_observation_date", "N/A"
            )
        )

        st.write(
            "**Last Observation:**",
            orbital_data.get(
                "last_observation_date", "N/A"
            )
        )

        with st.expander("View raw NASA profile data"):

            st.json(details)

    except requests.exceptions.RequestException as error:

        st.error(
            f"Could not retrieve full asteroid profile: {error}"
        )

    except (ValueError, KeyError) as error:

        st.error(
            f"Could not process asteroid profile: {error}"
        )


# =====================================================
# 14. PROJECT FOOTER
# =====================================================

st.markdown("---")

st.markdown(
    """
<div style="text-align:center; color:#8ab4ff;">
    <h3>🪐 ASTRA</h3>
    <p>NASA Near-Earth Asteroid Monitoring System</p>
    <p>Python | Streamlit | Pandas | Plotly | NASA NeoWs API</p>
    <p>Educational and data exploration project.</p>
</div>
""",
    unsafe_allow_html=True
)

st.caption(
    "Data source: NASA/JPL Near Earth Object Web Service (NeoWs). "
    "Asteroid measurements and classifications are estimates."
)
