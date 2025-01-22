def generate_data_paths():
    ride_name = input("Enter the ride name: ").replace(" ",
                                                       "_").lower()  # Replace spaces with underscores for the folder name
    full_ride_name = ride_name.replace("_", " ").title()  # Capitalize the full ride name for the file name
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    base_path = r'C:\Users\luked\PycharmProjects\disneylandapp'  # Base directory

    # Start the output with the ride initialization
    print(f"{ride_name} = Ride(")
    print(f'    name="{full_ride_name}",')
    print(f'    url="https://www.thrill-data.com/waits/park/dlr/disneyland/",')
    print(f'    data_paths={{  # Paths for your data here')

    # Loop through months and print the corresponding data paths
    for month in months:
        print(f"        '{month}': r'{base_path}\\{ride_name}\\{full_ride_name}, {month} 2024, Disneyland.csv',")

    # Close the dictionary and the ride initialization
    print(f'    }},')
    print(f'    pushover_user_key="unb249suwmpir19ng1zguhxqxyyfgd",')
    print(f'    pushover_api_token="amqmtqh5hjne37tk68keg9iwytjwhd"')
    print(')')


# Example usage:
generate_data_paths()
