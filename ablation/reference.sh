#!/bin/sh

rm BC5-CDR.model
crfsuite learn -m BC5-CDR.model train_without_.crfsuite
crfsuite tag -qt -m BC5-CDR.model test_without_.crfsuite
