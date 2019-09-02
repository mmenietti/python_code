#------------------------------------------------------------
# Dependencies
#------------------------------------------------------------
import pathlib
import os
import argparse
import re 
#------------------------------------------------------------
# 
#------------------------------------------------------------
def is_video_file(in_file):
    if in_file.suffix == '.avi':
        return True
    elif in_file.suffix == '.mp4':
        return True
    elif in_file.suffix == '.mkv':
        return True
    elif in_file.suffix == '.wmv':
        return True
    else:
        return False

def build_filename_tokens(in_path):

    delimiters = r'\W'
    
    stem_tokens = re.split(delimiters, in_path.stem)

    print(stem_tokens)

def process_directory(sub_dir):
    for x in sub_dir.iterdir():
        if is_video_file(x):
            build_filename_tokens(x)


if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description='Process path string.')
    # parser.add_argument('input_directory')
    # args = parser.parse_args()
    
    # input_directory_path = pathlib.Path(args.input_directory)    
    input_directory_path = pathlib.Path('E:\\downloads_backup')    

    for x in input_directory_path.iterdir():
        if x.is_dir():
            process_directory(x)