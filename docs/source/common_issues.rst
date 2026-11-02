==============
Common Issues
==============


.. _espeak-not-installed:

espeak not installed on your system
-----------------------------------

``RuntimeError: espeak not installed on your system`` means that ``phonemizer``
cannot load the espeak shared library. This happens when espeak is not
installed, or when it is installed in a place where the library is not found
automatically (this is often the case on Windows and MacOS, or within a
virtual environment).

Give the path to the library explicitly, either from Python (before calling
:py:func:`phonemizer.phonemize`):

.. code-block:: python

    from phonemizer.backend.espeak.wrapper import EspeakWrapper

    # on Windows
    EspeakWrapper.set_library(r'C:\Program Files\eSpeak NG\libespeak-ng.dll')
    # on MacOS with brew
    EspeakWrapper.set_library('/opt/homebrew/lib/libespeak-ng.dylib')

or with the ``PHONEMIZER_ESPEAK_LIBRARY`` environment variable. For example,
within a conda environment have a:

.. code-block:: bash

   conda env config vars set PHONEMIZER_ESPEAK_LIBRARY="C:\Program Files\eSpeak NG\libespeak-ng.dll"

If the espeak data directory (containing the ``phontab`` file) is not found
either, set it with ``EspeakWrapper.set_data_path()`` or the
``PHONEMIZER_ESPEAK_DATA_PATH`` environment variable. See
:ref:`custom-installation` for details.


Phonemization is slow
---------------------

Each call to :py:func:`phonemizer.phonemize` has a cost: the phonemization
backend is cached between calls with the same parameters, but the text is
processed line by line. It is more efficient to group many lines in a single
call, which can then also be parallelized with ``njobs``:

.. code-block:: python

    from phonemizer import phonemize

    text = [line1, line2, ...]

    # Do this:
    phonemized = phonemize(text, njobs=4)

    # Not this:
    phonemized = [phonemize(line) for line in text]

An alternative is to instantiate the backend of your choice and to call its
:py:meth:`~phonemizer.backend.base.BaseBackend.phonemize` method. This method
expects a list of lines and returns a list:

.. code-block:: python

    from phonemizer.backend import EspeakBackend

    backend = EspeakBackend('en-us')
    phonemized = backend.phonemize(text)


How to disable the warnings
---------------------------

``phonemizer`` sends its messages (for instance on language switches or words
count mismatches) to the ``phonemizer`` logger of the standard :py:mod:`logging`
module. By default they are handled by the logging configuration of your
application. To hide the warnings, raise the level of that logger:

.. code-block:: python

    import logging

    logging.getLogger('phonemizer').setLevel(logging.ERROR)

You can also give your own logger to :py:func:`phonemizer.phonemize` or to a
backend with the ``logger`` argument, or use the one returned by
:py:func:`phonemizer.logger.get_logger`, which writes to the standard error
stream and does not propagate to your application:

.. code-block:: python

    from phonemizer import phonemize
    from phonemizer.logger import get_logger

    phonemize(text, logger=get_logger('quiet'))  # or 'normal', 'verbose'

From the command line, use the ``--quiet`` option.


Threads and parallel jobs
-------------------------

:py:func:`phonemizer.phonemize` can be called concurrently from several
threads: each thread uses its own backends. A backend instance (for instance
an :py:class:`~phonemizer.backend.espeak.espeak.EspeakBackend`) must not be
shared between threads, create one per thread instead.

With ``njobs > 1`` the lines of the text are phonemized in parallel processes.
The espeak library and data path chosen with ``EspeakWrapper.set_library()``
and ``EspeakWrapper.set_data_path()`` are used by those processes as well.
