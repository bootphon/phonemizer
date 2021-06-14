---
title: 'Phonemizer: Text to Phones Conversion for Multiple Languages in Python'
tags:
  - Python
  - linguistics
  - natural language processing
  - text-to-speech
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

Phones are elementary components of speech, on which syllables and words are
built. The conversion of texts in orthographic form to a phonetic representation
is an important preprocessing step in various applications related to speech and
language processing. `Phonemizer` is a Python package addressing precisely this
issue: it converts a text from it's orthographic representation to a phonetic
one. The package consists in a single `phonemize` function, also available as a
command-line interface, wrapping three backends in an homogoneous interface. It
supports many languages and, in top of those backends, it provides end-user
functionalities such as punctuation preservation, phones accentuation,
customization of phones, syllables and words separators, as well as parallel
processing.

Espeak [@espeak:2019] is the default backend. It is a text to speech software
built on linguistic expertise and hand written transcription rules. It supports
more than a hundred languages, transcribe phones in the International Phonetic
Alphabet and preserves both phones and word boundaries. Using MBROLA voices
[@mbrola:2019], available for 35 languages, the espeak backend outputs phones in
the SAMPA computer readable phonetic alphabet while losoing word boundaries.
Festival [@festival:2014] is another text to speech software. It's backend in
``phonemizer`` is available for American English and uses a non standard
phoneset for transcription. This backend is the only one to preserve syllable
boundaries. Segments [@forkel:2019] is a Python package providing Unicode
Standard tokenization routines and orthography segmentation. It's `phonemizer`
backend relies on a grapheme to phoneme mapping to generate the phonemization.
This backend is mostly usefull for low-resource languages, for which users with
linguistic expertise can write their own mappings. Six languages are provided as
exemples with `phonemizer`: Chintang, Cree, Inuktitut, Japanese, Sesotho and
Yucatec.



# Statement of Need

Text phonemization is a preprocessing step required in different fields of
natural language processing and speech processing.

* Used in the preprocessing pipeline of various deep learning tst to speech
systems [@zhang:2020; @mozilla:2021; @asideas:2021].

* Used as a preprocessing step in word segmentation studies regarding child
  development [@cristia:2019;@bernard:2020].

* Used to build speech datasets with phonetic transcriptions, for example for
  the Zero Speech Challenges [@dunbar:2017]. Also needed for some ASR models
  (Kaldi).


# Acknowledgements

We are thankful to Alex Cristia who initiated this project and to Emmanuel
Dupoux for his support and advices. We also tha the package users for their bug
reports and features requests. This work is funded by the European Research
Council (ERC-2011-AdG-295810 BOOTPHON), the Agence Nationale pour la Recherche
(ANR-17-EURE-0017 Frontcog, ANR-10-IDEX-0001-02 PSL, ANR-19-P3IA-0001 PRAIRIE
3IA Institute) and grants from CIFAR (Learning in Machines and Brains), Facebook
AI Research (Research Grant), Google (Faculty Research Award), Microsoft
Research (Azure Credits and Grant), and Amazon Web Service (AWS Research
Credits).


# References
