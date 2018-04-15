# Script to ground tagged entities to dictionary entries in a 
# memory-friendly manner.

import os, sys
import argparse
from multiprocessing import Pool
from fuzzywuzzy import process

import utils

CHUNK_SIZE = 50 # Sentence chunks.
BATCH_SIZE = 10000 # Word batches -- approximate due to line breaks.

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--dictionary", help="A tab separated file containing terms to be grounded to.", default="./CDR_MeSH.tsv")
parser.add_argument("-t", "--tags", help="A text file containing corresponding entity recognition tags on each line.")
parser.add_argument("-i", "--input", help="A tab separated file containing original terms before entity recognition.")
parser.add_argument("-o", "--output", help="The optional path to which a file containing grounded terms in each sentence will be written.", default="_")
args = parser.parse_args()

if any([i is None for i in [args.tags, args.input, args.dictionary]]):
    parser.print_help()
    sys.exit(1)

output_file = utils.get_write_path(args.output)
out = open(output_file, 'w+')

# Build the disease and chemical dictionary choices separately.
dictionary = utils.parse_tsv(args.dictionary)
if len(dictionary) == 0:
    print("Error: read an empty dictionary, check the tsv.")
    sys.exit(1)

chemical_choices = {i[2]: i[0] for i in dictionary if i[1].lower() == "chemical"}
disease_choices = {i[2]: i[0] for i in dictionary if i[1].lower() == "disease"}

def process_sentence(sentence):
    """ Return a string of grounded terms in comma separated IDs within the sentence. """

    current_entity = []
    current_entity_class = ""
    grounded_terms_ids = []

    for word in sentence:
        tag = word[1].strip().lower()
        
        # The end of the previous entity.
        if tag.startswith("b") or tag.startswith("o"):
            if len(current_entity) > 0:
                # Match and output this assembled entity.
                assembled_entity = " ".join(current_entity)
                if current_entity_class == "chemical":
                    match = process.extractOne(assembled_entity, chemical_choices)
                else:
                    match = process.extractOne(assembled_entity, disease_choices)
                grounded_terms_ids.append(match[2])
            
            # Clear current states
            current_entity = []
            current_entity_class = ""

            if tag.startswith("b"):
                if "chemical" in tag:
                    current_entity_class = "chemical"
                else:
                    current_entity_class = "disease"
                current_entity.append(word[0])
        
        elif tag.startswith("i"):
            current_entity.append(word[0])
        

    if len(current_entity) > 0:
        # Match and output the last assembled entity.
        assembled_entity = " ".join(current_entity)
        if current_entity_class == "chemical":
            match = process.extractOne(assembled_entity, chemical_choices)
        else:
            match = process.extractOne(assembled_entity, disease_choices)
        grounded_terms_ids.append(match[2])

    return ','.join(grounded_terms_ids)

pool = Pool()

tag_file = utils.open_file(args.tags)
input_file = utils.open_file(args.input)
tag = tag_file.readline()
word = input_file.readline()

if not tag or not word:
    print("Error: empty original input or tags.")
    sys.exit(1)

tags = []
words = []
total = 1

while tag and word:

    tag = tag.strip()
    word = word.strip()
    tags.append(tag)
    word_items = word.split('\t')
    words.append(word_items)

    if len(word_items) < 6:
        if len(words) > BATCH_SIZE:
            sentences = utils.make_sentences(words, tags)
            output_ids = ["" for i in range(len(sentences))]
            for ind, result in enumerate(pool.map(process_sentence, sentences, CHUNK_SIZE)):
                output_ids[ind] = result
            for i in output_ids:
                out.write(i + "\n")
            print("Processed {} words in {} sentences, total processed {} words.".format(len(words), len(sentences), total))
            tags = []
            words = []

    tag = tag_file.readline()
    word = input_file.readline()
    total += 1

if len(words) > 0:
    sentences = utils.make_sentences(words, tags)
    output_ids = ["" for i in range(len(sentences))]
    for ind, result in enumerate(pool.map(process_sentence, sentences, CHUNK_SIZE)):
        output_ids[ind] = result
    for i in output_ids:
        out.write(i + "\n")
    print("Processed {} words in {} sentences, total processed {} words.".format(len(words), len(sentences), total))

out.close()
tag_file.close()
input_file.close()


    
