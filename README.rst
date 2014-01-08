===============================
Manuscript
===============================

.. image:: https://badge.fury.io/py/manuscript.png
    :target: http://badge.fury.io/py/manuscript
    
.. image:: https://pypip.in/d/manuscript/badge.png
        :target: https://crate.io/packages/manuscript?version=latest


Manuscript helps you manage your python scripts and their dependencies

Python still is a scripting language, and it is awesome for
this. Moreover, we now have some great libraries that make writing
scripts even easier, like requests, docopt or pathlib. However, having
to install them system-wide, or start worrying about virtualenv for
just one script is annoying. Manuscript is here to help you handle that.

Just add a line of the form ``#deps: requests docopt pathlib`` to your script,
and manuscript will install them in a virtualenv and create a wrapper for you.

Install
-------

You can get it on `pypi`_ with the usual ``pip install manuscript``.

You can also install manuscript using manuscript! For this, use this line get manuscript and its dependencies, and use manuscript to install itself::

    cd /tmp && wget https://bitbucket.org/pitrou/pathlib/raw/b393963cdf9dd02b13fe5ac53709f4d4bc48363a/pathlib.py https://raw.github.com/docopt/docopt/0.6.1/docopt.py https://raw.github.com/madjar/manuscript/master/manuscript.py && python3 manuscript.py install -c manuscript.py

Once it's done, I recommend you add ``~/.manuscript/bin/`` to your path, to make it easier to access installed scripts.

.. _`pypi`: https://pypi.python.org/pypi/manuscript

Usage
-----

You just wrote ``some_awesome_script.py`` that uses ``requests`` and ``docopt``, and you want to use it on your system without worrying about the dependencies. Just add this line somewhere in your script::

  #deps requests docopt

Then run manuscript::

  manuscript install some_awesome_script.py

This will install all the dependencies in a virtualenv and create a wrapper around the script as ``~/.manuscript/bin/some_awesome_script``.

The virtualenv will use the interpreter mentioned in the script's shebang, falling back to ``python`` if none is found. You can force an interpreter with the ``-i`` option, like so::

  manuscript install some_awesome_script.py -i pypy

If you don't want a script to share the default virtualenv with other scripts, you can specify a virtualenv name in which to install the script (it will be created if needed)::

  manuscript install some_awesome_script.py -e awesome-venv

If you edit you script to add more dependencies, just run::

  manuscript check-deps

This will install all missing dependencies for all the scripts.


Finally, if you want to use manuscript on a script that won't last (something downloaded from the internet that sits on your ``/tmp`` for example), just add the `-c` argument: manuscript will first copy the script to a safe place, then do the whole dance.

Contribute
----------

The source code is available on `github`_.

Bug reports and pull requests welcomed !

.. _`github`: https://github.com/madjar/manuscript

Author
------

This project is made by Georges Dubus <georges.dubus@gmail.com>.
You can find me on twitter: `@georgesdubus`_.

.. _`@georgesdubus`: https://twitter.com/georgesdubus
