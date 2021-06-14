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

The `phonemizer` software is used to turn an input text from its orthographic
representation into a phonetic transcription.

A wrapper on four different backends:

- Espeak [@espeakng:2019] is the default backend used by ``phonemizer`. It is a
  text-to-speech (TTS) software that supports more than a hundred languages.

- Espeak-mbrola [@mbrola:2019]

- Festival [@festival:2014] is another TTS software. It's backend in
  ``phonemizer`` is available for American English and uses a [custom
  phoneset](http://www.festvox.org/bsv/c4711.html) for transcription. This
  backend is the only one to support tokenization at the syllable level.

- Segments [@forkel:2019] is a Python package providing Unicode Standard
  tokenization routines and orthography segmentation. It's `phonemizer` backend
  relies on a grapheme to phoneme mapping to generate the phonemization. This
  backend is mostly usefull for low-resource languages, where users can use
  their own mappings. Six languages are provided as exemples with `phonemizer`:
  Chintang, Cree, Inuktitut, Japanese, Sesotho and Yucatec.


Avaibable functionalities:

- Usage as a single function `phonemizer.phonemize` or using the command-line `phonemize`.

- Customization of tokenization symbols at phone, syllable and word level. For instance

<!-- A `hello world` example in Python: -->
<!-- ```python -->
<!-- >>> from phonemizer import phonemize -->
<!-- >>> phonemize('hello world') -->
<!-- 'hhaxlow werld ' -->
<!-- ``` -->

<!-- The same from command-line interface: -->

<!-- ```bash -->
<!-- $ echo "hello world" | phonemize --backend festival -->
<!-- hhaxlow werld -->
<!-- ``` -->

# Statement of Need

Text phonemization is a preprocessing step required in different fields of
natural language processing and speech processing. The `phonemizer` is used for
word segmentation in the [wordseg toolbox](https://github.com/bootphon/wordseg)
[@bernard:2020]. It is also in use in the preprocessing pipeline of deep
learning TTS systems [@zhang:2020; @mozilla:2021; @asideas:2021].


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
