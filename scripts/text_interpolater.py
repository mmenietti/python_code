#------------------------------------------------------------
# Dependencies
#------------------------------------------------------------
import pathlib
import os
import argparse

#------------------------------------------------------------
# File Contents Reader
#------------------------------------------------------------
def collect_insertion_data(insert_root):
    inserts_dict = {}
    for x in insert_root.iterdir():
        if x.is_file():
            inserts_dict[x.stem] = x.read_text(encoding='utf-8')
        elif x.is_dir():
            sub_inserts = collect_insertion_data(x)
            for (path_stem, file_contents) in sub_inserts.items():
                insert_key = x.stem + '/' + path_stem
                inserts_dict[insert_key] = file_contents

    return inserts_dict

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
    # inserts_dict = {}
    # for x in inserts_directory_path.iterdir():
    #     if x.is_file():
    #         inserts_dict[x.stem] = x.read_text(encoding='utf-8')
    inserts_dict = collect_insertion_data(inserts_directory_path)

    # print(inserts_dict)

    # Import the input file text and interpolate the insertion text
    input_file_string = input_file_path.read_text(encoding='utf-8')
    interpolated_string = input_file_string.format(**inserts_dict)

    # Write the interpolated text to the output file.
    output_file_path.write_text(data=interpolated_string, encoding='utf-8')