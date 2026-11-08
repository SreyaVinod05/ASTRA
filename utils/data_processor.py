
def filter_asteroids(df, search="", hazardous_only=False, sort_by="Distance (km)"):

    filtered_df = df.copy()

    # Search asteroid by name
    if search:
        filtered_df = filtered_df[
            filtered_df["Name"].str.contains(
                search,
                case=False,
                na=False,
                regex=False
            )
        ]

    # Filter potentially hazardous asteroids
    if hazardous_only:
        filtered_df = filtered_df[
            filtered_df["Hazardous"] == True
        ]

    # Sort the results
    filtered_df = filtered_df.sort_values(
        by=sort_by,
        ascending=True
    )

    return filtered_df
