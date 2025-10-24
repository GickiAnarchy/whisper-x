import json
import os # Used only to create a sample file for demonstration

def format_json_file(input_filename = "gp.json", output_filename = "lyrics2.json", indent_size=4):
    """
    Reads a JSON file, rewrites it to a new file with improved,
    human-readable indentation.

    Args:
        input_filename (str): The path to the source JSON file.
        output_filename (str): The path where the formatted JSON will be saved.
        indent_size (int): The number of spaces to use for indentation.
    """
    try:
        # 1. Read the JSON file and load its content into a Python dictionary
        with open(input_filename, 'r') as infile:
            data = json.load(infile)

        # 2. Write the Python dictionary back to a file in a formatted way
        with open(output_filename, 'w') as outfile:
            # The 'indent' parameter is what adds the human-readable formatting
            json.dump(data, outfile, indent=indent_size)

        print(f"Successfully read from '{input_filename}' and wrote formatted JSON to '{output_filename}'.")

    except FileNotFoundError:
        print(f"Error: The file '{input_filename}' was not found.")
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{input_filename}'. Check the file's structure.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    format_json_file()
