from __future__ import division
# Script for extracting co-occurence information from grounded associations.

import os, sys
import argparse
from itertools import combinations
from collections import defaultdict
from operator import itemgetter
from math import log
from tabulate import tabulate

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

mentions = defaultdict(int)
associations = defaultdict(int)
total_lines = 0 # Excluding lines without any grounded entities.
while True:

    assoc = assoc_file.readline()
    if not assoc:
        break

    assoc = assoc.strip()
    if len(assoc) > 0:

        # Multiples of the same in a sentence are only counted once.
        elements = sorted(list(set([i.strip() for i in assoc.split(",")])))

        # Generate pairs.
        pairs = combinations(elements, 2)

        # Tally total.
        total_lines += 1

        for pair in pairs:

            # Individual occurrences.
            for item in pair:
                mentions[item] += 1

            # If set, only consider pairs of chemical and disease.
            # Dictionary composition: {id: (name, type), ...}
            if MIXED_ONLY:
                first_t = dictionary[pair[0]][1]
                second_t = dictionary[pair[1]][1]
                if first_t.lower() == second_t.lower():
                    continue
            
            # Co-occurrences.
            associations[pair] += 1

assoc_file.close()


print("Top 10 Chemicals:")
chemicals = sorted(filter(lambda x: dictionary[x[0]][1].lower() == "chemical", mentions.items()), key=itemgetter(1), reverse=True)[:10]
for c in chemicals:
    identity = c[0]
    name = dictionary[identity][0]
    print("{} ({:0.3f}%) - {} ({})".format(c[1], c[1]/total_lines, identity, name))
print("")

print("Top 10 Diseases:")
diseases = sorted(filter(lambda x: dictionary[x[0]][1].lower() == "disease", mentions.items()), key=itemgetter(1), reverse=True)[:10]
for c in diseases:
    identity = c[0]
    name = dictionary[identity][0]
    print("{} ({:0.3f}%) - {} ({})".format(c[1], c[1]/total_lines, identity, name))
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
    print("{} ({:0.5f}%) - {} ({}, {}) and {} ({}, {})".format(c[1], c[1]/total_lines, first, first_c, first_t, second, second_c, second_t))
print("")

# Lines without any grounded entities are excluded from the total, while any line with
# any grounded chemical or disease at all are counted, not requiring both types to appear.
# This keeps probabilities consistent between chemical and disease entities.
element_prob = {i: mentions[i] / total_lines for i in mentions}
joint_prob = {i: associations[i] / total_lines for i in associations}
pmi = {i: log(joint_prob[i] / (element_prob[i[0]] * element_prob[i[1]]), 2) for i in joint_prob}
npmi = {i: pmi[i] / (-1 * log(joint_prob[i], 2)) for i in pmi}
scp = {i: joint_prob[i] ** 2 / (element_prob[i[0]] * element_prob[i[1]]) for i in joint_prob}
jaccard = {i: associations[i] / (mentions[i[0]] + mentions[i[1]] - associations[i]) for i in associations}

print("Top 10 co-mentions by PMI (log base 2): ")
co_mentions = sorted(pmi.items(), key=itemgetter(1), reverse=True)[:10]
header = ("PMI", "MESH ID", "Name", "MESH ID", "Name")
rows = []
for c in co_mentions:
    first = c[0][0]
    first_c = dictionary[first][0]
    first_t = dictionary[first][1]
    second = c[0][1]
    second_c = dictionary[second][0]
    second_t = dictionary[second][1]
    if first_t.lower() == "chemical":
        rows.append((c[1], first, first_c, second, second_c))
    else:
        rows.append((c[1], second, second_c, first, first_c))
    print("PMI {:0.5f} - {} ({}, {}) and {} ({}, {})".format(c[1], first, first_c, first_t, second, second_c, second_t))
print("")
print(tabulate(rows, header, tablefmt="latex"))
print("")

print("Top 10 co-mentions by Normalised PMI (log base 2): ")
co_mentions = sorted(npmi.items(), key=itemgetter(1), reverse=True)[:10]
header = ("NPMI", "MESH ID", "Name", "MESH ID", "Name")
rows = []
for c in co_mentions:
    first = c[0][0]
    first_c = dictionary[first][0]
    first_t = dictionary[first][1]
    second = c[0][1]
    second_c = dictionary[second][0]
    second_t = dictionary[second][1]
    if first_t.lower() == "chemical":
        rows.append((c[1], first, first_c, second, second_c))
    else:
        rows.append((c[1], second, second_c, first, first_c))
    print("NPMI {:0.5f} - {} ({}, {}) and {} ({}, {})".format(c[1], first, first_c, first_t, second, second_c, second_t))
print("")
print(tabulate(rows, header, tablefmt="latex"))
print("")

print("Top 10 co-mentions by Symmetric Conditional Probability: ")
co_mentions = sorted(scp.items(), key=itemgetter(1), reverse=True)[:10]
header = ("SCP", "MESH ID", "Name", "MESH ID", "Name")
rows = []
for c in co_mentions:
    first = c[0][0]
    first_c = dictionary[first][0]
    first_t = dictionary[first][1]
    second = c[0][1]
    second_c = dictionary[second][0]
    second_t = dictionary[second][1]
    if first_t.lower() == "chemical":
        rows.append((c[1], first, first_c, second, second_c))
    else:
        rows.append((c[1], second, second_c, first, first_c))
    print("SCP {:0.5f} - {} ({}, {}) and {} ({}, {})".format(c[1], first, first_c, first_t, second, second_c, second_t))
print("")
print(tabulate(rows, header, tablefmt="latex"))
print("")

print("Top 10 co-mentions by Jaccard Index: ")
co_mentions = sorted(npmi.items(), key=itemgetter(1), reverse=True)[:10]
header = ("Jaccard Index", "MESH ID", "Name", "MESH ID", "Name")
rows = []
for c in co_mentions:
    first = c[0][0]
    first_c = dictionary[first][0]
    first_t = dictionary[first][1]
    second = c[0][1]
    second_c = dictionary[second][0]
    second_t = dictionary[second][1]
    if first_t.lower() == "chemical":
        rows.append((c[1], first, first_c, second, second_c))
    else:
        rows.append((c[1], second, second_c, first, first_c))
    print("Jaccard Index {:0.5f} - {} ({}, {}) and {} ({}, {})".format(c[1], first, first_c, first_t, second, second_c, second_t))
print("")
print(tabulate(rows, header, tablefmt="latex"))
print("")
