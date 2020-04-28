#------------------------------------------------------------
# Dependencies
#------------------------------------------------------------
import pathlib
import csv
import argparse
import collections
import dateutil.parser
import hashlib
import math
import itertools
import mm.text_utilities
import mm.misc_utilities
#------------------------------------------------------------
# 
#------------------------------------------------------------
FileMetaData = collections.namedtuple('FileMetaData', ['path', 'hash', 'date', 'actors', 'source', 'unknown_char_groups'])

def read_file_info(file_info_path):    
    file_info_set = set()

    with file_info_path.open('r', newline='', encoding='utf-8') as file_path:
        file_records = csv.reader(file_path)
        for row in file_records:
            file_info_set.add(
                FileMetaData(
                    path=pathlib.Path(row[0]),
                    hash=row[1],
                    date=frozenset([dateutil.parser.parse(x) for x in row[2].split('|')]),
                    source=row[3],
                    actors=frozenset(row[4].split('|')),
                    unknown_char_groups=frozenset(row[5].split('|'))
                )
            )

    return file_info_set

def process_file(file_info, root_path):    
    file_name_format = r'{}-{}-{}-{}{}'
    date_format      = r'%Y_%m_%d'

    file_name_parts = [file_info.source, '_'.join([x.strftime(date_format) for x in file_info.date]), '_'.join(file_info.actors), '_'.join(file_info.unknown_char_groups), file_info.path.suffix]
    file_name = file_name_format.format(*file_name_parts)

    source_subdirectory = root_path.joinpath(file_info.source)
    new_file_path = source_subdirectory.joinpath(file_name)

    # Make subdirectory for source if needed
    source_subdirectory.mkdir(exist_ok=True)

    # Ensure Uniqueness
    counter = 0
    original_stem = new_file_path.stem
    original_suffix = new_file_path.suffix
    while new_file_path.exists():
        counter += 1
        new_file_path = new_file_path.with_name(original_stem + '-' + str(counter) + original_suffix)
    
    # Rename and Move file
    if file_info.path.exists():
        # print(new_file_path)
        file_info.path.rename(new_file_path)

if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description='Process path string.')
    # parser.add_argument('input_directory')
    # args = parser.parse_args()
    
    # I/O Paths    
    #---------------------------------------------------------------------------------------------------    
    # Input file info
    file_info_path = pathlib.Path(r'C:\Users\micha\Documents\python\scripts\usenet_file_tools\parsed_usenet_files_corrected.csv')    
    
    # Base Directory to move files to 
    output_root_path = pathlib.Path(r'E:\usenet')

    # Processing
    #---------------------------------------------------------------------------------------------------
    file_info_set = read_file_info(file_info_path)

    for i_info in file_info_set:
        process_file(i_info, output_root_path)

    # # Testing Alternate Output
    # #---------------------------------------------------------------------------------------------------    
    # # I/O Paths    
    # #---------------------------------------------------------------------------------------------------
    # # Output file info
    # out_file_info_path = pathlib.Path(r'C:\Users\micha\Documents\python\scripts\usenet_organizer_output.csv')    

    # # Processing
    # #---------------------------------------------------------------------------------------------------
    # file_info_set = read_file_info(file_info_path)
    # file_name_dict = dict()

    # file_name_format = r'{}-{}-{}-{}{}'
    # date_format      = r'%Y_%m_%d'

    # for i_info in file_info_set:
    #     file_name_parts = [i_info.source, i_info.date.strftime(date_format), '_'.join(i_info.actors), '_'.join(i_info.unknown_char_groups), i_info.path.suffix]
    #     file_name = file_name_format.format(*file_name_parts)

    #     file_name_dict[i_info.path] = file_name

    # # Output
    # #---------------------------------------------------------------------------------------------------
    # with out_file_info_path.open('w', newline='', encoding='utf-8') as out_path:
    #     csv_writer = csv.writer(out_path)
    #     csv_writer.writerow(['Original', 'new'])
    #     for i_path, i_new_name in file_name_dict.items():            
    #         row = [i_path.name, i_new_name]
    #         csv_writer.writerow(row)
