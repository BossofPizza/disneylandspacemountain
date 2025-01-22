def generate_thread_code(ride_name):
    # Format the ride name to be lowercase and replace spaces with underscores
    formatted_ride_name = ride_name.replace(" ", "_").lower()

    # Generate the thread creation code
    thread_code = f"{formatted_ride_name}_thread = threading.Thread(target={formatted_ride_name}.start_checking)\n"
    thread_code += f"{formatted_ride_name}_thread.daemon = True\n"
    thread_code += f"{formatted_ride_name}_thread.start()"
    # Return the generated code
    return thread_code

# Example usage
ride_name = input("Enter the ride name: ")
generated_code = generate_thread_code(ride_name)
print("\nGenerated Thread Code:")
print(generated_code)
