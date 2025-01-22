def generate_data_paths():
    base_path = r'C:\Users\luked\PycharmProjects\disneylandapp'  # Base directory
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    rides = []

    while True:
        ride_name = input("Enter the ride name (or type 'stop' to finish): ")
        if ride_name.strip().lower() == 'stop':
            break

        ride_name = ride_name.replace(" ", "_").lower()  # Replace spaces with underscores for the folder name
        full_ride_name = ride_name.replace("_", " ").title()  # Capitalize the full ride name for the file name

        ride_data = []
        ride_data.append(f"{ride_name} = Ride(")
        ride_data.append(f'    name="{full_ride_name}",')
        ride_data.append(f'    url="https://www.thrill-data.com/waits/park/dlr/disneyland/",')
        ride_data.append(f'    data_paths={{  # Paths for your data here')

        for month in months:
            ride_data.append(f"        '{month}': r'{base_path}\\{ride_name}\\{full_ride_name}, {month} 2024, Disneyland.csv',")

        ride_data.append(f'    }},')
        ride_data.append(f'    pushover_user_key="unb249suwmpir19ng1zguhxqxyyfgd",')
        ride_data.append(f'    pushover_api_token="amqmtqh5hjne37tk68keg9iwytjwhd"')
        ride_data.append(')')

        rides.append("\n".join(ride_data))

    print("\n\n".join(rides))

# Example usage:
generate_data_paths()