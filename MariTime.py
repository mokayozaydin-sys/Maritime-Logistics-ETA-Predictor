import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# ==========================================
# 1. SETUP & CONFIGURATION
# ==========================================
n_rows = 5000
np.random.seed(42)

# Standardized Port Names (Tableau-friendly)
origin_ports = ['Shanghai', 'Ningbo', 'Singapore', 'Busan', 'Tokyo', 'Los Angeles', 'Dubai']
transit_hubs = ['Singapore', 'Jebel Ali', 'Tanger Med', 'Piraeus', 'Marsaxlokk']

# Correcting names for global recognition (e.g., Marseille, Izmir)
destination_ports = [
    'Ambarli', 'Izmir', 'Mersin', 'Valencia', 'Barcelona',
    'Genoa', 'New York', 'Antwerp', 'Rotterdam', 'Marseille'
]

# Mapping cities to countries to solve "Ambiguous/Unrecognized" errors
city_to_country = {
    'Shanghai': 'China', 'Ningbo': 'China', 'Singapore': 'Singapore',
    'Busan': 'South Korea', 'Tokyo': 'Japan', 'Los Angeles': 'United States',
    'Dubai': 'United Arab Emirates', 'Jebel Ali': 'United Arab Emirates',
    'Tanger Med': 'Morocco', 'Piraeus': 'Greece', 'Marsaxlokk': 'Malta',
    'Ambarli': 'Turkey', 'Izmir': 'Turkey', 'Mersin': 'Turkey',
    'Valencia': 'Spain', 'Barcelona': 'Spain', 'Genoa': 'Italy',
    'New York': 'United States', 'Antwerp': 'Belgium', 'Rotterdam': 'Netherlands',
    'Marseille': 'France'
}

# ==========================================
# 2. LOGIC FUNCTIONS
# ==========================================
def calculate_disruption(weather):
    probs = {
        'Clear': [0.95, 0.05], 'Rain': [0.85, 0.15],
        'Fog': [0.60, 0.40], 'Storm': [0.20, 0.80], 'Hurricane': [0.0, 1.0]
    }
    return np.random.choice([0, 1], p=probs.get(weather, [0.95, 0.05]))

# ==========================================
# 3. DATA GENERATION
# ==========================================
data = {
    'Shipment_ID': [f"SC-{np.random.randint(10000, 99999)}" for _ in range(n_rows)],
    'Order_Date': [datetime(2024, 1, 1) + timedelta(days=np.random.randint(0, 365)) for _ in range(n_rows)],
    'Origin_Port': np.random.choice(origin_ports, n_rows),
    'Transit_Port': np.random.choice(transit_hubs, n_rows),
    'Destination_Port': np.random.choice(destination_ports, n_rows),
    'Total_Distance_nm': np.random.randint(4000, 12000, n_rows),
    'Weather_L1': np.random.choice(['Clear', 'Rain', 'Fog', 'Storm', 'Hurricane'], n_rows, p=[0.7, 0.18, 0.08, 0.035, 0.005]),
    'Weather_L2': np.random.choice(['Clear', 'Rain', 'Fog', 'Storm', 'Hurricane'], n_rows, p=[0.7, 0.18, 0.08, 0.035, 0.005])
}

df = pd.DataFrame(data)

# Adding Countries for perfect mapping
df['Origin_Country'] = df['Origin_Port'].map(city_to_country)
df['Transit_Country'] = df['Transit_Port'].map(city_to_country)
df['Destination_Country'] = df['Destination_Port'].map(city_to_country)

# Calculating Disruptions and Durations
df['D1'] = df['Weather_L1'].apply(calculate_disruption)
df['D2'] = df['Weather_L2'].apply(calculate_disruption)

speed = 18 * 24 # daily nautical miles
# Rounding to 1 decimal place to prevent ##### error in Tableau
df['Leg_1_Days'] = np.round((df['Total_Distance_nm']*0.5 / speed) * (1 + (df['D1']*0.3)), 1)
df['Leg_2_Days'] = np.round((df['Total_Distance_nm']*0.5 / speed) * (1 + (df['D2']*0.3)), 1)
df['Total_Days'] = df['Leg_1_Days'] + df['Leg_2_Days']

# ==========================================
# 4. FIXING THE CALCULATION ERROR IN PYTHON
# ==========================================
# We calculate the ETA here so you don't need a formula in Tableau
df['Final_Arrival_Date'] = df.apply(lambda x: x['Order_Date'] + timedelta(days=float(x['Total_Days'])), axis=1)

# Final export
df.to_csv('final_logistics_v5.csv', index=False)
print("Done! Open final_logistics_v5.csv in Tableau.")