#------------------------------------------------------------
# Dependencies
#------------------------------------------------------------
import pathlib
import os
import argparse

#------------------------------------------------------------
# Entry Point
#------------------------------------------------------------
if __name__ == "__main__":
    # Parse Command-line Arguments
    parser = argparse.ArgumentParser(description='Process path string.')
    parser.add_argument('inserts_directory')
    parser.add_argument('input_file')
    parser.add_argument('output_file')
    
    args = parser.parse_args()    
    
    # Setup file paths to inputs and outputs
    inserts_directory_path = pathlib.Path(args.inserts_directory)    
    input_file_path        = pathlib.Path(args.input_file)  
    output_file_path       = pathlib.Path(args.output_file)  

    # Collect insertion data
    inserts_dict = {}
    for x in inserts_directory_path.iterdir():
        if x.is_file():
            inserts_dict[x.stem] = x.read_text(encoding='utf-8')

    # Import the input file text and interpolate the insertion text
    input_file_string = input_file_path.read_text(encoding='utf-8')
    interpolated_string = input_file_string.format(**inserts_dict)

    # Write the interpolated text to the output file.
    output_file_path.write_text(data=interpolated_string, encoding='utf-8')