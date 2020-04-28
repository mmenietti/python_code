#------------------------------------------------------------
# Dependencies
#------------------------------------------------------------
import pathlib
import csv
import argparse
import collections
import datetime
import hashlib
import math
import itertools
import exifread
import mm.text_utilities
import mm.misc_utilities
#------------------------------------------------------------
# 
#------------------------------------------------------------
FilePredictors = collections.namedtuple('FilePredictors', ['name', 'path', 'tokens', 'hash'])
FileMetaData   = collections.namedtuple('FileMetaData', ['name', 'original_name', 'path', 'hash', 'date', 'actors', 'source'])

def split_filename(in_string):
    char_group_array = []
    
    delimiter_groups_array = mm.text_utilities.split_delimiters(in_string)
    camel_case_groups_array = [mm.text_utilities.split_camel_case(x) for x in delimiter_groups_array]

    for i_list in camel_case_groups_array:
        char_group_array.extend(i_list)

    return char_group_array

def read_names(names_file_path):    
    name_set = set()

    with names_file_path.open('r', newline='', encoding='utf-8') as file_path:
        name_records = csv.reader(file_path)
        for row in name_records:
            name_set.add(row[0].casefold())

    return name_set

def read_lexicon(file_path):    
    lexicon = dict()

    with file_path.open('r', newline='', encoding='utf-8') as file_reader:
        csv_reader = csv.reader(file_reader)
        for row in csv_reader:
            lexicon[row[0]] = float(row[1])
    return lexicon

def read_source_assignments(file_path):    
    source_dict = dict()

    with file_path.open('r', newline='', encoding='utf-8') as file_path:
        assignments = csv.reader(file_path)
        for row in assignments:
            file_name = row[0]
            source = row[1]

            name_groups =  frozenset([x.casefold() for x in split_filename(file_name)])

            char_group_set = source_dict.get(source, set())
            char_group_set.add(name_groups)

            source_dict[source] = char_group_set

    return source_dict


def read_source_alias(file_path):    
    source_alias_dict = dict()

    with file_path.open('r', newline='', encoding='utf-8') as file_path:
        name_records = csv.reader(file_path)
        for row in name_records:
            canonical_name = row[0]
            name_groups =  [x.casefold() for x in split_filename(row[0])]
            alias_groups =  [x.casefold() for x in split_filename(row[1])]

            source_alias_dict[canonical_name] = (frozenset(name_groups), frozenset(alias_groups))

    return source_alias_dict

def predictors_2_file_metadata(file_name, file_path, predictors):

    token_dict = predictors.tokens

    if 'date' in token_dict:
        token_list = token_dict['date']
        date_parts = token_list[0].value
        date = datetime.date(year = date_parts.year, month=date_parts.month, day=date_parts.day)
    else:
        date = datetime.date.min

    if 'source' in token_dict:
        token_list = token_dict['source']
        source = token_list[0].value
    else:
        source = ''

    if 'name' in token_dict:
        token_list = token_dict['name']
        actors = set([x.value for x in token_list])
    else:
        actors = []

    return FileMetaData(name=file_name, original_name=file_name, path=file_path, hash=predictors.hash,  date=date, actors=actors, source=source)

def identify_feasible_date_parts(in_digits):
    parts = set()

    is_year = ((in_digits >= 2015) and (in_digits <= 2020))\
            or((in_digits >= 14) and (in_digits <= 19))

    is_month = (in_digits >= 1) and (in_digits <= 12)

    is_day = (in_digits >= 1) and (in_digits <= 31)

    if is_year:
        parts.add('Y')

    if is_month:
        parts.add('M')
    
    if is_day:
        parts.add('D')

    if not (is_year or is_month or is_day):
        parts.add('N')

    return ''.join(parts)

