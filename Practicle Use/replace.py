def replace_and_create_new_file(ride_name, original_script_file):
    # Read the content of the original script from the file
    try:
        with open(original_script_file, "r", encoding="utf-8") as file:
            original_script = file.read()
    except FileNotFoundError:
        print(f"Error: The file '{original_script_file}' was not found.")
        return

    # Replace the placeholder 'Space Mountain' with the user-provided ride name
    modified_script = original_script.replace("Space Mountain", ride_name)

    # Generate the filename for the new script
    filename = f"noti-{ride_name.replace(' ', '_').lower()}.py"

    # Write the modified script to a new file
    with open(filename, "w", encoding="utf-8") as new_file:
        new_file.write(modified_script)

    print(f"New script created: {filename}")


# Get the ride name from the user
ride_name_input = input("Enter the ride name: ")

# Provide the path to the original script file
original_script_file = input("Enter the path of the original script file: ")

# Call the function to replace and create the new file
replace_and_create_new_file(ride_name_input, original_script_file)
