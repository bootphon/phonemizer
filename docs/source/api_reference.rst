=============
API Reference
=============

Toplevel API
-------------

.. _phonemize:

.. autofunction:: phonemizer.phonemize

.. autofunction:: phonemizer.phonemize.clear_backends_cache


.. autoclass:: phonemizer.separator.Separator
    :members:

.. autoclass:: phonemizer.punctuation.Punctuation
    :members:


Backends
--------

.. autoclass:: phonemizer.backend.base.BaseBackend
    :members:


.. autoclass:: phonemizer.backend.espeak.espeak.EspeakBackend
    :members:

.. autoclass:: phonemizer.backend.espeak.mbrola.EspeakMbrolaBackend
    :members:

.. autoclass:: phonemizer.backend.segments.SegmentsBackend
    :members:

.. autoclass:: phonemizer.backend.festival.festival.FestivalBackend
    :members:


Espeak library
--------------

.. autoclass:: phonemizer.backend.espeak.wrapper.EspeakWrapper
    :members: set_library, set_data_path, library, library_path, data_path, version


Logging
-------

.. autofunction:: phonemizer.logger.default_logger

.. autofunction:: phonemizer.logger.get_logger
