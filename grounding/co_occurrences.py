# Script for extracting co-occurence information from grounded associations.

import os, sys
import argparse
from itertools import combinations
from collections import defaultdict
from operator import itemgetter

import utils

MIXED_ONLY = True # Only identify chemical and disease associations and exclude C-C and D-D.

parser = argparse.ArgumentParser()
parser.add_argument("-a", "--associations", help="A file with either empty lines or lines of comma-separated dict entries.", default="./associations.txt")
parser.add_argument("-d", "--dictionary", help="A tab separated file containing terms for reference.", default="./CDR_MeSH.tsv")
args = parser.parse_args()

# Build the dictionary first.
dictionary = utils.parse_tsv(args.dictionary)
if len(dictionary) == 0:
    print("Error: read an empty dictionary, check the tsv.")
    sys.exit(1)
dictionary = {i[2]: (i[0], i[1]) for i in dictionary}

assoc_file = utils.open_file(args.associations)
if not assoc_file:
    print("Error: invalid path to the associations file.")
    sys.exit(1)

chemical_mentions = defaultdict(int)
disease_mentions = defaultdict(int)
associations = defaultdict(int)
while True:

    assoc = assoc_file.readline()
    if not assoc:
        break

    assoc = assoc.strip()
    if len(assoc) > 0:
        elements = sorted([i.strip() for i in assoc.split(",")])
        pairs = combinations(elements, 2)
        for pair in pairs:

            for item in pair:
                if dictionary[item][1].lower() == "chemical":
                    chemical_mentions[item] += 1
                else:
                    disease_mentions[item] += 1

            if MIXED_ONLY:
                first_t = dictionary[pair[0]][1]
                second_t = dictionary[pair[1]][1]
                if first_t.lower() == second_t.lower():
                    continue
            
            associations[pair] += 1

assoc_file.close()


print("Top 10 Chemicals:")
chemicals = sorted(chemical_mentions.items(), key=itemgetter(1), reverse=True)[:10]
for c in chemicals:
    identity = c[0]
    name = dictionary[identity][0]
    print("{} - {} ({})".format(c[1], identity, name))
print("")

print("Top 10 Diseases:")
diseases = sorted(disease_mentions.items(), key=itemgetter(1), reverse=True)[:10]
for c in diseases:
    identity = c[0]
    name = dictionary[identity][0]
    print("{} - {} ({})".format(c[1], identity, name))
print("")

if MIXED_ONLY:
    print("Considering co-mentions between chemicals and diseases only!\n")

print("Top 10 co-mentions:")
co_mentions = sorted(associations.items(), key=itemgetter(1), reverse=True)[:10]
for c in co_mentions:
    first = c[0][0]
    first_c = dictionary[first][0]
    first_t = dictionary[first][1]
    second = c[0][1]
    second_c = dictionary[second][0]
    second_t = dictionary[second][1]
    print("{} - {} ({}, {}) and {} ({}, {})".format(c[1], first, first_c, first_t, second, second_c, second_t))


        
    
    