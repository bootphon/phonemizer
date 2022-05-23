==============
Common Issues
==============


Phonemization is slow
---------------------

You may have realized that large number of calls to :py:meth:`phonemizer.phonemize`
makes for a very slow execution. It is much more efficient to minimize the number of calls to the phonemize function.
Indeed the initialization of the phonemization backend can be expensive, especially for espeak.
It's much more efficient to either:

- group all the calls into one using a list of strings
- "manually" instantiate your backend of choice, then call its own :py:meth:`phonemizer.backends.BaseBackend.phonemize`

.. code-block:: python

    from phonemizer import phonemize

    text = [line1, line2, ...]

    # Do this:
    phonemized = phonemize(text, ...)

    # Not this:
    phonemized = [phonemize(line, ...) for line in text]

    # An alternative is to directly instanciate the backend and to call the
    # phonemize function from it:
    from phonemizer.backend import EspeakBackend
    backend = EspeakBackend('en-us', ...)
    phonemized = [backend.phonemize(line, ...) for line in text]