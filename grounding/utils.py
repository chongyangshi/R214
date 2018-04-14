from os import path

def get_full_path(file_path):
    """
    Return the full path to a file.
    """

    return path.abspath(path.expanduser(file_path))


def get_write_path(file_path):
    """
    Given the path to a non-existent file, returns the full path to write by
    expanding any user prefixes. 
    """

    directory = path.dirname(file_path)
    full_dir = path.abspath(path.expanduser(directory))

    if not path.isdir(full_dir):
        return None

    return path.join(full_dir, path.basename(file_path))


def parse_tsv(input_tsv):
    """
    Open and parse a tab separated file at `input_tsv.` Return 
    a 2-D list of parsed data, which contains empty lines (len < 3)
    signalling a break in sentences.
    """

    full_path = get_full_path(input_tsv)
    if not path.isfile(full_path):
        return False

    with open(full_path, 'r') as tsv:
        content = tsv.readlines()

    parsed_data = [i.strip().split('\t') for i in content]

    return parsed_data


def read_tags(input_file):
    """
    Open and read a text file containing tags from entity recognition
    on each line. Returns a 1-D list of tags, which contains empty lines 
    (len < 3) signalling a break in sentences.
    """

    full_path = get_full_path(input_file)
    if not path.isfile(full_path):
        return False

    with open(full_path, 'r') as tags_file:
        content = tags_file.readlines()

    parsed_data = [i.strip() for i in content]

    return parsed_data