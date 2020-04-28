#------------------------------------------------------------
# Dependencies
#------------------------------------------------------------
import pathlib
import os
import csv
import argparse
import re 
import collections
import datetime
import itertools

#------------------------------------------------------------------------------    

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

def split_delimiters(in_string):    
    return re.split(r'[-|\s\W+_]', in_string)

def split_camel_case(in_string):
    matches = re.finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', in_string)
    return [m.group(0) for m in matches]

def split_filename(in_string):
    char_group_array = []
    
    delimiter_groups_array = split_delimiters(in_string)
    camel_case_groups_array = [split_camel_case(x) for x in delimiter_groups_array]

    for i_list in camel_case_groups_array:
        char_group_array.extend(i_list)

    return char_group_array

def read_website_names(file_path):    
    website_dict = dict()

    with file_path.open('r', newline='', encoding='utf-8') as file_path:
        name_records = csv.reader(file_path)
        for row in name_records:
            canonical_name = row[0]
            char_groups =  [x.casefold() for x in split_filename(row[1])]

            website_dict[canonical_name] = frozenset(char_groups)

    return website_dict

def process_directory(sub_dir):
    lexicon_dict = dict()

    file_count = 0

    for i_path in sub_dir.iterdir():
        if i_path.is_file() and is_video_file(i_path):
            file_count += 1
            file_char_groups = split_filename(i_path.stem)

            for i_group in set(file_char_groups):
                if i_group in lexicon_dict:
                    lexicon_dict[i_group.casefold()] += 1
                else:
                    lexicon_dict[i_group.casefold()] = 1

        elif i_path.is_dir():
            (sub_file_count, sub_lexicon_dict) = process_directory(i_path)

            file_count += sub_file_count

            for i_group, i_count in sub_lexicon_dict.items():
                if i_group in lexicon_dict:
                    lexicon_dict[i_group] += i_count
                else:
                    lexicon_dict[i_group] = i_count
            
    return (file_count, lexicon_dict)
            

if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description='Process path string.')
    # parser.add_argument('input_directory')
    # args = parser.parse_args()
          
    input_file_name_path = pathlib.Path(r'C:\Users\micha\Documents\python\scripts\website_names.csv')    
    output_file_name_path = pathlib.Path(r'C:\Users\micha\Documents\python\scripts\website_names_new.csv')   

    old_website_dict = read_website_names(input_file_name_path)
    
    new_website_dict = dict()

    for i_name, i_groups in old_website_dict.items():
        name_tokens = [x.casefold() for x in split_filename(i_name)]

        new_website_dict[i_name] = (name_tokens,  [x.casefold() for x in i_groups])

        

    with output_file_name_path.open('w', newline='', encoding='utf-8') as out_path:
        csv_writer = csv.writer(out_path)

        for i_name, i_group_tuple in new_website_dict.items():
            row = [i_name, '|'.join(i_group_tuple[0]), '|'.join(i_group_tuple[1])]
            csv_writer.writerow(row)