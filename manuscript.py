#!/usr/bin/env python3
#deps: docopt pathlib
"""Manuscript. Manage your scripts and their dependencies.

Just add a line of the form "#deps: requests docopt pathlib" to your script,
and manuscript will install them in a virtualenv and create a wrapper.

Usage:
  manuscript install SCRIPT [-i INTERPRETER -c]
  manuscript check-deps

Options:
  -i INTERPRETER  Specify the interpreter to use, otherwise,
                  it's guessed from the script's shebang.
  -c              Copy the script so the original can be deleted
"""
import os
import subprocess
import shutil
from pathlib import Path
from docopt import docopt

MANUSCRIPT_DIR = Path(os.path.expanduser('~'), '.manuscript')
ENVS_DIR = MANUSCRIPT_DIR['envs']
BIN_DIR = MANUSCRIPT_DIR['bin']
COPIES_DIR = MANUSCRIPT_DIR['script_copies']


def initialize():
    """Checks that everything that should exist exists"""
    subprocess.check_output(['virtualenv', '--version'])
    for path in (MANUSCRIPT_DIR, ENVS_DIR, BIN_DIR, COPIES_DIR):
        if not path.exists():
            path.mkdir()


class Env:
    """One of the virtualenv manipulated by manuscript"""

    def __init__(self, name, python='python'):
        """Creates a virtualenv with the given name using the given python
        interpreter.
        The ability to manipulate names is not yet given in the cli."""
        self.name = name
        self.dir = ENVS_DIR[name]
        self.python = python

        if not self.dir.exists():
            subprocess.check_call(['virtualenv', '-p', self.python,
                                   str(self.dir)])

    def bin_path(self, bin):
        """Returns the path to a bin in the env"""
        return self.dir['bin'][bin]

    def install(self, pkgs):
        """Install the given packages in the env"""
        if pkgs:
            subprocess.check_call([str(self.bin_path('pip')), 'install']
                                  + pkgs)


SCRIPT_TEMPLATE = """#!/bin/sh
INTERPRETER={}
FILE={}
$INTERPRETER $FILE $*
"""


class Script:
    """One of the scripts manipulated by manuscript"""

    def __init__(self, script, env=None, interpreter=None, copy=False):
        """Creates a script attached to the given environment.  If none is
        given, choose one for the given interpreter, or try to guess it from
        the script shebang."""

        self.path = Path(script).resolve()
        self.name = self.path.name

        if copy:
            shutil.copy(str(self.path), str(COPIES_DIR))
            print('Copied {} to {}'.format(self.path, COPIES_DIR))
            self.path = COPIES_DIR[self.name]

        if self.name.endswith('.py'):
            self.name = self.name[:-3]

        if env:
            self.env = env
            if interpreter:
                print('Interpreter {} ignored for script {} because an'
                      ' env was given'.format(interpreter, script))
        else:
            interpreter = (interpreter or self.interpreter_from_shebang()
                           or 'python')
            self.env = Env(interpreter, interpreter)

    def interpreter_from_shebang(self):
        """Tries to guess the interpreter to use from the shebang of the
        script. Returns None if none is found."""
        with self.path.open() as f:
            line = next(f)
            if line.startswith('#!'):
                if 'env' in line:
                    return line.strip().split('env ')[1]
                else:
                    return line.strip().split('/')[-1]
        return None

    def dependencies(self):
        """Looks for dependencies of the form "#deps: ..." in the script"""
        with self.path.open() as f:
            for line in f:
                if line.startswith('#deps:'):
                    line = line.replace('#deps:', '').strip()
                    return line.split(' ')
        return []

    def install_deps(self):
        """Install the dependencies of the script"""
        self.env.install(self.dependencies())

    def save(self):
        """Save the script in manuscript's bin dir"""
        self.install_deps()
        with BIN_DIR[self.name].open('w') as f:
            f.write(SCRIPT_TEMPLATE.format(self.env.bin_path('python'),
                                           repr(str(self.path))))
        subprocess.check_call(['chmod', '+x', str(BIN_DIR[self.name])])
        print('Created {}'.format(BIN_DIR[self.name]))


def all_scripts():
    """Return all the scripts handled by manuscript"""
    for script in BIN_DIR:
        with script.open() as f:
            next(f)  # The sh shebang
            env = Env(next(f).split('/')[-3])
            script = next(f).split("'")[-2]
            yield Script(script, env)


def main():
    args = docopt(__doc__)
    initialize()
    if args['install']:
        script = Script(args['SCRIPT'], interpreter=args['-i'],
                        copy=args['-c'])
        script.save()
    elif args['check-deps']:
        for script in all_scripts():
            script.install_deps()


if __name__ == '__main__':
    main()
