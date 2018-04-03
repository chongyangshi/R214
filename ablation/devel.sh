#!/bin/sh

rm BC5-CDR.model
crfsuite learn -m BC5-CDR.model train_without_$1.crfsuite
crfsuite tag -qt -m BC5-CDR.model devel_without_$1.crfsuite
