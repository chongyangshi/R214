#!/bin/sh

rm BC5-CDR.model
crfsuite learn --algorithm=lbfgs --set=$1=$2 --set=$3=$4 -m BC5-CDR.model train_trigrams_3.crfsuite
crfsuite tag -qt -m BC5-CDR.model devel_trigrams_3.crfsuite
