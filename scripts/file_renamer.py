#------------------------------------------------------------
# Dependencies
#------------------------------------------------------------
import pathlib
import os
import argparse

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
                
def rename_video(sub_dir):
    counter = 0
    for x in sub_dir.iterdir():
        counter = counter + 1
        if is_video_file(x):
            print(x.name + ' is video')
            new_name_path = x.with_name(sub_dir.name)            

            new_name_path = new_name_path.with_suffix(x.suffix)            
            new_path_path = new_name_path.parents[1].joinpath(new_name_path.name)

            while new_path_path.exists():                
                new_path_path = new_path_path.with_name(sub_dir.name + ' ' + str(counter) + new_path_path.suffix)
                
                                
            print(new_path_path.parts)
            x.rename(new_path_path)
        # else:
        #     print(x.name + ' is not video')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process path string.')
    parser.add_argument('input_directory')

    args = parser.parse_args()
    
    input_directory_path = pathlib.Path(args.input_directory)    

    for x in input_directory_path.iterdir():
        if x.is_dir():
            rename_video(x)