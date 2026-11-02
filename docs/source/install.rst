=============
Installation
=============

Dependencies
------------

**You need python>=3.10.** If you are using an older python version, use the
``phonemizer-3.4`` release, pip selects it automatically. If you really need
to use python2, use the ``phonemizer-1.0`` release.

You need to install
`festival <http://www.festvox.org/docs/manual-2.4.0/festival_6.html#Installation>`_,
`espeak-ng <https://github.com/espeak-ng/espeak-ng#espeak-ng-text-to-speech>`_
and/or `mbrola <https://github.com/numediart/MBROLA>`_ in order to use the
corresponding ``phonemizer`` backends. The **segments** backend is a Python
package, installed with ``pip install phonemizer[segments]`` (see below).
The **espeak** backend requires espeak>=1.48 or espeak-ng (the **espeak-mbrola**
backend requires espeak-ng). Follow instructions for your system below.

On Debian/Ubuntu
~~~~~~~~~~~~~~~~

To install dependencies, simply run

.. code-block:: bash

    sudo apt-get install festival espeak-ng mbrola

When using the **espeak-mbrola** backend, additional mbrola voices must be
installed (see the `espeak-ng documentation on mbrola
<https://github.com/espeak-ng/espeak-ng/blob/master/docs/mbrola.md>`__). List
the installable voices with

.. code-block:: bash

    apt search mbrola


On CentOS/Fedora
~~~~~~~~~~~~~~~~

To install dependencies, simply run

.. code-block:: bash

    sudo yum install festival espeak-ng

When using the **espeak-mbrola** backend, the mbrola binary and additional
mbrola voices must be installed (see the `espeak-ng documentation on mbrola
<https://github.com/espeak-ng/espeak-ng/blob/master/docs/mbrola.md>`__).


On MacOS
~~~~~~~~

**espeak-ng** is available on brew:

.. code-block:: bash

    brew install espeak-ng

**festival** and **mbrola** are not packaged for MacOS (neither by brew nor
by MacPorts) and must be compiled from sources. Note that ``phonemizer`` is not
tested with them on MacOS.

* **mbrola**: follow the compilation instructions of the `MBROLA repository
  <https://github.com/numediart/MBROLA>`__, then copy the ``Bin/mbrola``
  executable to a folder in your ``PATH``. The voices are available from the
  `MBROLA-voices repository <https://github.com/numediart/MBROLA-voices>`__,
  copy them to the ``mbrola`` folder of the espeak-ng data directory (as given
  by ``espeak-ng --version``).

* **festival**: follow the `festival install guide
  <https://github.com/festvox/festival/blob/master/INSTALL>`__ (compile the
  speech tools, then festival with its English lexicons and voices), then give
  the path to the festival executable to ``phonemizer`` (see
  :ref:`custom-installation`).

The `setup-festival-mbrola <https://github.com/pettarin/setup-festival-mbrola>`__
script formerly suggested here is archived and no longer works (see `issue #203
<https://github.com/bootphon/phonemizer/issues/203>`__).

On Windows
~~~~~~~~~~

Install **espeak-ng** with the `.msi` Windows installer provided with
`espeak releases <https://github.com/espeak-ng/espeak-ng/releases>`_.

.. warning::

    On Windows the installation of espeak can cause issues (see `issue #44
    <https://github.com/bootphon/phonemizer/issues/44>`__).

    Make sure you install the correct `.msi` file for your platform. It exists
    for two architectures: X64 and X86. Most today's machines are X64 so, if you
    don't know which one to choose, you should start trying with
    ``espeak-ng-X64.msi``.

    If ``phonemizer`` fails with a message ``RuntimeError: espeak not installed
    on your system``, see :ref:`espeak-not-installed`.

**festival** must be compiled from sources (see the `festival install guide
<https://github.com/festvox/festival/blob/master/INSTALL>`__ and `this
tutorial <https://www.eguidedog.net/doc/doc_build_win_festival.php>`__).
**mbrola** is not available for Windows.


.. _custom-installation:

Custom espeak and festival installations
----------------------------------------

By default ``phonemizer`` uses the espeak library, the espeak data and the
festival program found on the system. You can choose others from Python,
before calling :py:func:`phonemizer.phonemize`:

.. code-block:: python

    from phonemizer.backend import FestivalBackend
    from phonemizer.backend.espeak.wrapper import EspeakWrapper

    EspeakWrapper.set_library('/path/to/libespeak-ng.so')
    EspeakWrapper.set_data_path('/path/to/espeak-ng-data')
    FestivalBackend.set_executable('/path/to/festival')

or with environment variables:

.. code-block:: bash

    export PHONEMIZER_ESPEAK_LIBRARY=/path/to/libespeak-ng.so
    export PHONEMIZER_ESPEAK_DATA_PATH=/path/to/espeak-ng-data
    export PHONEMIZER_FESTIVAL_EXECUTABLE=/path/to/festival

The data path is the espeak data directory, containing the ``phontab`` file
(with espeak<1.49 it must be named ``espeak-data``). The values set from Python
take precedence over the environment variables.
From the command line, use the ``--espeak-library`` and
``--festival-executable`` options.


Phonemizer
----------

* The simplest way is using pip:

  .. code-block:: bash

      pip install phonemizer

  To use the **segments** backend, install the optional dependencies with:

  .. code-block:: bash

      pip install phonemizer[segments]

* **OR** install it from sources with:

  .. code-block:: bash

      git clone https://github.com/bootphon/phonemizer
      cd phonemizer
      pip install .[segments]

  If you experience an error such as ``ImportError: No module named
  setuptools`` during installation, refer to `issue #11
  <https://github.com/bootphon/phonemizer/issues/11>`__.


Docker image
------------

Alternatively you can run the phonemizer within docker, using the
provided ``Dockerfile``. The image includes espeak-ng, festival, mbrola with
the French voice, and runs the tests at build time. To build the docker image,
have a:

.. code-block:: bash

    git clone https://github.com/bootphon/phonemizer
    cd phonemizer
    sudo docker build -t phonemizer .

Then run an interactive session with:

.. code-block:: bash

    sudo docker run -it phonemizer /bin/bash


Development
-----------

When installed from sources, you can run the tests suite from the root
``phonemizer`` folder:

.. code-block:: bash

    pip install .[test]  # this installs pytest
    pytest

To build this documentation, have a:

.. code-block:: bash

    pip install .[doc]
    make --directory=docs html

If you are a `pixi <https://pixi.sh>`_ user, the development environments are
already configured:

.. code-block:: bash

    pixi run test              # run the tests
    pixi run -e py310 test     # run the tests on python-3.10
    pixi run lint              # check the code with ruff
