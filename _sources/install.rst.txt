=============
Installation
=============

Dependencies
------------

**You need python>=3.6.** If you really need to use python2, use the
``phonemizer-1.0`` release.

You need to install
`festival <http://www.festvox.org/docs/manual-2.4.0/festival_6.html#Installation>`_,
`espeak-ng <https://github.com/espeak-ng/espeak-ng#espeak-ng-text-to-speech>`_
and/or `mbrola <https://github.com/numediart/MBROLA>`_ in order to use the
corresponding ``phonemizer`` backends.
Follow instructions for your system below.

On Debian/Unbuntu
~~~~~~~~~~~~~~~~~

To install dependencies, simply run

.. code-block:: bash

    sudo apt-get install festival espeak-ng mbrola

When using the **espeak-mbrola** backend, additional mbrola voices must be
installed (see
`here <https://github.com/espeak-ng/espeak-ng/blob/master/docs/mbrola.md)>`_. List
the installable voices with

.. code-block:: bash

    apt search mbrola



On CentOS/Fedora
~~~~~~~~~~~~~~~~

To install dependencies, simply run

.. code-block:: bash

    sudo yum install festival espeak-ng

When using the **espeak-mbrola** backend, the mbrola binary and additional
mbrola voices must be installed (see
`here <https://github.com/espeak-ng/espeak-ng/blob/master/docs/mbrola.md)>`_).


On MacOS
~~~~~~~~~

**espeak** is available on brew at version 1.48: ``brew install espeak``. If you
want a more recent version you have to `compile it from sources
<https://github.com/espeak-ng/espeak-ng/blob/master/docs/building.md#linux-mac-bsd>`_.
To install **festival**, **mbrola** and additional mbrola voices, use the script
provided `here <https://github.com/pettarin/setup-festival-mbrola>`_.

On Windows
~~~~~~~~~~

Install **espeak-ng** with the `.msi` Windows installer provided with
`espeak releases <https://github.com/espeak-ng/espeak-ng/releases>`_.

.. warning::

    On Windows the installation of espeak can cause issues (see `here
    <https://github.com/bootphon/phonemizer/issues/44>`_).

    Make sure you install the correct `.msi` file for your platform. It exists
    for two architectures: X64 and X86. Most today's machines are X64 so, if you
    don't know which one to choose, you should start trying with
    ``espeak-ng-X64.msi``.

    If ``phonemizer`` fails with a message ``RuntimeError: espeak not installed
    on your system``, it means the ``libespeak-ng.dll`` library file is not
    found by ``phonemizer``. You can specify it's path from Python (before
    calling the phonemize function):

    .. code-block:: python

        from phonemizer.backend.espeak.wrapper import EspeakWrapper

        EspeakWrapper.set_library('C:\Program Files\eSpeak NG\libespeak-ng.dll')

    An alternative is to define the environment variable
    ``PHONEMIZER_ESPEAK_LIBRARY`` to the absolute path to the DLL. For example
    if using conda have a:

    .. code-block:: bash

       conda env config vars set PHONEMIZER_ESPEAK_LIBRARY="C:\Program Files\eSpeak NG\libespeak-ng.dll"

**festival** must be compiled from sources (see
`here <https://github.com/festvox/festival/blob/master/INSTALL>`_ and
`here <https://www.eguidedog.net/doc/doc_build_win_festival.php)>`_.
**mbrola** is not available for Windows.


Phonemizer
----------

* The simplest way is using pip:

    .. code-block:: bash

        pip install phonemizer

* **OR** install it from sources with:

    .. code-block:: bash

        git clone https://github.com/bootphon/phonemizer
        cd phonemizer
        pip install .
        # to run tests or build this documentation, have a
        # pip install .[test,doc]

    If you experiment an error such as ``ImportError: No module named setuptools``
    during installation, refer to `issue #11 <https://github.com/bootphon/phonemizer/issues/11>`_.


Docker image
------------

Alternatively you can run the phonemizer within docker, using the
provided ``Dockerfile``. To build the docker image, have a:

.. code-block:: bash

    git clone https://github.com/bootphon/phonemizer
    cd phonemizer
    sudo docker build -t phonemizer .

Then run an interactive session with:

.. code-block:: bash

    sudo docker run -it phonemizer /bin/bash


Testing
-------

When installed from sources or whithin a Docker image, you can run the tests
suite from the root ``phonemizer`` folder (once you installed ``pytest``):

.. code-block:: bash

    pip install .[test]  # this installs pytest
    pytest
