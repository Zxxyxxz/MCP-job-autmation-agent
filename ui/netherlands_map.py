import folium
from streamlit_folium import st_folium
import json

NETHERLANDS_CITIES = {
    'Amsterdam': [52.3676, 4.9041],
    'Rotterdam': [51.9244, 4.4777],
    'The Hague': [52.0705, 4.3007],
    'Utrecht': [52.0907, 5.1214],
    'Eindhoven': [51.4416, 5.4697],
    'Groningen': [53.2194, 6.5665],
    'Tilburg': [51.5555, 5.0913],
    'Almere': [52.3508, 5.2647],
    'Breda': [51.5719, 4.7683],
    'Nijmegen': [51.8426, 5.8545],
    'Enschede': [52.2215, 6.8937],
    'Hengelo': [52.2659, 6.7931],
    'Oldenzaal': [52.3136, 6.9295],
    'Rijswijk': [52.0365, 4.3251],
    'Overijssel': [52.4387, 6.5019]
}

def create_job_map(db):
    """Create map with job locations color-coded by score"""
    m = folium.Map(
        location=[52.1326, 5.2913],  # Center of Netherlands
        zoom_start=7,
        tiles='OpenStreetMap'
    )
    
    # Get job counts by city
    cursor = db.conn.execute("""
        SELECT location, COUNT(*) as count, AVG(ai_score) as avg_score
        FROM jobs
        GROUP BY location
    """)
    
    job_locations = {}
    for row in cursor.fetchall():
        location = row['location']
        if location:
            # Extract city name from location string
            for city in NETHERLANDS_CITIES:
                if city.lower() in location.lower():
                    if city not in job_locations:
                        job_locations[city] = {'count': 0, 'avg_score': 0}
                    job_locations[city]['count'] += row['count']
                    job_locations[city]['avg_score'] = row['avg_score'] or 0
                    break
    
    # Add markers for cities with jobs
    for city, coords in NETHERLANDS_CITIES.items():
        if city in job_locations:
            data = job_locations[city]
            
            # Color based on average score
            if data['avg_score'] >= 80:
                color = 'green'
                icon = 'star'
            elif data['avg_score'] >= 70:
                color = 'orange'
                icon = 'info-sign'
            else:
                color = 'red'
                icon = 'warning-sign'
            
            folium.Marker(
                coords,
                popup=f"<b>{city}</b><br>{data['count']} jobs<br>Avg Score: {data['avg_score']:.0f}",
                tooltip=f"{city}: {data['count']} jobs",
                icon=folium.Icon(color=color, icon=icon)
            ).add_to(m)
        else:
            # Add gray marker for cities without jobs
            folium.Marker(
                coords,
                popup=f"<b>{city}</b><br>No jobs yet",
                tooltip=city,
                icon=folium.Icon(color='gray', icon='question-sign')
            ).add_to(m)
    
    return m