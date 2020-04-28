import re
import collections

#------------------------------------------------------------------------------    
DateParts = collections.namedtuple('DateParts', ['day', 'month', 'year'])
SplitString = collections.namedtuple('SplitString', ['original', 'char_groups'])
Token = collections.namedtuple('Token', ['type', 'value', 'confidence', 'position', 'char_group'])

#------------------------------------------------------------------------------    
def split_delimiters(in_string):    
    return re.split(r'[-|\s\W+_]', in_string)

#------------------------------------------------------------------------------    
def split_camel_case(in_string):
    matches = re.finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', in_string)
    return [m.group(0) for m in matches]

#------------------------------------------------------------------------------    
def tokenize_char_group_array(in_char_group_array, identifier_array):
    token_dict = dict()
    unknown_char_group_set = set(in_char_group_array)
        

    for i_id in identifier_array:
        (token_list, unknown_group_set) = i_id(in_char_group_array)

        unknown_char_group_set = unknown_char_group_set.intersection(unknown_group_set)  

        for token in token_list:
            updated_token_list = token_dict.get(token.type,[])
            updated_token_list.append(token)

            token_dict[token.type] = updated_token_list

    return (token_dict, unknown_char_group_set)

#------------------------------------------------------------------------------    
if __name__ == '__main__':

    print('Text Utilities Module')
    print('Splitting|This.Text_On Delimiters')
    print(split_delimiters('Splitting|This.Text_On Delimiters'))
    print('SplittingThisCamelCaseText')
    print(split_camel_case('SplittingThisCamelCaseText'))