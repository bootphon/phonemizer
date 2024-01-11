.. _python-examples:

===============
Python Examples
===============

In Python import the ``phonemize`` function with ``from phonemizer import phonemize``.
See :py:meth:`phonemizer.phonemize`.


Example 1: phonemize a text with festival
-----------------------------------------

The following example downloads a text and phonemizes it using the
festival backend, preserving punctuation and using 4 jobs in parallel.
The phones are not separated, words are separated by a space and
syllables by ``|``.

.. code:: python

   # need to pip install requests
   import requests
   from phonemizer import phonemize
   from phonemizer.separator import Separator

   # text is a list of 190 English sentences downloaded from github
   url = (
       'https://gist.githubusercontent.com/CorentinJ/'
       '0bc27814d93510ae8b6fe4516dc6981d/raw/'
       'bb6e852b05f5bc918a9a3cb439afe7e2de570312/small_corpus.txt')
   text = requests.get(url).content.decode()
   text = [line.strip() for line in text.split('\n') if line]

   # phn is a list of 190 phonemized sentences
   phn = phonemize(
       text,
       language='en-us',
       backend='festival',
       separator=Separator(phone=None, word=' ', syllable='|'),
       strip=True,
       preserve_punctuation=True,
       njobs=4)


Example 2: build a lexicon with espeak
--------------------------------------

The following example extracts a list of words present in a text,
ignoring punctuation, and builds a dictionary ``word: [phones]``,
e.g. ``{'students': 's t uː d ə n t s', 'cobb': 'k ɑː b', 'its': 'ɪ t s', 'put': 'p ʊ t', ...}``.
We consider here the same text as in the previous example.

.. code:: python

   from phonemizer.backend import EspeakBackend
   from phonemizer.punctuation import Punctuation
   from phonemizer.separator import Separator

   # remove all the punctuation from the text, considering only the specified
   # punctuation marks
   text = Punctuation(';:,.!"?()-').remove(text)

   # build the set of all the words in the text
   words = {w.lower() for line in text for w in line.strip().split(' ') if w}

   # initialize the espeak backend for English
   backend = EspeakBackend('en-us')

   # separate phones by a space and ignoring words boundaries
   separator = Separator(phone=' ', word=None)

   # build the lexicon by phonemizing each word one by one. The backend.phonemize
   # function expect a list as input and outputs a list.
   lexicon = {
       word: backend.phonemize([word], separator=separator, strip=True)[0]
       for word in words}