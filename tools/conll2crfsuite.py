#!/usr/bin/env python

# Simple feature extractor for CRFsuite. Based on example/ner.py in the
# CRFsuite distribution (https://github.com/chokkan/crfsuite).

import crfutils

import sys
from os import path, getcwd

features = [
    ('', []),
    ('word', [[['word', 0]], [['word', -1]], [['word', 1]]]),
    ('lemma', [[['lemma', 0]]]),
    ('soundex', [[['soundex', 0]]]),
    ('pos', [[['pos', 0]]]),
    ('chunk', [[['chunk', 0]]]),
]

if len(sys.argv) < 4:
    raise RuntimeError("Need to supply paths to train, devel, and test CSVs.")

train_csv = open(path.abspath(path.expanduser(sys.argv[1])), 'r')
devel_csv = open(path.abspath(path.expanduser(sys.argv[2])), 'r')
test_csv = open(path.abspath(path.expanduser(sys.argv[3])), 'r')
ablation_path = path.join(path.dirname(path.dirname(path.realpath(__file__))), 'ablation')
feature_keys = [i[0] for i in features]
feature_items = [i[1] for i in features]

for ablated_feature, _ in features:
    
    input_columns = ''
    attribute_templates = []
    for i, _ in enumerate(feature_keys):
        if feature_keys[i] != ablated_feature and feature_keys[i] != '':
            input_columns += feature_keys[i] + ' '
            attribute_templates += feature_items[i]
    input_columns += 'y'

    print("Using features: {} ({}).".format(input_columns, str(attribute_templates)))

    feature_extractor = lambda x: crfutils.apply_templates(x, attribute_templates)
    
    for fi, txt in [(train_csv, "train"), (devel_csv, "devel"), (test_csv, "test")]:
        write_to = path.join(ablation_path, txt + "_without_" + ablated_feature + ".crfsuite")
        fo = open(write_to, "w+")
        print("Writing to {}...".format(write_to))
        crfutils.main(feature_extractor, fi, fo, fields=input_columns, sep='\t')
        fo.close()

train_csv.close()
devel_csv.close()
test_csv.close()