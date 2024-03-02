#!/usr/bin/env python3
import requests
import csv
from datetime import datetime
import pytz

# Replace 'your_api_key_here' with your actual JCDecaux API key.
API_KEY = 'e42659b6b45ae7dd9ca5cfc3674528e84a28e254'

def fetch_data(api_key):
    api_url = "https://api.jcdecaux.com/vls/v1/stations"
    contract = "dublin"

    full_url = f"{api_url}?contract={contract}&apiKey={api_key}"

    try:
        response = requests.get(full_url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def convert_epoch_to_readable(epoch_time):
    # Assuming the epoch time is in milliseconds
    return datetime.fromtimestamp(epoch_time / 1000, pytz.timezone('Europe/Dublin')).strftime('%Y-%m-%d %H:%M:%S')

def save_to_csv(data, filename):
    if data:
        field_names = ["number", "name", "address", "position", "banking", "bonus", "status", "contract_name", "bike_stands", "available_bike_stands", "available_bikes", "last_update"]
        
        try:
            with open(filename, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=field_names)
                writer.writeheader()
                for station in data:
                    # Convert the last_update field to a readable format
                    station['last_update'] = convert_epoch_to_readable(station['last_update'])
                    writer.writerow(station)
            print(f"Data saved to {filename} successfully!")
        except Exception as e:
            print(f"Error occurred while writing to CSV: {e}")
    else:
        print("No data to save.")

def main():
    data = fetch_data(API_KEY)
    save_to_csv(data, "stations_data.csv")

if __name__ == "__main__":
    main()
