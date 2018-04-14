# Script to ground tagged entities to dictionary entries.

import os, sys
import argparse
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

words = []
current_sentence = ""
current_grounded_terms = []
current_reference = 0
for i, word in enumerate(original):

    if len(word) < 6:
        # It is an empty line signalling a new sentence.
        print(current_sentence)
        for i, t, s in current_grounded_terms:
            print("[" + str(i) + "] " + t + " (Score: " + str(s) + ")")
        current_reference = 0
        current_sentence = ""
        current_grounded_terms = []
        print("\n")
        continue
        
    # Exclude those outside recognised entities.
    if 'chemical' not in tags[i].lower() and 'disease' not in tags[i].lower():
        current_sentence += " " + word[0]
        continue

    # Find the best match from chemical choices.
    elif 'chemical' in tags[i].lower():
        best_match = process.extractOne(word[1], chemical_choices)
    
    # Find the best match from disease choices.
    else:
        best_match = process.extractOne(word[1], disease_choices)
    
    # Record groundings of recognised terms.
    current_reference += 1
    current_sentence += " *" + word[0] + "*[" + str(current_reference) + "]"
    current_grounded_terms.append((current_reference, best_match[0], best_match[1]))

# Sort out the last bit.
if len(current_sentence) > 0:
    print(current_sentence)
    for i, t, s in current_grounded_terms:
        print("[" + str(i) + "] " + t + " (Score: " + str(s) + ")")

print("\n")
print("(End of grounding.)")
        




    