def identify_date(in_char_group_list):
    
    folded_char_group_list = [x.casefold() for x in in_char_group_list]
    
    token_list = []
    unknown_char_group_set = set(folded_char_group_list)

    
    feasible_parts = []
    int_values = []
    for i_group in folded_char_group_list:
        if i_group.isdigit():
            int_values.append(int(i_group))
            feasible_parts.append(identify_feasible_date_parts(int_values[-1]))
        else:
            int_values.append(0)
            feasible_parts.append('N')

    for k in range(len(folded_char_group_list)-2):            
        parts_slice = feasible_parts[k:k+3]
        int_slice = int_values[k:k+3]
        char_group_slice = folded_char_group_list[k:k+3]

        if 'D' in parts_slice[0] and 'M' in parts_slice[1] and 'Y' in parts_slice[2]:
            if int_slice[2] < 100:
                year = int_slice[2] + 2000
            else:
                year = int_slice[2]

            date_value = mm.text_utilities.DateParts(year=year, month=int_slice[1], day=int_slice[0])
            token_list.append(mm.text_utilities.Token(type = 'date', confidence = 1, value=date_value, char_group=char_group_slice, position=k))

            unknown_char_group_set = unknown_char_group_set.difference(char_group_slice)

        elif 'Y' in parts_slice[0] and 'M' in parts_slice[1] and 'D' in parts_slice[2]:
            if int_slice[2] < 100:
                year = int_slice[0] + 2000
            else:
                year = int_slice[0]

            date_value = mm.text_utilities.DateParts(year=year, month=int_slice[1], day=int_slice[2])
            token_list.append(mm.text_utilities.Token(type = 'date', confidence = 1, value=date_value, char_group=char_group_slice, position=k))
            
            unknown_char_group_set = unknown_char_group_set.difference(char_group_slice)

    return (token_list, unknown_char_group_set)

def source_distance(focal_char_group_set, source_dict):

    distance_dict = dict()

    for i_source, i_char_group_set in source_dict.items():
        distance_dict[i_source] = set()
        for i_char_group in i_char_group_set:
            distance = mm.misc_utilities.set_cosine_metric(focal_char_group_set, i_char_group)
            distance_dict[i_source].add(distance)

    return distance_dict

def identify_website(char_group_array, source_dict, source_alias):    

    focal_folded_group_set = set([x.casefold() for x in char_group_array])

    distance_dict = source_distance(focal_folded_group_set, source_dict)

    mean_distance_dict = dict()

    for i_source, i_distance_set in distance_dict.items():
        sum_distance = math.fsum(i_distance_set)
        n_distances = len(i_distance_set)

        mean_distance_dict[i_source] = sum_distance / n_distances

    min_mean_distance_item = min(mean_distance_dict.items(), key=lambda x: x[1])

    token = mm.text_utilities.Token(type='source',
                                    value=min_mean_distance_item[0],
                                    confidence = 1-min_mean_distance_item[1], 
                                    char_group= char_group_array,
                                    position=None)

    unknown_char_group_set = focal_folded_group_set.difference(source_alias[min_mean_distance_item[0]])

    return ([token], unknown_char_group_set)

def identify_names(char_group_array, name_set):
    id_names = []
    unknown_char_group_set = set()

    for k, i_group in enumerate(char_group_array):
        folded_group = i_group.casefold()
        if folded_group in name_set:
            id_names.append(mm.text_utilities.Token(type='name',confidence=1, value=folded_group, char_group= i_group, position=k))
        else:
            unknown_char_group_set.add(folded_group)

    return (id_names, unknown_char_group_set)

def hash_file(in_file_path, max_bytes = 5*2^20):
    BUF_SIZE = 8 * 2**10 # Read in 8KB chunks

    (whole_iterations, partial_bytes) = divmod(max_bytes, BUF_SIZE)
    if partial_bytes > 0:
        max_iterations = whole_iterations + 1
    else:
        max_iterations = whole_iterations

    hash_function = hashlib.sha256()

    with in_file_path.open(mode='rb') as f:
        data = f.read(BUF_SIZE)
        itr_count = 1

        while data and itr_count <= max_iterations:
            hash_function.update(data)
            data = f.read(BUF_SIZE)
            itr_count += 1

    return hash_function.hexdigest()
    # return '--------------NOT_A_HASH----------------'

def tokenize_filename(in_path, identifier_array):
    char_group_array = split_filename(in_path.stem)

    return mm.text_utilities.tokenize_char_group_array(char_group_array, identifier_array)

def process_file_path(in_path, max_hash_bytes, identifier_array):
    (token_dict, file_unknown_char_group_set) = tokenize_filename(in_path, identifier_array)
        
    hash_digest = hash_file(in_file_path=in_path, max_bytes=max_hash_bytes)

    predictors = FilePredictors(name=in_path.name, path=in_path, tokens=token_dict, hash=hash_digest)

    return (predictors, file_unknown_char_group_set)

