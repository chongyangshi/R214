# Resources for BMIP 2018 practical

Contents of this repository:

- `BC5-CDR/`          :  BioCreative V Chemical-Disease Relation (CDR) Task Corpus
- `BC5-CDR/original/` :   Data in original corpus format
- `BC5-CDR/conll/`    :   Data in CoNLL format
- `tools/`                 :   Scripts for working with the data

Conversion from original to basic CoNLL format available from
https://github.com/spyysalo/ncbi-disease . Extra columns added using
NERsuite (http://nersuite.nlplab.org/).

In this coursework project, data taken from the BioCreative V Chemical-Disease Relation dataset was used to train a Conditional Random Field (CRM) entity recognition model, which was then paired with an approximate string matching-based grounding system to extract relations between mentions of chemicals and diseases in biomedical literature. 

The codebase operates on Python 2.7, and was based on the framework supplied by the assessment setters. The hard-forked repository can be found [here](https://github.com/cambridgeltl/bmip-2018/).

In the unlikely case that you wish to make use of this repository, with the exception of academic prohibitions in using the codebase for assessments, I disclaim copyright to my proportion of the codebase. The original conll2crfsuite and crfutils tools belong to their original setters, who may have stricter constraints on how derivations of their work can be used.
