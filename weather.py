# weather.py

import os
import requests
from dotenv import load_dotenv
from datetime import datetime
import database as db

# --- (Keep load_dotenv, API_KEY, BASE_URL, and celsius_to_fahrenheit as is) ---
load_dotenv()
API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5/forecast"

def celsius_to_fahrenheit(temp_celsius):
    return (temp_celsius * 9/5) + 32

def fetch_and_log_weather():
    params = { "lat": 35.79, "lon": -78.78, "appid": API_KEY, "units": "metric" }
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        full_forecast = response.json()
        
        # --- New Rain Check Logic ---
        rain_forecast = False
        today_date = datetime.now().date()
        for period in full_forecast["list"]:
            period_date = datetime.fromisoformat(period["dt_txt"]).date()
            if period_date == today_date:
                weather_id = period["weather"][0]["id"]
                # Weather condition codes: 2xx=Thunderstorm, 3xx=Drizzle, 5xx=Rain
                if 200 <= weather_id <= 599:
                    rain_forecast = True
                    break # Found rain, no need to check further

        # Get current temp and log everything to the DB
        current_temp_c = full_forecast["list"][0]['main']['temp']
        current_feels_like_c = full_forecast["list"][0]['main']['feels_like']
        
        with db.engine.connect() as connection:
            db.add_weather_log(connection, current_temp_c, current_feels_like_c, rain_forecast)
        print("Successfully fetched and logged new weather data to DB.")
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")