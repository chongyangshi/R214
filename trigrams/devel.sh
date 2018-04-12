#!/bin/sh

rm BC5-CDR.model
crfsuite learn -m BC5-CDR.model train_trigrams_$1.crfsuite
crfsuite tag -qt -m BC5-CDR.model devel_trigrams_$1.crfsuite
