import math

#------------------------------------------------------------------------------ 
def is_video_file(in_file):
    video_extensions = {'.avi','.mp4','.mkv','.wmv'}

    if in_file.suffix in video_extensions:
        return True
    else:
        return False
#------------------------------------------------------------------------------ 
def build_recursive_file_list(sub_dir, selection_function=lambda x: True):
    file_list = list()

    for i_path in sub_dir.iterdir():
        if i_path.is_file() and selection_function(i_path):
            file_list.append(i_path)
        elif i_path.is_dir():
            sub_file_list = build_recursive_file_list(i_path, selection_function)            
            file_list.extend(sub_file_list)

    return file_list

#------------------------------------------------------------------------------ 
def set_cosine_metric(l_set, r_set):    
    lr_intersection = l_set.intersection(r_set)

    numerator = len(lr_intersection)
    denominator = len(l_set) * len(r_set)

    return 1 - float(numerator) / denominator
    
#------------------------------------------------------------------------------ 
def weighted_set_cosine_metric(l_set, r_set, weight_dict):    
    lr_intersection = l_set.intersection(r_set)

    l_weights = [weight_dict.get(x,1.0) for x in l_set]
    r_weights = [weight_dict.get(x,1.0) for x in r_set]
    lr_weights = [weight_dict.get(x,1.0) for x in lr_intersection]

    l_norm = math.sqrt(math.fsum( [math.pow(x,-2) for x in l_weights]))
    r_norm = math.sqrt(math.fsum( [math.pow(x,-2) for x in r_weights]))
    lr_norm = math.sqrt(math.fsum( [math.pow(x,-2) for x in lr_weights]))
    
    return 1 - lr_norm / (l_norm*r_norm)

#------------------------------------------------------------------------------ 
# Print iterations progress
def print_progress_bar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    # print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix + ' ' * 50), end = '\r')
    filled_progress = f'{prefix}|{bar}|{percent}%%{suffix}'

    print('\r' + filled_progress + ' ' * 50, end = '\r')
    # Print New Line on Complete
    if iteration == total: 
        print()
            
if __name__ == '__main__':

    print('Miscellaneous Utilities Module')

