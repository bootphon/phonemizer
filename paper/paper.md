---
title: 'Phonemizer: text to phones conversion for multiple languages in Python'
tags:
  - Python
  - linguistics
  - natural language processing
  - speech processing
authors:
  - name: Mathieu Bernard
    orcid: 0000-0001-7586-7133
    affiliation: 1
affiliations:
  - name: LSCP/ENS/CNRS/EHESS/Inria/PSL Research University, Paris, France
    index: 1
date: 11 June 2021
bibliography: paper.bib
---


# Summary

The `phonemizer` software is used to turn an input text into phonetic alphabet.
A wrapper on four different backends:

- espeak
- espeak-mbrola
- Festival [@festival:2014]
- Segments [@forkel:2019]


# Statement of Need

Text phonemization is a preprocessing step required in different fields of
natural language processing and speech processing. The `phonemizer` is used for
word segmentation in the [wordseg toolbox](https://github.com/bootphon/wordseg)
[@bernard:2020]. It is also in use in the preprocessing pipeline of deep
learning text-to-speech systems [@zhang:2020; @mozilla:2021; @asideas:2021].


# Acknowledgements

We are thankful to Alex Cristia who initiated this project and to Emmanuel
Dupoux for his support and advices. This work is funded by the European Research
Council (ERC-2011-AdG-295810 BOOTPHON), the Agence Nationale pour la Recherche
(ANR-17-EURE-0017 Frontcog, ANR-10-IDEX-0001-02 PSL, ANR-19-P3IA-0001 PRAIRIE
3IA Institute) and grants from CIFAR (Learning in Machines and Brains), Facebook
AI Research (Research Grant), Google (Faculty Research Award), Microsoft
Research (Azure Credits and Grant), and Amazon Web Service (AWS Research
Credits).


# References
