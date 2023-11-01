"""A program that fetches the weather forecast of a location based on coordinates"""
import pandas as pd
from geopy.geocoders import Nominatim
import requests, json

def get_add_coordinates():
    """Get address coordinates from geopy service."""
    # Initialize geolocator
    geolocator = Nominatim(timeout=10, user_agent="Locatoriser")

    # Get user address input
    address = input("Enter your address here: ")

    # Convert address to lowercase
    address = address.lower()

    # Initialize latitude and longitude
    latitude = 0
    longitude = 0

    # Check if address is provided
    if not address:
        print("Error: No Address Provided")
        return None
    else:
        # Check if address is at least 5 characters long
        if len(address) < 5:
            print("Address should be at least 5 characters long.")
            return None
        else:
            # Get location coordinates from address
            location = geolocator.geocode(address)

            # Check if location is found
            if location is not None:
                # Get latitude and longitude
                latitude = location.latitude 
                longitude = location.longitude

    # Return latitude and longitude
    return latitude, longitude

def get_forecast(latitude, longitude):
    """Get forecast data from API."""
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=temperature_2m,relativehumidity_2m&forecast_days=1"
    params = {
        "latitude": latitude,
        "longitude": longitude,
    }
    r = requests.get(url, json=params) # Send GET request with JSON data
    if r.status_code == 200:
        return json.loads(r.text) # Return JSON response if successful
    else:
        print(f"Error: Request failed with status code {r.status_code}") # Print error message
        return None # Return None if request fails

# Normalise the data
# Store the data into pandas dataframe for analysis
def main():
    # Get coordinates and weather data
    latitude, longitude = get_add_coordinates()
    
    if latitude is not None and longitude is not None:
        data = get_forecast(latitude, longitude)


        if data is not None:
            final_output = pd.json_normalize(data)

            # Extract and explode the necessary columns
            hourlyTime = final_output[['hourly.time']]
            hourlyTime = hourlyTime.explode('hourly.time')
            hourlyTime.reset_index(drop=True, inplace=True)

            hourlyTemp = final_output[['hourly.temperature_2m']]
            hourlyTemp = hourlyTemp.explode('hourly.temperature_2m')
            hourlyTemp.reset_index(drop=True, inplace=True)

            hourlyHumid = final_output[['hourly.relativehumidity_2m']]
            hourlyHumid = hourlyHumid.explode('hourly.relativehumidity_2m')
            hourlyHumid.reset_index(drop=True, inplace=True)

            # Concatenate the exploded columns
            new_df = pd.concat([hourlyTime["hourly.time"], hourlyTemp["hourly.temperature_2m"], 
                                hourlyHumid["hourly.relativehumidity_2m"]],axis=1)

            # Rename columns for clarity
            new_df.columns = ["Time", "Temperature", "Relative Humidity"]

            # Print or process the new_df DataFrame as needed
            return new_df
        else:
            print("Error: Unable to fetch weather data")
    else:
        print("Error: Unable to obtain coordinates")

main()