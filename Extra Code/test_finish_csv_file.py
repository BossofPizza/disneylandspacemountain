import pandas as pd
from datetime import datetime, timedelta


def extend_to_end_of_month(input_csv_path, output_csv_path):
    # Load the CSV data
    df = pd.read_csv(input_csv_path, parse_dates=['Date/Time'])

    # Ensure Date/Time is parsed properly
    df['Date/Time'] = pd.to_datetime(df['Date/Time'])

    # Find the last timestamp in the dataset
    last_time = df['Date/Time'].max()

    # Define the end of the month based on the last timestamp
    end_of_month = datetime(last_time.year, last_time.month, last_time.day, 23, 59, 59)

    # Create a list of 5-minute intervals from the last timestamp to the end of the month
    new_data = []
    current_time = last_time

    while current_time <= end_of_month:
        # Calculate the average wait time for the given 5-minute interval
        time_window = df[(df['Date/Time'] >= current_time) & (df['Date/Time'] < current_time + timedelta(minutes=5))]

        # Calculate the average wait time for this time window
        if not time_window.empty:
            average_wait_time = time_window['Wait Time'].mean()
        else:
            average_wait_time = 0  # Default to 0 if no data in this window

        # Append the new row
        new_data.append({
            'Ride': 'Big Thunder Mountain Railroad',  # Keep the same ride name
            'Date/Time': current_time,
            'Wait Time': average_wait_time
        })

        # Move to the next 5-minute interval
        current_time += timedelta(minutes=5)

    # Convert the new data to a DataFrame
    new_df = pd.DataFrame(new_data)

    # Append the new data to the original data and save to a new CSV
    final_df = pd.concat([df, new_df], ignore_index=True)

    # Save to the new CSV file
    final_df.to_csv(output_csv_path, index=False)


# Usage example
input_csv_path = 'path_to_your_input_file.csv'
output_csv_path = 'path_to_output_file.csv'
extend_to_end_of_month(input_csv_path, output_csv_path)
