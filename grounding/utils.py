from os import path
from fuzzywuzzy import process

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


def open_file(input_file):
    """
    Open d file at `input_file.` Return the file object.
    """

    full_path = get_full_path(input_file)
    if not path.isfile(full_path):
        return False

    return open(full_path, 'r')


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


def make_sentences(words, tags):
    """
    Organise a 1-D list of words into a 2-D list of sentences, each
    of which containing tuples of lemma and tag.
    """

    sentences = []
    current_sentence = []
    # Information collected: (lemma, recognised_tag)
    for i, word in enumerate(words):
        if len(word) < 6:
            sentences.append(current_sentence)
            current_sentence = []
        else:
            current_sentence.append((word[1], tags[i]))

    if current_sentence != []:
        sentences.append(current_sentence)

    return sentences