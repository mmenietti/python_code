#------------------------------------------------------------
# Dependencies
#------------------------------------------------------------
import pathlib
# import os
import csv
import argparse
import collections
import datetime
# import itertools
# import sys
import hashlib
import math
import mm.text_utilities
import mm.misc_utilities
#------------------------------------------------------------

# def read_ssa_names(names_directory_path):    
#     name_set = set()

#     for i_path in names_directory_path.iterdir():
#         with i_path.open('r', newline='', encoding='utf-8') as file_path:
#             if i_path.is_file() and i_path.suffix == '.txt':
#                 name_records = csv.reader(file_path)
#                 for row in name_records:
#                     name_set.add(row[0].casefold())
#     return name_set



if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description='Process path string.')
    # parser.add_argument('input_directory')
    # args = parser.parse_args()
          
    names_directory_path = pathlib.Path(r'C:\Users\micha\Documents\python\scripts\names')
    output_file_name_path = pathlib.Path(r'C:\Users\micha\Documents\python\scripts\ssa_name_dataset.csv')

    name_year_gender_dict = dict()

    for i_path in names_directory_path.iterdir():
        if i_path.is_file() and i_path.suffix == '.txt':
            with i_path.open('r', newline='', encoding='utf-8') as file_path:
                year = int(i_path.stem[-4:])

                name_records = csv.reader(file_path)
                for row in name_records:
                    name = row[0].casefold()
                    gender = row[1].casefold()
                    count = int(row[2])

                    name_year_gender_dict[(name, year, gender)] = count

    with output_file_name_path.open('w', newline='', encoding='utf-8') as out_path:
        csv_writer = csv.writer(out_path)

        for i_name_year_gender, i_count in name_year_gender_dict.items():
            row = [i_name_year_gender[0], i_name_year_gender[1], i_name_year_gender[2], i_count]                
            csv_writer.writerow(row)

    # name_set = read_ssa_names(names_directory_path)
    # website_dict = read_website_names(website_file_path)
    # lexicon_dict = read_lexicon(lexicon_file_path)
    # assignment_dict = read_source_assignments(assignment_file_path)

    # identifier_array = [lambda x: identify_date(x),
    #                     lambda x: identify_names(x, name_set),
    #                     lambda x: identify_website(x, assignment_dict)]

    # exclusion_set = {'1080p', '720p', '480p', 'XXX', 'h264'}
    # exclusion_func = lambda x: x in exclusion_set
    
    # (directory_predictor_dict, unknown_char_group_set) = process_directory(working_directory_path, identifier_array, exclusion_func)

    # unknown_groups_file_name_path.write_text('\n'.join(unknown_char_group_set))

    # with output_file_name_path.open('w', newline='', encoding='utf-8') as out_path:
    #     csv_writer = csv.writer(out_path)
    # # 'name', 'original_name', 'path', 'hash', 'date', 'actors', 'source'
    #     csv_writer.writerow(('file_name', 'hash', 'date', 'website', 'actors'))
    #     for file_path, predictor_dict in directory_predictor_dict.items():
    #         metadata = predictors_2_file_metadata(file_path.name, file_path, predictor_dict)

    #         row = [metadata.name, metadata.hash, str(metadata.date), metadata.source, '|'.join(metadata.actors)]                
    #         csv_writer.writerow(row)

    # with unknown_groups_file_name_path.open('w', newline='', encoding='utf-8') as out_path:        
    #     out_path.write('\n'.join(unknown_char_group_set))