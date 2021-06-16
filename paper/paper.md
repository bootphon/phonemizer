---
title: 'Phonemizer: Text to Phones Transcription for Multiple Languages in Python'
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

Phones are elementary sounds which compose speech, on which syllables and words
are built. The conversion of texts from their orthographic form into a phonetic
representation is an important requirement in various applications related to
speech and language processing, for instance for text to speech systems.
`Phonemizer` is a Python package addressing precisely this issue: it transcribes
a text from it's orthographic representation into a phonetic one. It supports
many languages and provides end-user functionalities such as punctuation
preservation, phones accentuation, tokenization at phone/syllable/word levels,
as well as parallel processing of large input texts. The package is
user-friendly as it exposes a single `phonemize` function, also available as a
command-line interface. The phonetic transcription is delegated to three
different backends that are wrapped in an homogoneous interface by the package.

The default backend used by `phonemizer` is Espeak [@espeak:2019], a text to
speech software built on linguistic expertise and hand written transcription
rules. It transcribes text into the International Phonetic Alphabet and supports
more than a hundred languages. Using MBROLA voices [@mbrola:2019], available for
35 languages, the espeak backend transcribes text in the SAMPA computer readable
phonetic alphabet. Festival [@festival:2014] is another text to speech software
used as a backend for ``phonemizer``. It is available for American English only,
and uses a non standard phoneset for transcription. Nevertheless this backend is
the only one to preserve syllable boundaries, which is a requirement for some
applications. The final `phonemizer` backend is Segments [@forkel:2019], a Python
package providing Unicode Standard tokenization routines and orthography
segmentation. It relies on a grapheme to phone mapping to generate the
transcription. This backend is mostly usefull for low-resource languages, for
which users with linguistic expertise can write their own mappings. Six
languages are provided as exemples with `phonemizer`: Chintang, Cree, Inuktitut,
Japanese, Sesotho and Yucatec.



# Statement of Need

Text to phones transcription is a critical need in different applications of
natural language and speech processing. So far, the `phonemizer` package is used
in the preprocessing pipeline of various deep learning text to speech systems
[@zhang:2020; @mozilla:2021; @asideas:2021]. It has also been used as a
preprocessing step in word segmentation studies regarding the role of prosody in
segmentability [@ludusan:2017] and the psychology of child development
[@cristia:2019;@bernard:2020].

* Used to build speech datasets with phonetic transcriptions, for example for
  the Zero Speech Challenges [@dunbar:2017]. Also needed for some ASR models
  (Kaldi).


# Acknowledgements

We are thankful to Alex Cristia who initiated this project and to Emmanuel
Dupoux for his support and advices. We also thank the package users for their bug
reports and features requests. This work is funded by the European Research
Council (ERC-2011-AdG-295810 BOOTPHON), the Agence Nationale pour la Recherche
(ANR-17-EURE-0017 Frontcog, ANR-10-IDEX-0001-02 PSL, ANR-19-P3IA-0001 PRAIRIE
3IA Institute) and grants from CIFAR (Learning in Machines and Brains), Facebook
AI Research (Research Grant), Google (Faculty Research Award), Microsoft
Research (Azure Credits and Grant), and Amazon Web Service (AWS Research
Credits).


# References