if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description='Process path string.')
    # parser.add_argument('input_directory')
    # args = parser.parse_args()
          
    
    
    # I/O Paths    
    #---------------------------------------------------------------------------------------------------    
    # Directory to Process
    working_directory_path = pathlib.Path(r'D:\other\pictures\amateur')    
    
    # Process output
    output_file_name_path = pathlib.Path(r'./image_exif_data.txt')
    
    # # Unidentified char groups
    # unknown_groups_file_name_path = pathlib.Path(r'./data_files/unknown_char_groups.txt')

    # # Names database
    # names_file_path = pathlib.Path(r'./data_files/name_dataset.csv')

    # # Source names and aliases
    # source_alias_file_path = pathlib.Path(r'./data_files/source_aliases.csv')

    # # Ground true dataset of (file name, source) pairs
    # assignment_file_path = pathlib.Path(r'./data_files/filename_sources.csv')    
    
    # Processing
    #---------------------------------------------------------------------------------------------------
    # name_set          = read_names(names_file_path)
    # source_dict       = read_source_assignments(assignment_file_path)
    # source_alias_dict = read_source_alias(source_alias_file_path)

    # identifier_array = [lambda x: identify_date(x),
    #                     lambda x: identify_names(x, name_set),
    #                     lambda x: identify_website(x, source_dict, source_alias_dict)]

    file_filter = lambda x: x.suffix in {'.jpg'}

    file_list = mm.misc_utilities.build_recursive_file_list(working_directory_path, file_filter)
    
    # Small for testing
    file_list = file_list[0:10]

    for i_path in file_list:
        with i_path.open('rb') as image_file:
            print('-'*80)
            print('Tags from: ' + i_path.stem)
            print('-'*80)
            tags = exifread.process_file(image_file)
            for i_tag, i_value in tags.items():
                if 'Thumbnail' not in i_tag:
                    print('Key: {}, value {}'.format(i_tag, i_value))
                else:
                    print('Key: {}, value {}'.format(i_tag, 'Thumbnail Data'))
            
            print('-'*80)
            
            image_data = image_file.read()
            
            xmp_start = image_data.find(b'<x:xmpmeta')
            xmp_end = image_data.find(b'</x:xmpmeta')
            xmp_str = image_data[xmp_start:xmp_end+12]
            
            print(xmp_str)   

    # for i_path in file_list:
    #     with i_path.open('rb') as image_file:
    #         print('-'*80)
    #         print('Tags from: ' + i_path.stem)
    #         print('-'*80)
    #         image_data = image_file.read()
            
    #         xmp_start = image_data.find(b'<x:xmpmeta')
    #         xmp_end = image_data.find(b'</x:xmpmeta')
    #         xmp_str = image_data[xmp_start:xmp_end+12]
            
    #         print(xmp_str)            

    
    

    # for k, i_path in enumerate(file_list):
    #     mm.misc_utilities.print_progress_bar (k, n_files, prefix = '', suffix = ' Working on: ' + i_path.stem, decimals = 1, length = 100, fill = '█')

    #     (file_predictors, unknown_char_groups) = process_file_path(i_path, max_hash_bytes, identifier_array)
    #     file_predictors_list.append(file_predictors)
    #     unknown_char_group_list.append(unknown_char_groups)
    
    # mm.misc_utilities.print_progress_bar (n_files, n_files, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█')

    # unknown_char_group_set = set(itertools.chain.from_iterable(unknown_char_group_list))
    # unknown_groups_file_name_path.write_text('\n'.join(unknown_char_group_set))

    # Output
    #---------------------------------------------------------------------------------------------------
    # file_name_format = r'{}-{}-{}{}'
    # date_format      = r'%Y_%m_%d'
    # column_names     = ('file_path', '_'.join(['hash','sha256', str(max_hash_bytes / 2**20 ), 'MB']), 'date', 'source', 'actors', 'unknown_tokens')
    # file_extensions  = {'wmv','mp4','mkv','avi', 'mov'}

    # with output_file_name_path.open('w', newline='', encoding='utf-8') as out_path:
    #     csv_writer = csv.writer(out_path)
    #     csv_writer.writerow(column_names)
    #     for i_file_predictors, i_unknown_char_groups in zip(file_predictors_list, unknown_char_group_list):
            
    #         metadata = predictors_2_file_metadata(i_file_predictors.name, i_file_predictors.path, i_file_predictors)
    #         i_unknown_char_groups = i_unknown_char_groups - file_extensions            

    #         row = [metadata.path, metadata.hash, str(metadata.date), metadata.source, '|'.join(metadata.actors), '|'.join(i_unknown_char_groups)]
    #         csv_writer.writerow(row)