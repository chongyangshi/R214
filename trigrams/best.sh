#!/bin/sh

rm BC5-CDR.model
crfsuite learn --algorithm=lbfgs --set=c2=0.25 -m BC5-CDR.model train_trigrams_3.crfsuite
crfsuite tag -qt -m BC5-CDR.model test_trigrams_3.crfsuite
