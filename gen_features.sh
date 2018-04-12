#!/bin/sh

python tools/conll2crfsuite.py BC5-CDR/conll/train.tsv BC5-CDR/conll/devel.tsv BC5-CDR/conll/test.tsv
python tools/conll2crfsuite_1b.py BC5-CDR/conll/train.tsv BC5-CDR/conll/devel.tsv BC5-CDR/conll/test.tsv