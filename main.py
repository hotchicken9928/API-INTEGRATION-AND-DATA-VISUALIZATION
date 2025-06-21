import requests
import json
import os
import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from dotenv import load_dotenv
from collections import Counter
from dotenv import load_dotenv

load_dotenv()

BASE_API_URL = "http://api.openweathermap.org/data/2.5/forecast"
PLOTS_DIR = "visualizations" 


def get_api_key():
    """
    Retrieves the OpenWeatherMap API key.
    Tries to get it from an environment variable first, then prompts the user.
    """
    api_key = os.getenv("OPENWEATHERMAP_API_KEY")
    if not api_key:
        print("OpenWeatherMap API key not found in .env file or environment variables.")
        api_key = input("Please enter your OpenWeatherMap API key: ").strip()
    if not api_key:
        print("API key is required to run the script. Exiting.")
        exit()
    return api_key

def fetch_weather_data(api_key, city_name):
    """
    Fetches 5-day/3-hour weather forecast data for the given city.
    
    Args:
        api_key (str): The OpenWeatherMap API key.
        city_name (str): The name of the city.
        
    Returns:
        dict: Parsed JSON response from the API, or None if an error occurs.
    """
    params = {
        "q": city_name,
        "appid": api_key,
        "units": "metric"  
    }
    try:
        response = requests.get(BASE_API_URL, params=params)
        response.raise_for_status() 
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 401:
            print(f"HTTP Error: {http_err} - Invalid API key or key not activated yet.")
        elif response.status_code == 404:
            print(f"HTTP Error: {http_err} - City not found: {city_name}")
        else:
            print(f"HTTP Error: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Request Error: {req_err}")
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON response from API.")
    return None

def process_forecast_data(data):
    """
    Processes the raw forecast data to extract relevant information for plotting.
    
    Args:
        data (dict): The raw JSON data from the OpenWeatherMap API.
        
    Returns:
        tuple: A tuple containing lists of timestamps, temperatures, feels_like temperatures,
               humidities, wind_speeds, and weather_descriptions. Returns None if data is invalid.
    """
    if not data or "list" not in data:
        print("Error: Invalid or empty data received from API.")
        return None

    timestamps = []
    temperatures = []
    feels_like_temps = []
    humidities = []
    wind_speeds = []
    weather_descriptions_main = [] 

    for entry in data["list"]:
        dt_object = datetime.datetime.fromtimestamp(entry["dt"])
        timestamps.append(dt_object)
        temperatures.append(entry["main"]["temp"])
        feels_like_temps.append(entry["main"]["feels_like"])
        humidities.append(entry["main"]["humidity"])
        wind_speeds.append(entry["wind"]["speed"]) # m/s
        if entry["weather"] and len(entry["weather"]) > 0:
            weather_descriptions_main.append(entry["weather"][0]["main"])
        else:
            weather_descriptions_main.append("N/A")
            
    return timestamps, temperatures, feels_like_temps, humidities, wind_speeds, weather_descriptions_main

def ensure_plots_dir():
    """Ensures the directory for saving plots exists."""
    if not os.path.exists(PLOTS_DIR):
        os.makedirs(PLOTS_DIR)
        print(f"Created directory: {PLOTS_DIR}")


def plot_temperature_forecast(timestamps, temps, feels_like_temps, city_name):
    """Generates and saves a plot for temperature and feels_like temperature."""
    plt.figure(figsize=(12, 6))
    sns.lineplot(x=timestamps, y=temps, marker='o', label="Temperature (°C)")
    sns.lineplot(x=timestamps, y=feels_like_temps, marker='x', linestyle='--', label="Feels Like (°C)")
    plt.title(f"5-Day Temperature & Feels Like Forecast for {city_name.title()}")
    plt.xlabel("Time")
    plt.ylabel("Temperature (°C)")
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    
    filename = os.path.join(PLOTS_DIR, "temperature_forecast.png")
    plt.savefig(filename)
    print(f"Saved temperature forecast plot to {filename}")
    plt.show()

def plot_humidity_forecast(timestamps, humidities, city_name):
    """Generates and saves a plot for humidity."""
    plt.figure(figsize=(12, 6))
    sns.lineplot(x=timestamps, y=humidities, marker='o', color='teal', label="Humidity (%)")
    plt.title(f"5-Day Humidity Forecast for {city_name.title()}")
    plt.xlabel("Time")
    plt.ylabel("Humidity (%)")
    plt.xticks(rotation=45)
    plt.ylim(0, 100) 
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    filename = os.path.join(PLOTS_DIR, "humidity_forecast.png")
    plt.savefig(filename)
    print(f"Saved humidity forecast plot to {filename}")
    plt.show()

def plot_wind_speed_forecast(timestamps, wind_speeds, city_name):
    """Generates and saves a plot for wind speed."""
    plt.figure(figsize=(12, 6))
    sns.lineplot(x=timestamps, y=wind_speeds, marker='o', color='purple', label="Wind Speed (m/s)")
    plt.title(f"5-Day Wind Speed Forecast for {city_name.title()}")
    plt.xlabel("Time")
    plt.ylabel("Wind Speed (m/s)")
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    filename = os.path.join(PLOTS_DIR, "wind_speed_forecast.png")
    plt.savefig(filename)
    print(f"Saved wind speed forecast plot to {filename}")
    plt.show()

def plot_weather_conditions_pie(weather_descriptions_main, city_name):
    """Generates and saves a pie chart for weather condition distribution."""
    if not weather_descriptions_main:
        print("No weather descriptions to plot for pie chart.")
        return

    condition_counts = Counter(weather_descriptions_main)
    labels = condition_counts.keys()
    sizes = condition_counts.values()
    
    colors = sns.color_palette('pastel')[0:len(labels)]

    plt.figure(figsize=(10, 8))
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140, shadow=True)
    plt.title(f"Distribution of Weather Conditions for {city_name.title()} (Next 5 Days)")
    plt.axis('equal')  
    plt.tight_layout()

    filename = os.path.join(PLOTS_DIR, "weather_conditions_pie_chart.png")
    plt.savefig(filename)
    print(f"Saved weather conditions pie chart to {filename}")
    plt.show()

def main():
    """Main function to run the weather data fetching and visualization."""
    print("--- Weather Data Visualizer ---")
    
    sns.set_theme(style="whitegrid")

    api_key = get_api_key()
    
    city_name = os.getenv("CITY_NAME")
    if not city_name:
        print("City name cannot be empty. Exiting.")
        return

    print(f"\nFetching weather data for {city_name.title()}...")
    weather_data = fetch_weather_data(api_key, city_name)

    if weather_data:
        print("Weather data fetched successfully.")
        
        processed_data = process_forecast_data(weather_data)
        if not processed_data:
            print("Failed to process weather data. Exiting.")
            return
            
        timestamps, temps, feels_like_temps, humidities, wind_speeds, weather_descriptions = processed_data
        
        ensure_plots_dir()
        
        print("\nGenerating and saving plots...")
        plot_temperature_forecast(timestamps, temps, feels_like_temps, city_name)
        plot_humidity_forecast(timestamps, humidities, city_name)
        plot_wind_speed_forecast(timestamps, wind_speeds, city_name)
        plot_weather_conditions_pie(weather_descriptions, city_name)
        
        print(f"\n--- All visualizations saved in '{PLOTS_DIR}' directory ---")
        print("--- Script finished ---")
    else:
        print(f"Could not retrieve weather data for {city_name.title()}. Please check the city name and your API key.")

if __name__ == "__main__":
    main()
