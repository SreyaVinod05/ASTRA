
import pandas as pd

from utils.data_processor import filter_asteroids


def sample_data():
    return pd.DataFrame({
        "Name": ["Asteroid A", "Asteroid B", "Asteroid C"],
        "Hazardous": [True, False, True],
        "Distance (km)": [500000, 200000, 800000]
    })


def test_filter_by_name():
    df = sample_data()

    result = filter_asteroids(df, search="Asteroid A")

    assert len(result) == 1
    assert result.iloc[0]["Name"] == "Asteroid A"


def test_filter_hazardous_only():
    df = sample_data()

    result = filter_asteroids(df, hazardous_only=True)

    assert len(result) == 2
    assert result["Hazardous"].all()


def test_sort_by_distance():
    df = sample_data()

    result = filter_asteroids(df, sort_by="Distance (km)")

    assert result["Distance (km)"].tolist() == [
        200000, 500000, 800000
    ]
