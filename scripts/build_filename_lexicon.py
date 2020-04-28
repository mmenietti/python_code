#------------------------------------------------------------
# Dependencies
#------------------------------------------------------------
import pathlib
# import os
import csv
import argparse
# import collections
# import itertools
import mm.misc_utilities
import mm.text_utilities

#------------------------------------------------------------------------------    
def split_filename(in_string):
    char_group_array = []
    
    delimiter_groups_array = mm.text_utilities.split_delimiters(in_string)
    camel_case_groups_array = [mm.text_utilities.split_camel_case(x) for x in delimiter_groups_array]

    for i_list in camel_case_groups_array:
        char_group_array.extend(i_list)

    return char_group_array
    
#------------------------------------------------------------------------------    
if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description='Process path string.')
    # parser.add_argument('input_directory')
    # args = parser.parse_args()
          
    working_directory_path = pathlib.Path(r'E:\downloads_backup')    
    output_file_name_path = pathlib.Path(r'C:\Users\micha\Documents\python\scripts\filename_lexicon.csv')

    path_list = mm.misc_utilities.build_recursive_file_list(working_directory_path, mm.misc_utilities.is_video_file)
    n_paths = len(path_list)
    
    lexicon_dict = dict()

    for i_path in path_list:
        char_groups = [x.casefold() for x in split_filename(i_path.stem)]

        for i_group in char_groups:
            group_count = lexicon_dict.get(i_group, 0)
            group_count += 1
            lexicon_dict[i_group] = group_count

    for i_group, group_count in lexicon_dict.items():        
        lexicon_dict[i_group] = float(group_count) / n_paths

    with output_file_name_path.open('w', newline='', encoding='utf-8') as out_path:
        csv_writer = csv.writer(out_path)

        for i_group, i_count in lexicon_dict.items():
            row = [i_group, str(i_count)]                
            csv_writer.writerow(row)