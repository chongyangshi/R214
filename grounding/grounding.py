# Script to ground tagged entities to dictionary entries.

import os, sys
import argparse
from multiprocessing import Pool
from itertools import product
from fuzzywuzzy import process

import utils

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--dictionary", help="A tab separated file containing terms to be grounded to.", default="./CDR_MeSH.tsv")
parser.add_argument("-t", "--tags", help="A text file containing corresponding entity recognition tags on each line.")
parser.add_argument("-i", "--input", help="A tab separated file containing original terms before entity recognition.")
args = parser.parse_args()

if any([i is None for i in [args.tags, args.input, args.dictionary]]):
    parser.print_help()
    sys.exit(1)

tags = utils.read_tags(args.tags)
original = utils.parse_tsv(args.input)
dictionary = utils.parse_tsv(args.dictionary)

if len(original) != len(tags):
    print("Error: mismatching original inputs and tags ({} and {}).".format(len(original), len(tags)))
    sys.exit(1)

if len(dictionary) == 0:
    print("Error: read an empty dictionary, check the tsv.")
    sys.exit(1)

# Build the disease and chemical dictionary choices separately.
chemical_choices = [i[0] for i in dictionary if i[1].lower() == "chemical"]
disease_choices = [i[0] for i in dictionary if i[1].lower() == "disease"]

# First, organise original inputs back into sentences.
sentences = []
current_sentence = []
# Information collected: (word, lemma, recognised_tag)
for i, word in enumerate(original):
    if len(word) < 6:
        sentences.append(current_sentence)
        current_sentence = []
    else:
        current_sentence.append((word[0], word[1], tags[i]))

if current_sentence != []:
    sentences.append(current_sentence)

# Then, within each sentence, annotate and match segments assembling entities.
# Parallised with horrible code here.
def process_sentence(sentence):

    result = ""
    current_entity_surface = ""
    current_entity = []
    current_entity_class = ""
    grounded_terms = []
    sentence_out = ""
    current_reference = 0

    for word in sentence:
        tag = word[2].strip().lower()
        
        # The end of the previous entity.
        if tag.startswith("b") or tag.startswith("o"):
            if len(current_entity) > 0:
                # Match and output this assembled entity.
                assembled_entity = " ".join(current_entity)
                if current_entity_class == "chemical":
                    match = process.extractOne(assembled_entity, chemical_choices)
                else:
                    match = process.extractOne(assembled_entity, disease_choices)
                current_reference += 1
                sentence_out += "**" + current_entity_surface + "** {" + str(current_reference) + "} "
                grounded_terms.append((current_reference, match[0], match[1]))
            
            # Clear current states
            current_entity_surface = ""
            current_entity = []
            current_entity_class = ""

            if tag.startswith("b"):
                if "chemical" in tag:
                    current_entity_class = "chemical"
                else:
                    current_entity_class = "disease"
                current_entity_surface += word[0] + " "
                current_entity.append(word[1])
            else:
                sentence_out += word[0] + " "
        
        elif tag.startswith("i"):
            current_entity_surface += word[0] + " "
            current_entity.append(word[1])
        

    if len(current_entity) > 0:
        # Match and output the last assembled entity.
        assembled_entity = " ".join(current_entity)
        if current_entity_class == "chemical":
            match = process.extractOne(assembled_entity, chemical_choices)
        else:
            match = process.extractOne(assembled_entity, disease_choices)
        current_reference += 1
        sentence_out += "**" + current_entity_surface + "** {" + str(current_reference) + "} "
        grounded_terms.append((current_reference, match[0], match[1]))

    result = ""
    result += sentence_out + "\n"
    for i, t, s in grounded_terms:
        result += "{" + str(i) + "} " + t + " (Score: " + str(s) + ")\n"
    result += "\n"

    return result

outputs = len(sentences)
output = ["" for i in range(outputs)]
pool = Pool()
chunksize = 50
for ind, result in enumerate(pool.map(process_sentence, sentences, chunksize)):
    output[ind] = result

for result in output:
    print(result)
print("\n")
print("(End of grounding.)")
        




    
